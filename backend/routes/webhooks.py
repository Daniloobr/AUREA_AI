import os
import uuid
import stripe
from flask import Blueprint, request, jsonify, current_app
from models.db_models import db, User, Transaction

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
    
    # Payload em BYTES (obrigatório para assinatura)
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

    current_app.logger.info("[WEBHOOK] Requisição recebida")

    if not sig_header:
        return jsonify({"error": "Missing Stripe-Signature"}), 400
    if not webhook_secret:
        return jsonify({"error": "Webhook secret not configured"}), 500

    # Verifica assinatura
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        current_app.logger.info(f"[WEBHOOK] Evento verificado: {event['type']}")
    except Exception as e:
        current_app.logger.error(f"[WEBHOOK] Falha na assinatura: {e}")
        return jsonify({"error": "Invalid signature"}), 400

    # Processa apenas checkout.session.completed
    if event["type"] != "checkout.session.completed":
        return jsonify({"status": "ignored"}), 200

    session = event["data"]["object"]

    # Extrai dados com segurança
    session_id = session.id
    payment_status = session.payment_status

    # Metadata: tratamento robusto (evita KeyError)
    metadata = {}
    if hasattr(session, 'metadata') and session.metadata is not None:
        if hasattr(session.metadata, 'to_dict'):
            metadata = session.metadata.to_dict()
        elif isinstance(session.metadata, dict):
            metadata = session.metadata
        else:
            try:
                metadata = dict(session.metadata)
            except:
                pass

    user_id = metadata.get("user_id") or getattr(session, 'client_reference_id', None)
    price_id = metadata.get("price_id")

    current_app.logger.info(f"[WEBHOOK] session={session_id}, user={user_id}, price={price_id}, status={payment_status}")

    # Idempotência
    if session_id and Transaction.query.filter_by(external_id=session_id).first():
        current_app.logger.warning(f"[WEBHOOK] Evento duplicado: {session_id}")
        return jsonify({"status": "already_processed"}), 200

    if payment_status != "paid":
        return jsonify({"status": "ignored", "reason": "not_paid"}), 200

    if not user_id:
        return jsonify({"status": "ignored", "reason": "no_user_id"}), 200

    # Fallback price_id via line_items (se necessário)
    if not price_id:
        try:
            line_items = stripe.checkout.Session.list_line_items(session_id, limit=1)
            if line_items and line_items.data:
                price_id = line_items.data[0].price.id
        except Exception as e:
            current_app.logger.error(f"Erro line_items: {e}")

    if not price_id:
        return jsonify({"status": "ignored", "reason": "no_price_id"}), 200

    # Mapeamento price_id -> créditos (incluindo seu ID de teste)
    credits_map = {
        "price_1TXBt5AXb2fn2YJDXDIF0iKk": 100,   # live
        "price_1TXBtWAXb2fn2YJDZxm1s4Xz": 200,
        "price_1TXBtrAXb2fn2YJDNsCz53jj": 400,
        "price_1TaSlbAXb2fn2YJD21xOhXPs": 100,   # teste (seu)
    }
    credits = credits_map.get(price_id)
    if not credits:
        current_app.logger.error(f"Price não mapeado: {price_id}")
        return jsonify({"status": "ignored", "reason": "price_not_mapped"}), 200

    # Busca o usuário (UUID compatível)
    user = None
    try:
        user = User.query.get(user_id)
        if not user:
            try:
                user = User.query.get(uuid.UUID(user_id))
            except:
                pass
        if not user:
            try:
                user = User.query.get(int(user_id))
            except:
                pass
    except Exception as e:
        current_app.logger.error(f"Erro busca user: {e}")

    if not user:
        return jsonify({"status": "ignored", "reason": "user_not_found"}), 200

    # Atualiza créditos
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
        current_app.logger.info(f"✅ {credits} créditos adicionados ao user {user.id} (saldo: {user.credits_balance})")
        return jsonify({"status": "success", "added_credits": credits}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro DB: {e}", exc_info=True)
        return jsonify({"error": "Database error"}), 500