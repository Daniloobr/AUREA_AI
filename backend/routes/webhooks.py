import os
import uuid
import stripe
from flask import Blueprint, request, jsonify, current_app

from models.db_models import db, User, Transaction

webhook_bp = Blueprint("webhook", __name__)


@webhook_bp.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    # 1. Reatribuir api_key dentro da função (garante leitura do env em runtime)
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

    # 2. Usar request.get_data() — NUNCA request.json (quebra a assinatura)
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

    current_app.logger.info("[STRIPE] Evento recebido")

    # Validações iniciais (podem retornar 400 — erros do cliente/config)
    if not sig_header:
        current_app.logger.error("[STRIPE][ERRO] Header Stripe-Signature ausente")
        return jsonify({"error": "Missing Stripe-Signature"}), 400

    if not webhook_secret:
        current_app.logger.error("[STRIPE][ERRO] STRIPE_WEBHOOK_SECRET não configurado no ambiente")
        return jsonify({"error": "Webhook secret não configurado"}), 400

    # 12. Validar assinatura com payload raw
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except stripe.error.SignatureVerificationError as e:
        current_app.logger.error(f"[STRIPE][ERRO] Assinatura inválida: {e}")
        return jsonify({"error": "Assinatura inválida"}), 400
    except Exception as e:
        current_app.logger.error(f"[STRIPE][ERRO] Falha ao construir evento: {e}")
        return jsonify({"error": f"Erro ao processar evento: {e}"}), 400

    # 3. Processar apenas checkout.session.completed
    if event["type"] != "checkout.session.completed":
        current_app.logger.info(f"[STRIPE] Evento ignorado: {event['type']}")
        return jsonify({"status": "ignored", "reason": "unhandled_event_type"}), 200

    # 2. Corrigir acesso ao StripeObject — usar atributos, NÃO .get()
    session = event["data"]["object"]

    session_id      = session.id
    payment_status  = session.payment_status
    metadata        = session.metadata or {}

    user_id  = metadata.get("user_id") or session.client_reference_id
    price_id = metadata.get("price_id")

    # 3 & 13. Logs obrigatórios
    print(f"[STRIPE] SESSION: {session_id}")
    print(f"[STRIPE] USER:    {user_id}")
    print(f"[STRIPE] PRICE:   {price_id}")
    print(f"[STRIPE] STATUS:  {payment_status}")

    current_app.logger.info(
        f"[STRIPE] session_id={session_id} | user_id={user_id} | "
        f"price_id={price_id} | payment_status={payment_status}"
    )

    # 4. Idempotência — verificar antes de qualquer alteração
    if session_id:
        try:
            existing = Transaction.query.filter_by(external_id=session_id).first()
            if existing:
                current_app.logger.warning(f"[STRIPE] Já processado: session_id={session_id}")
                return jsonify({"status": "success", "message": "already_processed"}), 200
        except Exception as e:
            current_app.logger.error(f"[STRIPE][ERRO] Falha na verificação de idempotência: {e}")
            return jsonify({"status": "error", "message": "idempotency_check_failed"}), 200

    # 5. Validar pagamento
    if payment_status != "paid":
        current_app.logger.info(f"[STRIPE] Ignorado — payment_status={payment_status}")
        return jsonify({"status": "ignored", "reason": "not_paid"}), 200

    # user_id obrigatório
    if not user_id:
        current_app.logger.error("[STRIPE][ERRO] user_id ausente no metadata e client_reference_id")
        return jsonify({"status": "ignored", "reason": "user_id_missing"}), 200

    # 6. Fallback para price_id via list_line_items
    if not price_id:
        try:
            line_items = stripe.checkout.Session.list_line_items(session.id, limit=1)
            if line_items and line_items.data:
                price_id = line_items.data[0].price.id
                current_app.logger.info(f"[STRIPE] price_id obtido via line_items: {price_id}")
        except Exception as e:
            current_app.logger.error(f"[STRIPE][ERRO] Falha ao buscar line_items: {e}")
            return jsonify({"status": "error", "message": "failed_to_fetch_line_items"}), 200

    if not price_id:
        current_app.logger.error("[STRIPE][ERRO] price_id ausente — não foi possível obter via fallback")
        return jsonify({"status": "ignored", "reason": "price_id_missing"}), 200

    # 7. Credits map — inclui price de TESTE obrigatoriamente
    credits_map = {
        "price_1TXBt5AXb2fn2YJDXDIF0iKk": 100,   # LIVE — 100 créditos
        "price_1TXBtWAXb2fn2YJDZxm1s4Xz": 200,   # LIVE — 200 créditos
        "price_1TXBtrAXb2fn2YJDNsCz53jj": 400,   # LIVE — 400 créditos
        "price_1TaSlbAXb2fn2YJD21xOhXPs": 100,   # TEST — 100 créditos
    }

    # 10. price_id não mapeado → return 200 (nunca 500)
    credits = credits_map.get(price_id)
    if not credits:
        current_app.logger.error(f"[STRIPE][ERRO] price_id não mapeado: {price_id}")
        print(f"[STRIPE][ERRO] price_id não mapeado: {price_id}")
        return jsonify({"status": "ignored", "reason": "price_id_not_mapped"}), 200

    # 8. Buscar usuário com fallback resiliente
    user = None
    try:
        # Tentativa 1: string direta (UUID como string — padrão do banco)
        user = User.query.get(user_id)

        if not user:
            # Tentativa 2: objeto uuid.UUID nativo
            try:
                user = User.query.get(uuid.UUID(user_id))
            except (ValueError, AttributeError):
                pass

        if not user:
            # Tentativa 3: inteiro (IDs legados)
            try:
                user = User.query.get(int(user_id))
            except (ValueError, TypeError):
                pass

    except Exception as e:
        current_app.logger.error(f"[STRIPE][ERRO] Erro na consulta ao banco para user_id={user_id}: {e}")
        user = None

    print(f"[STRIPE] user encontrado: {user}")
    print(f"[STRIPE] credits: {credits}")
    current_app.logger.info(f"[STRIPE] user={user} | credits={credits}")

    # 9. User não encontrado → return 200 (nunca 500)
    if not user:
        current_app.logger.error(f"[STRIPE][ERRO] Usuário não encontrado para user_id={user_id}")
        return jsonify({"status": "ignored", "reason": "user_not_found"}), 200

    # 11. Atualizar créditos com commit seguro
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
            f"[STRIPE] ✅ Créditos adicionados! user_id={user.id} "
            f"+{credits} (antes={old_balance} → depois={user.credits_balance})"
        )

    except Exception as e:
        try:
            db.session.rollback()
        except Exception as rollback_err:
            current_app.logger.error(f"[STRIPE][ERRO] Rollback falhou: {rollback_err}")

        current_app.logger.error(f"[STRIPE][ERRO] Falha ao salvar no banco: {e}")
        return jsonify({"status": "error", "message": "database_error"}), 200

    return jsonify({"status": "success", "added_credits": credits}), 200
