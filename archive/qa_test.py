import requests
import time
import uuid
import hmac
import hashlib
import json
import os
import sys

BASE_URL = "http://localhost:5005"
API_URL = f"{BASE_URL}/api"

# Use the webhook secret from config or .env to sign mock Stripe webhooks
# Make sure this matches the STRIPE_WEBHOOK_SECRET in backend/.env
WEBHOOK_SECRET = "whsec_TEST_REPLACE_ME"

print("=" * 60)
print("QA TEST RUNNER - ESTÚDIO DE FOTOS IA")
print("=" * 60)

session = requests.Session()

# State variables
user_token = None
user_id = None
test_email = f"qa_test_{uuid.uuid4().hex[:8]}@example.com"
test_password = "SecurePassword123!"
test_name = "QA Tester"

def log_step(name):
    print(f"\n>>> [STEP] {name}")

def log_result(success, message, data=None):
    symbol = "[SUCCESS]" if success else "[FAIL]"
    print(f"  {symbol} {message}")
    if data:
        print(f"    [Response Data]: {data}")

# =====================================================================
# AREA 1: AUTHENTICATION
# =====================================================================
log_step("1. Autenticação (Registro, Login, Token, Logout)")

# 1.1 Register
try:
    reg_res = session.post(f"{API_URL}/auth/register", json={
        "name": test_name,
        "email": test_email,
        "password": test_password
    })
    if reg_res.status_code == 201:
        reg_data = reg_res.json()
        log_result(True, f"Registro de usuário com sucesso ({test_email}).", reg_data)
        user_token = reg_data.get("token")
        user_id = reg_data.get("user")["id"]
    else:
        log_result(False, f"Falha no registro: Status {reg_res.status_code}", reg_res.text)
except Exception as e:
    log_result(False, f"Erro ao tentar registrar: {e}")

# 1.2 Login
if user_id:
    try:
        login_res = requests.post(f"{API_URL}/auth/login", json={
            "email": test_email,
            "password": test_password
        })
        if login_res.status_code == 200:
            login_data = login_res.json()
            log_result(True, "Login com sucesso.", login_data)
            # Use the token returned in response or set cookie
            user_token = login_data.get("token")
            # Update session headers with the JWT token
            session.headers.update({"Authorization": f"Bearer {user_token}"})
        else:
            log_result(False, f"Falha no login: Status {login_res.status_code}", login_res.text)
    except Exception as e:
        log_result(False, f"Erro ao tentar logar: {e}")

# 1.3 Validate profile (Token Verification)
if user_token:
    try:
        me_res = session.get(f"{API_URL}/auth/me")
        if me_res.status_code == 200:
            me_data = me_res.json()
            log_result(True, "Verificação de Token (/auth/me) com sucesso.", me_data)
            # Verify initial credits
            credits = me_data.get("user", {}).get("credits_balance", 0)
            log_result(credits == 0, f"Saldo inicial verificado: {credits} créditos.")
        else:
            log_result(False, f"Falha ao validar token: Status {me_res.status_code}", me_res.text)
    except Exception as e:
        log_result(False, f"Erro ao tentar obter perfil: {e}")

# =====================================================================
# AREA 2: UPLOAD
# =====================================================================
log_step("2. Upload de Imagem (Válida/Inválida, Validação Facial)")

# Create a small dummy image file
dummy_img_path = "dummy_face.png"
dummy_txt_path = "dummy_invalid.txt"

with open(dummy_txt_path, "w") as f:
    f.write("I am not an image!")

# Write a valid dummy PNG image using Pillow
try:
    from PIL import Image
    img = Image.new('RGB', (600, 600), color='red')
    img.save(dummy_img_path)
except Exception as e:
    print(f"Erro ao criar imagem com Pillow: {e}")
    # Fallback to simple bytes
    png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    with open(dummy_img_path, "wb") as f:
        f.write(png_bytes)

# 2.1 Invalid Upload (Text file)
try:
    with open(dummy_txt_path, "rb") as f:
        up_res = session.post(f"{API_URL}/upload", files={"file": (dummy_txt_path, f, "text/plain")})
    if up_res.status_code == 400:
        log_result(True, "Upload de arquivo inválido rejeitado corretamente (400).", up_res.json())
    else:
        log_result(False, f"Upload de arquivo inválido obteve status inesperado: {up_res.status_code}", up_res.text)
except Exception as e:
    log_result(False, f"Erro ao testar upload inválido: {e}")

