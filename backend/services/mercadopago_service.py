import os
from mercadopago import MP
from mercadopago.config import MPConfig

# --- Constants (Should be moved to environment variables in production) ---
MP_PUBLIC_KEY = "TEST-d2fd38e9-7a83-497e-976d-2263fa0948ba"
MP_ACCESS_TOKEN = "TEST-4071444009330339-052500-30c5003cbcb9fe44932d613ce33c5009-3425510730"
SELLER_USER_ID = "3423925626"
BUYER_USER_ID = "3423210117"
# -------------------------------------------------------------------------

# Configuration (Using Access Token)
MP_CONFIG = MPConfig.from_access_token(MP_ACCESS_TOKEN)
mp = MP(MP_CONFIG)

def create_card_payment(card_token: str, amount: float, description: str, payer_email: str, external_ref: str):
    """
    Creates a card payment using a Mercado Pago token.
    """
    try:
        payment_data = {
            "transaction_amount": amount,
            "token": card_token,
            "description": description,
            "installments": 1,
            "payer": {
                "email": payer_email,
                "identification": {
                    "type": "other",
                    "number": BUYER_USER_ID # Using Buyer ID as a placeholder for identification if required
                }
            }
        }
        
        # For card payments, we use the preference to link to the seller account if necessary,
        # but standard card payments usually go directly through the access token owner.
        # For simplicity, we use the direct payment creation endpoint available on the MP object.
        
        result = mp.payment.create(payment_data)
        
        # Check if payment was created successfully (HTTP 201)
        if result.status_code == 201:
            return result.json()
        else:
            print(f"Card payment failed. Status: {result.status_code}, Response: {result.json()}")
            result.raise_for_status() # Raise an exception for other HTTP errors

    except Exception as e:
        print(f"Error creating card payment: {e}")
        raise

def create_pix_payment(amount: float, description: str, payer_email: str, external_ref: str):
    """
    Creates a PIX payment and returns the Base64 encoded QR code data (or notification_url/id).
    For simplicity in this initial setup, we create an *order* or *preference* that generates the QR code link/data.
    Mercado Pago often handles PIX generation via an Order/Preference, which then provides the QR code data.
    For a direct Pix payment capture, we use the 'pix' type in payment creation.
    """
    try:
        payment_data = {
            "transaction_amount": amount,
            "description": description,
            "payment_method_id": "pix",
            "payer": {
                "email": payer_email,
                "identification": {
                    "type": "other",
                    "number": BUYER_USER_ID
                }
            },
            # Notification URL is critical for backend confirmation
            "notification_url": f"https://aurea-ai-ftqa.onrender.com/api/webhooks/mercadopago?external_reference={external_ref}"
        }

        result = mp.payment.create(payment_data)

        if result.status_code == 201:
            payment_info = result.json()
            
            # PIX QR code data is often available in 'point_of_interaction' for 'qr_code' payments
            # or as a 'transaction_details' -> 'external_resource_url' for 'qr_code_dynamic' (which we assume we use here)
            
            if payment_info.get('point_of_interaction', {}).get('type') == 'qr_code':
                return {
                    "status": payment_info.get("status"),
                    "payment_id": payment_info.get("id"),
                    "qr_code_base64": payment_info['point_of_interaction']['qr_data'], # Contains the base64 or raw data
                    "transaction_id": payment_info.get("id")
                }
            else:
                 # If it's not a direct QR code (e.g., it's a redirect URL for a dynamic QR), return what's available
                return {
                    "status": payment_info.get("status"),
                    "payment_id": payment_info.get("id"),
                    "transaction_id": payment_info.get("id"),
                    "qr_code_data": payment_info.get('point_of_interaction', {}).get('qr_code', {}).get('in_store_order_id', 'N/A') # Fallback or dynamic URL
                }
        else:
            print(f"PIX payment creation failed. Status: {result.status_code}, Response: {result.json()}")
            result.raise_for_status()

    except Exception as e:
        print(f"Error creating PIX payment: {e}")
        raise


def get_payment_status(payment_id: str):
    """
    Fetches payment status by ID.
    """
    try:
        result = mp.payment.get(payment_id)
        
        if result.status_code == 200:
            return result.json()
        else:
            result.raise_for_status()

    except Exception as e:
        print(f"Error fetching payment status for {payment_id}: {e}")
        raise

# Placeholder for webhook handler logic (This logic lives in the webhook endpoint)
def handle_webhook_notification(data):
    """
    This function would typically be called by the webhook route handler to process
    incoming notifications from Mercado Pago.
    """
    # Example structure assuming 'data' is the parsed JSON body
    topic = data.get('topic')
    id = data.get('id')
    
    if topic == 'payment' and id:
        # Fetch latest status from MP to ensure accuracy
        status_data = get_payment_status(id)
        status = status_data.get('status')
        
        # Logic to credit user balance and create Transaction record goes here based on status
        print(f"Webhook received payment ID {id} with status {status}")
        
        if status == 'approved':
            # Integrate with existing user/transaction models here
            print("INFO: Payment Approved - Crediting user balance and creating transaction record.")
            return {"success": True, "message": "Transaction processed"}
            
    return {"success": False, "message": "Unhandled topic or ID missing"}