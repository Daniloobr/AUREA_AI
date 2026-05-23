from flask import Blueprint, request, jsonify
from services.syncpay_service import syncpay_service
from utils.auth_utils import token_required
import os

payments_bp = Blueprint('payments', __name__)

# Mapeamento dos pacotes (ajuste conforme seus valores reais)
PACKAGES = {
    '100_credits': {'amount': 25.00, 'credits': 100},
    '200_credits': {'amount': 50.00, 'credits': 200},
    '400_credits': {'amount': 120.00, 'credits': 400}
}

@payments_bp.route('/create-pix-payment', methods=['POST'])
@token_required
def create_pix_payment(current_user):
    data = request.get_json()
    package_id = data.get('package_id')
    client_cpf = data.get('cpf')
    client_phone = data.get('phone')
    client_name = data.get('name', current_user.name or "Cliente")

    if not package_id or package_id not in PACKAGES:
        return jsonify({'success': False, 'error': 'Pacote inválido'}), 400
    if not client_cpf or not client_phone:
        return jsonify({'success': False, 'error': 'CPF e telefone são obrigatórios'}), 400

    package = PACKAGES[package_id]
    description = f"user_{current_user.id}"   # identificador único do usuário

    webhook_url = f"{os.environ.get('BASE_URL', 'http://localhost:5000')}/api/webhooks/syncpay"

    try:
        result = syncpay_service.create_cash_in(
            amount=package['amount'],
            client_name=client_name,
            client_cpf=client_cpf,
            client_email=current_user.email,
            client_phone=client_phone,
            description=description,
            webhook_url=webhook_url
        )
        return jsonify({
            'success': True,
            'qr_code': result['pix_code'],
            'identifier': result['identifier']
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

