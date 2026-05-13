import requests
import json
import sys

# Configurações
BASE_URL = "http://127.0.0.1:5000/api"
USER_EMAIL = "demo@example.com"
USER_PASSWORD = "password"

def test_generation():
    print("🚀 Iniciando teste de geração...")

    # 1. Login para obter Token
    print("\n[1/4] Fazendo login...")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": USER_EMAIL,
        "password": USER_PASSWORD
    })
    
    if login_res.status_code != 200:
        print(f"❌ Erro no login: {login_res.text}")
        return

    auth_data = login_res.json()
    token = auth_data.get("token")
    user = auth_data.get("user")
    print(f"✅ Logado como {user['name']}. Saldo: {user['credits_balance']} moedas.")

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload de Imagem
    print("\n[2/4] Enviando imagem de teste...")
    # Criamos um arquivo de teste se não existir ou usamos um existente
    try:
        with open("test_image.jpg", "rb") as f:
            files = {"file": f}
            upload_res = requests.post(f"{BASE_URL}/upload", files=files, headers=headers)
    except FileNotFoundError:
        print("❌ Arquivo 'test_image.jpg' não encontrado na pasta raiz.")
        return

    if upload_res.status_code != 200:
        print(f"❌ Erro no upload: {upload_res.text}")
        return

    upload_data = upload_res.json()
    image_url = upload_data.get("file_url")
    print(f"✅ Upload concluído: {image_url}")

    # 3. Solicitar Geração
    print("\n[3/4] Solicitando geração de ensaio...")
    gen_res = requests.post(f"{BASE_URL}/generate", json={
        "image_url": image_url,
        "tipo_ensaio": "gestante_outdoor"
    }, headers=headers)

    if gen_res.status_code != 200:
        print(f"❌ Erro na geração: {gen_res.text}")
        return

    gen_data = gen_res.json()
    job_id = gen_data.get("job_id")
    print(f"✅ Job criado: {job_id}. Aguardando processamento...")

    # 4. Polling de Status
    print("\n[4/4] Monitorando progresso...")
    attempts = 0
    while attempts < 30: # 5 minutos max
        status_res = requests.get(f"{BASE_URL}/generate/{job_id}/result", headers=headers)
        status_data = status_res.json()
        
        status = status_data.get("status")
        progress = status_data.get("progress", 0)
        message = status_data.get("message", "")

        print(f"⏳ [{status}] {progress}% - {message}")

        if status == "SUCCEEDED":
            print(f"\n🎉 SUCESSO! Imagens geradas: {status_data.get('images')}")
            break
        elif status == "FAILED":
            print(f"\n❌ A geração falhou: {status_data.get('error')}")
            break
        
        attempts += 1
        import time
        time.sleep(10)

if __name__ == "__main__":
    test_generation()
