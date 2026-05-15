import os
import stripe
import logging

# Configuração de log (opcional, mas útil)
logger = logging.getLogger(__name__)

# Configura a chave da API do Stripe a partir da variável de ambiente
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')


class StripeService:
    """
    Serviço para integração com o Stripe (checkout e webhooks).
    """

    def create_checkout_session(self, price_id, user_id, user_email, success_url, cancel_url):
        """
        Cria uma sessão de checkout no Stripe para pagamento único.

        Args:
            price_id (str): ID do preço no Stripe (ex: 'price_...')
            user_id (str): ID do usuário no sistema
            user_email (str): Email do usuário
            success_url (str): URL de redirecionamento em caso de sucesso
            cancel_url (str): URL de redirecionamento em caso de cancelamento

        Returns:
            dict: {'sessionId': str, 'url': str} ou {'error': str} em caso de erro
        """
        if not stripe.api_key:
            logger.error("STRIPE_SECRET_KEY não configurada no ambiente")
            return {"error": "Gateway de pagamento não configurado."}

        if not price_id:
            return {"error": "ID do preço não informado."}

        try:
            logger.info(f"Criando sessão de checkout: price={price_id}, user={user_id}")
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=str(user_id),
                customer_email=user_email,
                metadata={
                    "price_id": price_id,
                    "user_id": str(user_id)
                }
            )
            logger.info(f"Sessão criada com sucesso: {session.id}")
            return {"sessionId": session.id, "url": session.url}

        except stripe.error.InvalidRequestError as e:
            # Erros comuns: price_id inválido, parâmetros faltando
            logger.error(f"Stripe InvalidRequestError: {e}")
            if "No such price" in str(e):
                return {"error": "Pacote de créditos inválido. Entre em contato com o suporte."}
            return {"error": f"Erro na requisição ao Stripe: {e.user_message}"}

        except stripe.error.AuthenticationError as e:
            logger.error(f"Stripe AuthenticationError: {e}")
            return {"error": "Chave de API do Stripe inválida ou não configurada."}

        except stripe.error.APIConnectionError as e:
            logger.error(f"Stripe APIConnectionError: {e}")
            return {"error": "Falha de conexão com o gateway de pagamento. Tente novamente."}

        except Exception as e:
            logger.error(f"Erro inesperado ao criar sessão Stripe: {e}")
            # Captura qualquer outra exceção e retorna mensagem genérica
            return {"error": "Falha ao criar sessão de pagamento no Stripe."}

    def handle_webhook(self, payload, sig_header, webhook_secret):
        """
        Constrói e valida o evento do webhook do Stripe.

        Returns:
            event (dict) ou None em caso de erro
        """
        if not webhook_secret:
            logger.error("STRIPE_WEBHOOK_SECRET não configurada")
            return None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except ValueError as e:
            logger.error(f"Payload inválido no webhook: {e}")
            return None
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Assinatura inválida no webhook: {e}")
            return None


# Instância única para ser importada em outros módulos
stripe_service = StripeService()