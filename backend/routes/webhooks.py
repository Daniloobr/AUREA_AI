import os
import uuid
import stripe
from flask import Blueprint, request, jsonify, current_app

from models.db_models import db, User, Transaction

webhook_bp = Blueprint("webhook", __name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


@webhook_bp.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

    current_app.logger.info("[STRIPE] Evento recebido")

    # Validação básica
    if not sig_header:
        current_app.logger.error("[STRIPE][ERRO] Missing Stripe-Signature")
        return jsonify({"error": "Missing Stripe-Signature"}), 400

    if not webhook_secret:
        current_app.logger.error("[STRIPE][ERRO] Webhook secret não configurado")
        return jsonify({"error": "Webhook secret não configurado"}), 200

    # Verificar assinatura
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        current_app.logger.error(f"[STRIPE][ERRO] Assinatura inválida: {e}")
        return jsonify({"error": f"Assinatura inválida: {e}"}), 400

    # Apenas evento necessário
    if event["type"] != "checkout.session.completed":
        return jsonify({"status": "ignored", "reason": "unhandled_event_type"}), 200

    session = event["data"]["object"]

    session_id = session.get("id")
    payment_status = session.get("payment_status")

    metadata = session.get("metadata") or {}

    user_id = metadata.get("user_id") or session.get("client_reference_id")
    price_id = metadata.get("price_id")

    # Requisito 5: Logs detalhados (print e logger)
    print(f"user_id: {user_id}")
    print(f"price_id: {price_id}")
    current_app.logger.info(
        f"[STRIPE] user_id={user_id} price_id={price_id} session_id={session_id} payment_status={payment_status}"
    )

    # Idempotência (ANTES de tudo)
    if session_id:
        try:
            existing_tx = Transaction.query.filter_by(external_id=session_id).first()
            if existing_tx:
                current_app.logger.warning(f"[STRIPE] Transação já processada anteriormente para session_id={session_id}")
                return jsonify({"status": "success", "message": "already_processed"}), 200
        except Exception as e:
            current_app.logger.error(f"[STRIPE][ERRO] Erro ao verificar idempotência: {e}")
            # Não quebra com 500, segue em frente ou retorna 200 com segurança
            return jsonify({"status": "error", "message": "idempotency_check_error"}), 200

    # Só processa se pago
    if payment_status != "paid":
        current_app.logger.info(f"[STRIPE] Ignorado - session_id={session_id} não está pago (status={payment_status})")
        return jsonify({"status": "ignored", "reason": "not_paid"}), 200

    # Requisito 2 & 8: user_id obrigatório, evitar 500 se ausente
    if not user_id:
        current_app.logger.error("[STRIPE][ERRO] user_id ausente")
        print("[STRIPE][ERRO] user_id ausente")
        return jsonify({"status": "ignored", "reason": "user_id_missing"}), 200

    # Fallback para price_id
    if not price_id:
        try:
            line_items = stripe.checkout.Session.list_line_items(session_id, limit=1)
            if line_items.data:
                price_id = line_items.data[0].price.id
        except Exception as e:
            current_app.logger.error(f"[STRIPE][ERRO] Falha ao buscar line_items: {e}")
            # Não retornar 500
            return jsonify({"status": "error", "message": "failed_to_fetch_line_items"}), 200

    if not price_id:
        current_app.logger.error("[STRIPE][ERRO] price_id ausente")
        print("[STRIPE][ERRO] price_id ausente")
        return jsonify({"status": "ignored", "reason": "price_id_missing"}), 200

    # Requisito 3: Mapeamento de créditos (garantir price_1TaSlbAXb2fn2YJD21xOhXPs mapeado)
    credits_map = {
        "price_1TXBt5AXb2fn2YJDXDIF0iKk": 100,
        "price_1TXBtWAXb2fn2YJDZxm1s4Xz": 200,
        "price_1TXBtrAXb2fn2YJDNsCz53jj": 400,
        "price_1TaSlbAXb2fn2YJD21xOhXPs": 100,  # TEST (temporário): PriceID de teste
    }

    # Requisito 4 & 8: Evitar crash se price_id não mapeado
    credits = credits_map.get(price_id)
    if not credits:
        current_app.logger.error(f"[STRIPE][ERRO] price_id não mapeado: {price_id}")
        print(f"price_id não mapeado: {price_id}")
        return jsonify({"status": "ignored", "reason": "price_id_not_mapped"}), 200

    # Requisito 1: Buscar usuário corretamente (UUID, string ou integer)
    user = None
    try:
        # Tenta buscar diretamente usando a string original (UUID)
        user = User.query.get(user_id)
        if not user:
            # Tenta converter para UUID se o banco exigir o tipo UUID nativo
            import uuid
            try:
                uuid_obj = uuid.UUID(user_id)
                user = User.query.get(uuid_obj)
            except ValueError:
                pass
        if not user:
            # Tenta converter para int para compatibilidade com IDs inteiros
            try:
                user = User.query.get(int(user_id))
            except ValueError:
                pass
    except Exception as e:
        current_app.logger.error(f"[STRIPE][ERRO] Erro ao consultar banco de dados para user_id {user_id}: {e}")
        user = None

    # Requisito 5: Log detalhado do usuário encontrado e créditos
    print(f"user encontrado: {user}")
    print(f"credits: {credits}")
    current_app.logger.info(f"[STRIPE] user encontrado={user}, credits={credits}")

    # Requisito 2 & 8: Evitar crash e 500 se o usuário não existir
    if not user:
        current_app.logger.error(f"[STRIPE][ERRO] Usuário não encontrado no banco de dados para user_id: {user_id}")
        return jsonify({"status": "ignored", "reason": "user_not_found"}), 200

    # Requisito 6 & 8: Atualizar créditos com transação e commit seguro
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
            f"[STRIPE] Créditos adicionados com sucesso! user_id={user.id} +{credits} (saldo anterior={old_balance}, atual={user.credits_balance})"
        )

    except Exception as e:
        try:
            db.session.rollback()
        except Exception as rollback_err:
            current_app.logger.error(f"[STRIPE][ERRO] Falha ao executar rollback: {rollback_err}")
            
        current_app.logger.error(f"[STRIPE][ERRO] Erro no banco de dados durante atualização: {e}")
        return jsonify({"status": "error", "message": "database_transaction_failed"}), 200

    return jsonify({"status": "success", "added_credits": credits}), 200
