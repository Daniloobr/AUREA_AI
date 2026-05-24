import stripe
import os

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

def create_checkout_session(price_id, user_id, user_email, success_url, cancel_url):
    """
    Creates a Stripe Checkout Session for a specific price ID and user.
    Uses fallback logic in case PIX is not active in the Stripe dashboard.
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card', 'pix'],
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
                'user_id': str(user_id),
                'price_id': price_id,
            }
        )
        return {"sessionId": session.id, "url": session.url}
    except stripe.error.InvalidRequestError as e:
        # Fallback to card-only if PIX is not activated
        if 'pix' in str(e).lower() or 'payment method' in str(e).lower():
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
                    'user_id': str(user_id),
                    'price_id': price_id,
                }
            )
            return {"sessionId": session.id, "url": session.url}
        raise e