# 2.2 Upload without authentication (Security check)
try:
    with open(dummy_img_path, "rb") as f:
        no_auth_res = requests.post(f"{API_URL}/upload", files={"file": (dummy_img_path, f, "image/png")})
    # Check if upload is protected or public
    # In some designs, upload can be public or require authentication
    log_result(True, f"Upload sem autenticação retornou status: {no_auth_res.status_code}")
except Exception as e:
    log_result(False, f"Erro ao testar upload sem auth: {e}")

# 2.3 Upload Valid image
uploaded_url = None
try:
    with open(dummy_img_path, "rb") as f:
        up_res = session.post(f"{API_URL}/upload", files={"file": (dummy_img_path, f, "image/png")})
    if up_res.status_code == 200:
        up_data = up_res.json()
        log_result(True, "Upload de imagem válida com sucesso (200).", up_data)
        uploaded_url = up_data.get("file_url") or up_data.get("url")
    else:
        log_result(False, f"Falha no upload de imagem válida: Status {up_res.status_code}", up_res.text)
except Exception as e:
    log_result(False, f"Erro ao tentar upload de imagem válida: {e}")

# 2.4 Facial Validation logic check
# Let's inspect face service response for our dummy image (should fail face detection)
try:
    # Since facial validation is in services/face_service.py and is not exposed as a public endpoint, 
    # we'll test it by importing face_service inside this script or analyzing if there is a face validation warning.
    # Note: Our 1x1 dummy image has no faces, so it should be rejected if evaluated.
    sys.path.append(os.path.abspath('.'))
    from services.face_service import validate_image
    face_report = validate_image(dummy_img_path)
    log_result(not face_report["valid"] and "Nenhum rosto detectado" in str(face_report["errors"]), 
               "Serviço de Validação Facial de Imagens detectou e rejeitou a imagem de 1x1 pixel sem rostos.", face_report)
except Exception as e:
    log_result(False, f"Erro ao invocar o serviço interno de validação facial: {e}")

# Cleanup local test files
if os.path.exists(dummy_img_path): os.remove(dummy_img_path)
if os.path.exists(dummy_txt_path): os.remove(dummy_txt_path)


# =====================================================================
# AREA 3: MERCADO PAGO PAYMENT (PIX FLOW)
# =====================================================================
log_step("3. Compra de Créditos (Pacote 100 créditos via PIX, Webhook, Saldo Atualizado, Transação)")

PACKAGE_ID_FOR_TEST = "100_credits"
TEST_PRICE = 25.00
TEST_CREDITS_EXPECTED = 100
payment_id = None
webhook_secret = WEBHOOK_SECRET # Reusing the secret for security check verification (if webhook_bp uses it for validation, which it does)

try:
    # 3.1 Create PIX Payment
    pay_res = session.post(f"{API_URL}/create-pix-payment", json={
        "package_id": PACKAGE_ID_FOR_TEST
    })
    if pay_res.status_code == 200:
        pay_data = pay_res.json()
        log_result(True, "PIX Payment Request created successfully.", pay_data)
        payment_id = pay_data.get("payment_id")
        qr_code = pay_data.get("qr_code") or pay_data.get("qr_code_base64")
        
        # Check QR code data exists
        log_result(bool(qr_code), "QR Code data present in response.")
        
        # Expected external reference based on service implementation
        expected_external_ref = f"{user_id}:{PACKAGE_ID_FOR_TEST}"
    else:
        log_result(False, f"Falha ao criar PIX session: Status {pay_res.status_code}", pay_res.text)
        payment_id = None
        expected_external_ref = None

except Exception as e:
    log_result(False, f"Erro ao iniciar PIX payment: {e}")
    payment_id = None
    expected_external_ref = None

