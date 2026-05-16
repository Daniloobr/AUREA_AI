from flask import Blueprint, request, jsonify, current_app
from models.db_models import db, User, Transaction
from services.pagseguro_service import pagseguro_service
from utils.auth_utils import token_required
import logging

logger = logging.getLogger(__name__)
pagseguro_bp = Blueprint('pagseguro', __name__)

# Mapeamento de IDs de pacote para créditos
PACKAGE_TO_CREDITS = {
    "100_credits": 100,
    "200_credits": 200,
    "400_credits": 400,
    # Fallback se vier apenas o número
    "100": 100,
    "200": 200,
    "400": 400
}

@pagseguro_bp.route('/create-pix-payment', methods=['POST'])
@token_required
def create_pix_payment(current_user):
    data = request.get_json()
    
    amount = data.get('amount') # Centavos
    customer_name = data.get('customer_name')
    customer_email = data.get('customer_email')
    customer_tax_id = data.get('customer_tax_id') # CPF
    package_id = data.get('package_id')
    
    if not all([amount, customer_name, customer_email, customer_tax_id, package_id]):
        return jsonify({"success": False, "error": "Dados incompletos"}), 400

    # Referência única: user_id:package_id:timestamp
    import time
    reference_id = f"{current_user.id}:{package_id}:{int(time.time())}"
    
    result = pagseguro_service.create_pix_order(
        amount_cents=amount,
        customer_name=customer_name,
        customer_email=customer_email,
        customer_tax_id=customer_tax_id,
        reference_id=reference_id
    )
    
    if not result:
        return jsonify({"success": False, "error": "Falha ao gerar PIX no PagSeguro"}), 500

    # Registrar a transação como pendente
    try:
        new_tx = Transaction(
            user_id=current_user.id,
            type='purchase',
            amount=PACKAGE_TO_CREDITS.get(package_id, 0),
            balance_before=current_user.credits_balance,
            balance_after=current_user.credits_balance, # Ainda não mudou
            description=f"Compra de créditos via PIX (PagSeguro)",
            status='pending',
            pagseguro_order_id=result['order_id'],
            external_id=result['order_id'] # Compatibilidade
        )
        db.session.add(new_tx)
        db.session.commit()
    except Exception as e:
        logger.error(f"Erro ao registrar transação pendente: {str(e)}")
        # Continuamos mesmo se o log da transação falhar, para não barrar o usuário de pagar

    return jsonify({
        "success": True,
        "qr_code_text": result['qr_code_text'],
        "qr_code_image": result['qr_code_image'],
        "order_id": result['order_id']
    })

@pagseguro_bp.route('/webhooks/pagseguro', methods=['POST'])
def pagseguro_webhook():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data"}), 200 # PagSeguro espera 200

    # Verificamos se é uma notificação de PEDIDO PAGO
    # Estrutura PagSeguro v2: a notificação envia o objeto order completo
    # com status e charges.
    
    order_id = data.get('id')
    reference_id = data.get('reference_id')
    charges = data.get('charges', [])
    
    # No PagSeguro v2 PIX, o status do pedido fica PAID quando o charge está PAID
    is_paid = False
    charge_id = None
    
    for charge in charges:
        if charge.get('status') == 'PAID':
            is_paid = True
            charge_id = charge.get('id')
            break

    if is_paid and reference_id:
        try:
            # Extrair user_id e package_id da referência
            parts = reference_id.split(':')
            if len(parts) < 2:
                logger.error(f"Referência inválida no webhook: {reference_id}")
                return jsonify({"status": "error"}), 200
            
            user_id = parts[0]
            package_id = parts[1]
            
            user = User.query.get(user_id)
            if not user:
                logger.error(f"Usuário {user_id} não encontrado no webhook")
                return jsonify({"status": "user_not_found"}), 200

            # Verificar se já processamos esta transação (idempotência)
            existing_tx = Transaction.query.filter_by(pagseguro_order_id=order_id, status='completed').first()
            if existing_tx:
                return jsonify({"status": "already_processed"}), 200

            credits_to_add = PACKAGE_TO_CREDITS.get(package_id, 0)
            
            # Atualizar saldo
            old_balance = user.credits_balance
            user.credits_balance += credits_to_add
            
            # Atualizar ou criar transação
            pending_tx = Transaction.query.filter_by(pagseguro_order_id=order_id, status='pending').first()
            if pending_tx:
                pending_tx.status = 'completed'
                pending_tx.balance_after = user.credits_balance
                pending_tx.pagseguro_charge_id = charge_id
                pending_tx.paid_amount = charges[0].get('amount', {}).get('value', 0) / 100.0
            else:
                new_tx = Transaction(
                    user_id=user.id,
                    type='purchase',
                    amount=credits_to_add,
                    balance_before=old_balance,
                    balance_after=user.credits_balance,
                    description=f"Compra de {credits_to_add} moedas via PIX",
                    status='completed',
                    pagseguro_order_id=order_id,
                    pagseguro_charge_id=charge_id,
                    external_id=order_id,
                    paid_amount=charges[0].get('amount', {}).get('value', 0) / 100.0
                )
                db.session.add(new_tx)
            
            db.session.commit()
            logger.info(f"PIX Pago com sucesso! {credits_to_add} créditos adicionados ao usuário {user.email}")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao processar webhook PagSeguro: {str(e)}")
            return jsonify({"status": "internal_error"}), 200

    return jsonify({"status": "ok"}), 200

@pagseguro_bp.route('/pagseguro/status/<order_id>', methods=['GET'])
@token_required
def check_order_status(current_user, order_id):
    # Primeiro verifica no nosso banco
    tx = Transaction.query.filter_by(pagseguro_order_id=order_id, user_id=current_user.id).first()
    
    if tx and tx.status == 'completed':
        return jsonify({"success": True, "status": "PAID", "credits_added": tx.amount})

    # Se não estiver completo no banco, consulta a API do PagSeguro (Double check)
    result = pagseguro_service.get_order(order_id)
    if not result:
        return jsonify({"success": False, "error": "Pedido não encontrado"}), 404

    # Verifica status nas cobranças
    is_paid = False
    charges = result.get('charges', [])
    for charge in charges:
        if charge.get('status') == 'PAID':
            is_paid = True
            break
    
    if is_paid:
        # Caso o webhook tenha falhado mas a API diga que está pago
        # O ideal seria processar aqui também para garantir, mas o webhook é o principal.
        return jsonify({"success": True, "status": "PAID"})
    
    return jsonify({"success": True, "status": "PENDING"})
