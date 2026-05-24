import os
import uuid
import stripe
from flask import Blueprint, request, jsonify, current_app
from models.db_models import db, User, Transaction

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    # Garante que a chave da API está configurada (já deve estar no ambiente)
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

    # 1. Obtém payload em BYTES (obrigatório para assinatura)
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

    current_app.logger.info("[STRIPE] Evento recebido")

    if not sig_header:
        current_app.logger.error("[STRIPE] Header Stripe-Signature ausente")
        return jsonify({"error": "Missing Stripe-Signature"}), 400

    if not webhook_secret:
        current_app.logger.error("[STRIPE] STRIPE_WEBHOOK_SECRET não configurado")
        return jsonify({"error": "Webhook secret not configured"}), 500

    # 2. Verifica assinatura
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except stripe.error.SignatureVerificationError as e:
        current_app.logger.error(f"[STRIPE] Assinatura inválida: {e}")
        return jsonify({"error": "Invalid signature"}), 400
    except Exception as e:
        current_app.logger.error(f"[STRIPE] Falha ao construir evento: {e}")
        return jsonify({"error": f"Webhook error: {e}"}), 400

    # 3. Processa apenas checkout.session.completed
    if event["type"] != "checkout.session.completed":
        current_app.logger.info(f"[STRIPE] Evento ignorado: {event['type']}")
        return jsonify({"status": "ignored"}), 200

    session = event["data"]["object"]
    session_id = session.id
    payment_status = session.payment_status
    metadata = dict(session.metadata) if session.metadata else {}

    user_id = metadata.get("user_id") or session.client_reference_id
    price_id = metadata.get("price_id")

    current_app.logger.info(
        f"[STRIPE] session={session_id} | user={user_id} | price={price_id} | status={payment_status}"
    )

    # 4. Idempotência
    if session_id and Transaction.query.filter_by(external_id=session_id).first():
        current_app.logger.warning(f"[STRIPE] Já processado: {session_id}")
        return jsonify({"status": "already_processed"}), 200

    # 5. Só processa se pago
    if payment_status != "paid":
        current_app.logger.info(f"[STRIPE] Pagamento não concluído: {payment_status}")
        return jsonify({"status": "ignored", "reason": "not_paid"}), 200

    if not user_id:
        current_app.logger.error("[STRIPE] user_id ausente")
        return jsonify({"status": "ignored", "reason": "user_id_missing"}), 200

    # 6. Fallback para price_id via line_items
    if not price_id:
        try:
            line_items = stripe.checkout.Session.list_line_items(session.id, limit=1)
            if line_items and line_items.data:
                price_id = line_items.data[0].price.id
                current_app.logger.info(f"[STRIPE] price_id obtido via line_items: {price_id}")
        except Exception as e:
            current_app.logger.error(f"[STRIPE] Erro ao buscar line_items: {e}")

    if not price_id:
        current_app.logger.error("[STRIPE] price_id ausente")
        return jsonify({"status": "ignored", "reason": "price_id_missing"}), 200

    # 7. Mapeamento price_id → créditos (inclui IDs de teste e live)
    credits_map = {
        # Live
        "price_1TXBt5AXb2fn2YJDXDIF0iKk": 100,
        "price_1TXBtWAXb2fn2YJDZxm1s4Xz": 200,
        "price_1TXBtrAXb2fn2YJDNsCz53jj": 400,
        # Teste (substitua pelo seu price_id de teste real)
        "price_1TaSlbAXb2fn2YJD21xOhXPs": 100,
    }
    credits = credits_map.get(price_id)
    if not credits:
        current_app.logger.error(f"[STRIPE] price_id não mapeado: {price_id}")
        return jsonify({"status": "ignored", "reason": "price_id_not_mapped"}), 200

    # 8. Busca usuário com fallback para UUID/int
    user = None
    try:
        user = User.query.get(user_id)
        if not user:
            try:
                user = User.query.get(uuid.UUID(user_id))
            except (ValueError, AttributeError):
                pass
        if not user:
            try:
                user = User.query.get(int(user_id))
            except (ValueError, TypeError):
                pass
    except Exception as e:
        current_app.logger.error(f"[STRIPE] Erro na busca do usuário: {e}")

    if not user:
        current_app.logger.error(f"[STRIPE] Usuário não encontrado: {user_id}")
        return jsonify({"status": "ignored", "reason": "user_not_found"}), 200

    # 9. Atualiza créditos
    try:
        old_balance = user.credits_balance or 0
        user.credits_balance = old_balance + credits
        tx = Transaction(
            user_id=user.id,
            type="purchase",
            amount=credits,
            balance_before=old_balance,
            balance_after=user.credits_balance,
            description=f"Compra de {credits} créditos via Stripe",
            external_id=session_id,
        )
        db.session.add(tx)
        db.session.commit()
        current_app.logger.info(
            f"[STRIPE] ✅ Créditos adicionados! user={user.id} +{credits} "
            f"({old_balance} → {user.credits_balance})"
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[STRIPE] Erro ao salvar: {e}")
        return jsonify({"status": "error", "message": "database_error"}), 200

    return jsonify({"status": "success", "added_credits": credits}), 200