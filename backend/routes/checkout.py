from flask import Blueprint, request, jsonify
from models.db_models import db, User, Transaction
from services.syncpay_service import syncpay_service
from utils.auth_utils import token_required
import os
from datetime import datetime, timedelta

checkout_bp = Blueprint('checkout', __name__)

# Preços fixos definidos no PDR v1.1.0
PRICES = {
    "100": {"credits": 100, "price": 25.00, "description": "100 créditos no AureaIA"},
    "250": {"credits": 250, "price": 50.00, "description": "250 créditos no AureaIA"},
    "500": {"credits": 500, "price": 120.00, "description": "500 créditos no AureaIA"}
}

@checkout_bp.route('/create-session', methods=['POST'])
@token_required
def create_session(current_user):
    print(f"DEBUG: create_session call for user {current_user.email}")
    data = request.get_json()
    package_id = str(data.get('package_id'))
    print(f"DEBUG: package_id: {package_id}")
    
    if package_id not in PRICES:
        print(f"DEBUG: Invalid package_id: {package_id}")
        return jsonify({"error": "Pacote inválido"}), 400
    
    package = PRICES[package_id]
    
    try:
        # 1. Cria uma transação pendente no banco
        new_transaction = Transaction(
            user_id=current_user.id,
            type='purchase',
            amount=package['credits'],
            balance_before=current_user.credits_balance,
            balance_after=current_user.credits_balance, # Não muda ainda
            description=package['description'],
            status='pending',
            paid_amount=package['price']
        )
        
        db.session.add(new_transaction)
        db.session.commit() # Commit para gerar o ID da transação
        print(f"DEBUG: Transaction created: {new_transaction.id}")
        
        # 2. Prepara dados do cliente para a SyncPay
        client_data = {
            "name": current_user.name,
            "email": current_user.email,
            "phone": current_user.phone or "51999999999",
            "cpf": current_user.cpf or "" # Placeholder ou vazio
        }
        
        # 3. Chama o serviço da SyncPay
        pix_charge = syncpay_service.create_pix_charge(
            amount=package['price'],
            external_reference=new_transaction.id,
            description=package['description'],
            client_data=client_data
        )
        
        if not pix_charge:
            print("DEBUG: SyncPay charge creation failed")
            # Se falhar, marcamos como falha
            new_transaction.status = 'failed'
            db.session.commit()
            return jsonify({
                "success": False,
                "error": "O gateway SyncPay não pôde processar a cobrança. Verifique as credenciais ou tente novamente."
            }), 500
        
        # Atualiza a transação com o ID da SyncPay (identifier)
        new_transaction.external_id = pix_charge['transaction_id']
        db.session.commit()
        print(f"DEBUG: Transaction updated with external_id: {new_transaction.external_id}")
        
        return jsonify({
            "transaction_id": new_transaction.id,
            "pix_code": pix_charge['pix_code'],
            "identifier_syncpay": pix_charge['transaction_id'],
            "status": "pending"
        }), 201
    except Exception as e:
        print(f"ERROR in create_session: {str(e)}")
        db.session.rollback()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@checkout_bp.route('/status/<transaction_id>', methods=['GET'])
@token_required
def get_status(current_user, transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    
    if not transaction:
        return jsonify({"error": "Transação não encontrada"}), 404
    
    return jsonify({
        "status": transaction.status,
        "amount": transaction.amount,
        "paid_amount": transaction.paid_amount
    }), 200

def webhook_syncpay():
    # De acordo com o PDR: Valida o header de assinatura se existir. Se não, ao menos verifique o identifier.
    data = request.get_json()
    
    # Log para debug
    print(f"Webhook SyncPay recebido: {data}")
    
    event = data.get('event')
    # A SyncPay envia o identifier (ID da transação na SyncPay)
    identifier = data.get('identifier') or data.get('id')
    
    if event == 'payment.confirmed' and identifier:
        # Localiza a transação pelo identifier_syncpay (external_id)
        transaction = Transaction.query.filter_by(external_id=identifier, status='pending').first()
        
        if transaction:
            user = User.query.get(transaction.user_id)
            if user:
                # Atualiza saldo
                transaction.balance_before = user.credits_balance
                user.credits_balance += transaction.amount
                transaction.balance_after = user.credits_balance
                transaction.status = 'completed'
                
                db.session.commit()
                print(f"Pagamento confirmado para usuário {user.email}. {transaction.amount} créditos adicionados.")
                return jsonify({"status": "success"}), 200
            else:
                print(f"Usuário não encontrado para transação {identifier}")
        else:
            print(f"Transação não encontrada ou já processada: {identifier}")
            
    return jsonify({"status": "ignored"}), 200
