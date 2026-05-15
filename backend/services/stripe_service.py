import os
import stripe

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

class StripeService:
    def create_checkout_session(self, price_id, user_id, user_email, success_url, cancel_url):
        try:
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
                    "price_id": price_id
                }
            )
            return {"sessionId": session.id, "url": session.url}
        except Exception as e:
            print(f"Error creating Stripe checkout session: {e}")
            return None

    def handle_webhook(self, payload, sig_header, webhook_secret):
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except ValueError as e:
            # Invalid payload
            print(f"Invalid payload for Stripe webhook: {e}")
            return None
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            print(f"Invalid signature for Stripe webhook: {e}")
            return None

stripe_service = StripeService()