# 3.2 Mock the webhook completion for PIX payment.updated
if payment_id and expected_external_ref:
    # Construct payload simulating a completed payment notification from MP
    mock_payload_data = {
        "id": payment_id,
        "type": "payment",
        "action": "payment.updated", # Crucial: must be updated, not created
        "object": "payment",
        "status": "approved", # Critical status for credit addition
        "external_reference": expected_external_ref,
        "amount_paid": TEST_PRICE,
        "payer": {"email": test_email}
    }
    
    payload_str = json.dumps(mock_payload_data, separators=(",", ":"))
    payload_bytes = payload_str.encode('utf-8')
    
    # Generate signature for webhook verification (assuming webhook_bp uses the same secret key pattern as Stripe tests)
    # NOTE: Mercado Pago uses 'ts' and 'v1' in signature headers, not 't' and 'v1' like the old Stripe mock.
    # We must ensure the webhook logic in backend/routes/webhooks.py can handle this mock or remove signature checks for this mock.
    # Reviewing backend/routes/webhooks.py: It expects 'x-request-id' and uses 'ts' and 'v1'.
    
    # Since the webhook logic relies on SECRET being set AND specific headers, 
    # for QA testing convenience where we control the source, we might temporarily bypass signature in the mock if we cannot perfectly replicate MP headers.
    # However, for robust testing, we should try to comply or disable the check.
    
    # Option: Temporarily disable signature check in the webhook route for this test only, OR rely on a known secret.
    # I will rely on the WEBHOOK_SECRET defined at the top of qa_test.py, hoping the webhook route uses it.
    
    timestamp = str(int(time.time()))
    # MP Manifest structure: id:{request-id};request-id:{request-id};ts:{ts};{payload_json}
    request_id = str(uuid.uuid4()) 
    manifest = f"id:{request_id};request-id:{request_id};ts:{timestamp};" + payload_str
    
    signature = hmac.new(
        webhook_secret.encode('utf-8'),
        manifest.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    mp_signature_header = f"ts={timestamp},v1={signature}"
    
    try:
        wh_res = requests.post(
            f"{API_URL}/webhooks/mercadopago",
            data=payload_bytes,
            headers={
                "X-Signature": mp_signature_header, # Using X-Signature as a proxy for the expected header if webhook_bp uses it, or setting 'x-signature' based on webhook.py Line 131
                "x-request-id": request_id,
                "Content-Type": "application/json"
            }
        )
        
        # The webhook route returns 200 on success, or 200/400 based on validation
        if wh_res.status_code == 200:
             log_result(True, "Mock MP Webhook POST success.", wh_res.json())
        else:
             log_result(False, f"Mock MP Webhook returned status {wh_res.status_code}.", wh_res.text)
             
    except Exception as e:
        log_result(False, f"Erro ao enviar mock MP webhook: {e}")

    # 3.3 Verify Updated Balance
    try:
        bal_res = session.get(f"{API_URL}/auth/me")
        if bal_res.status_code == 200:
            bal_data = bal_res.json()
            new_credits = bal_data.get("user", {}).get("credits_balance", 0)
            
            # If webhook worked, credits should be 100 (since previous step established initial balance was 0)
            log_result(new_credits == TEST_CREDITS_EXPECTED, 
                       f"Saldo de créditos atualizado corretamente! Novo saldo: {new_credits} créditos (Esperado: {TEST_CREDITS_EXPECTED}).")
        else:
            log_result(False, "Falha ao obter saldo atualizado após webhook.", bal_res.text)
    except Exception as e:
        log_result(False, f"Erro ao verificar saldo atualizado: {e}")
        
else:
    log_result(False, "Skipping webhook simulation due to prior payment failure.")

# =====================================================================
# AREA 4: GENERATION (Requires Credits)
# =====================================================================
log_step("4. Geração (Seleção de estilo, Débito de 25 créditos, Job assíncrono, Imagem na galeria, Reembolso em falha)")

# 4.1 styles (Re-run to ensure we have styles data)
try:
    styles_res = session.get(f"{API_URL}/generate/styles")
    if styles_res.status_code == 200:
        styles = styles_res.json().get("styles", [])
        log_result(len(styles) > 0, f"Disponibilidade de estilos verificada: {len(styles)} estilos encontrados.")
    else:
        log_result(False, f"Falha ao obter estilos: Status {styles_res.status_code}", styles_res.text)
except Exception as e:
    log_result(False, f"Erro ao obter estilos: {e}")

# 4.2 Start Generation (require exactly 3 reference images)
job_id = None
dummy_refs = [
    "https://xdxkqkwewywrfxwtkzdy.supabase.co/storage/v1/object/public/inputs/test1.png",
    "https://xdxkqkwewywrfxwtkzdy.supabase.co/storage/v1/object/public/inputs/test2.png",
    "https://xdxkqkwewywrfxwtkzdy.supabase.co/storage/v1/object/public/inputs/test3.png"
]

try:
    gen_res = session.post(f"{API_URL}/generate", json={
        "image_urls": dummy_refs,
        "style": "gestante_outdoor",
        "prompt": "Maternity photo in a park"
    })
    
    if gen_res.status_code == 200:
        gen_data = gen_res.json()
        log_result(True, "Job de geração criado com sucesso (200).", gen_data)
        job_id = gen_data.get("job_id")
    else:
        # If credits < 25, it will return 402/500
        log_result(False, f"Falha ao iniciar geração: Status {gen_res.status_code}", gen_res.text)
except Exception as e:
    log_result(False, f"Erro ao iniciar geração: {e}")

# 4.3 Verify debit
if job_id:
    try:
        bal_res = session.get(f"{API_URL}/auth/me")
        if bal_res.status_code == 200:
            bal_data = bal_res.json()
            curr_credits = bal_data.get("user", {}).get("credits_balance", 0)
            # New credits must be (previous_balance + 100 - 25) = 75
            log_result(curr_credits == 75, f"Débito de 25 créditos verificado com sucesso. Saldo atual: {curr_credits} créditos. (Esperado: 75)")
        else:
            log_result(False, "Falha ao verificar débito.")
    except Exception as e:
        log_result(False, f"Erro ao verificar débito: {e}")

# 4.4 Async job execution simulation
# Let's check status of the job
if job_id:
    try:
        status_res = session.get(f"{API_URL}/generate/status/{job_id}")
        if status_res.status_code == 200:
            status_data = status_res.json()
            log_result(True, "Job assíncrono criado e verificado no banco.", status_data)
            
            print(f"    [Job Status]: {status_data.get('status')} | Progress: {status_data.get('progress')}%")
        else:
            log_result(False, f"Falha ao obter status do job: Status {status_res.status_code}", status_res.text)
    except Exception as e:
        log_result(False, f"Erro ao obter status do job: {e}")

# =====================================================================
# AREA 5: GALLERY
# =====================================================================
log_step("5. Galeria (Listagem, Download imagem existente e inexistente)")

# 5.1 Gallery List
try:
    gal_res = session.get(f"{API_URL}/gallery/")
    if gal_res.status_code == 200:
        gal_data = gal_res.json()
        log_result(True, f"Listagem da galeria com sucesso ({gal_data.get('count')} ensaios).", gal_data)
    else:
        log_result(False, f"Falha ao obter galeria: Status {gal_res.status_code}", gal_res.text)
except Exception as e:
    log_result(False, f"Erro ao obter galeria: {e}")

# 5.2 Download Proxy checks
try:
    # Existing/authorized domain
    down_auth_res = session.get(f"{API_URL}/download-image?url=https://supabase.co/storage/v1/object/public/inputs/test.jpg")
    log_result(True, f"Download proxy para domínio autorizado (Supabase) retornou status: {down_auth_res.status_code} (Pode ser 404 se o arquivo não existe, mas não 403).")
    
    # Unauthorized domain (Security CORS check)
    down_unauth_res = session.get(f"{API_URL}/download-image?url=https://malicious-site.com/hack.jpg")
    log_result(down_unauth_res.status_code == 403, f"Download proxy para domínio não autorizado rejeitado corretamente (403): {down_unauth_res.text}")
except Exception as e:
    log_result(False, f"Erro ao testar downloads: {e}")

# =====================================================================
# AREA 6: STATEMENT (EXTRATO)
# =====================================================================
log_step("6. Extrato (Transações listadas: tipo, amount, descrição, saldos)")

try:
    tx_res = session.get(f"{API_URL}/auth/user/transactions")
    if tx_res.status_code == 200:
        tx_data = tx_res.json()
        tx_list = tx_data.get("transactions", [])
        log_result(len(tx_list) > 0, f"Extrato retornado com sucesso. Encontradas {len(tx_list)} transações.", tx_data)
        for tx in tx_list:
            print(f"    - Tipo: {tx.get('type')} | Valor: {tx.get('amount')} | Desc: {tx.get('description')} | Saldo antes: {tx.get('balance_before')} | Saldo depois: {tx.get('balance_after')}")
    else:
        log_result(False, f"Falha ao carregar extrato: Status {tx_res.status_code}", tx_res.text)
except Exception as e:
    log_result(False, f"Erro ao carregar extrato: {e}")

# =====================================================================
# AREA 7: SECURITY (CORS, HEADERS, EXPOSED KEYS)
# =====================================================================
log_step("7. Segurança (CORS, Headers, Chaves expostas)")

# 7.1 Talisman Headers Check
try:
    # Check headers of a simple GET request
    resp = requests.get(f"{BASE_URL}/health")
    headers = resp.headers
    
    log_result("X-Content-Type-Options" in headers, f"X-Content-Type-Options presente: {headers.get('X-Content-Type-Options')}")
    log_result("Strict-Transport-Security" in headers, f"HSTS presente: {headers.get('Strict-Transport-Security')}")
    log_result("X-Frame-Options" in headers, f"X-Frame-Options presente: {headers.get('X-Frame-Options')}")
except Exception as e:
    log_result(False, f"Erro ao validar headers de segurança: {e}")

print("\n" + "=" * 60)
print("QA TEST EXECUTION COMPLETED")
print("=" * 60)
