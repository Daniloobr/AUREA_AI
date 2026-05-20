import os
import sys

# Adicionar o diretório pai ao sys.path para importar os serviços
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Configurar variáveis de ambiente manualmente para o teste
os.environ['PAGSEGURO_EMAIL'] = 'devdanilobr@gmail.com'
os.environ['PAGSEGURO_TOKEN_SANDBOX'] = 'd03af6b3-614f-4983-b7e3-88e5a15f7e4ec3b10c2d413f863867f8a87df6abaab039a8-70a9-496d-9097-5446420d5acc'
os.environ['PAGSEGURO_SANDBOX'] = 'True'
os.environ['PAGSEGURO_NOTIFICATION_URL'] = 'https://aurea-ai-ftqa.onrender.com/webhooks/pagseguro'

def test_pix_generation():
    print("Iniciando teste de geração de PIX PagSeguro Sandbox...")
    
    # Dados de teste
    amount = 1000 # R$ 10,00
    customer_name = "Teste Usuario"
    customer_email = "teste@exemplo.com"
    customer_tax_id = "12345678909" # CPF Falso para teste
    reference_id = "TEST-REF-123"
    
    # O serviço precisa ser reinicializado pois as envs foram setadas agora
    from services.pagseguro_service import PagSeguroService
    test_service = PagSeguroService()
    
    result = test_service.create_pix_order(
        amount_cents=amount,
        customer_name=customer_name,
        customer_email=customer_email,
        customer_tax_id=customer_tax_id,
        reference_id=reference_id
    )
    
    if result:
        print("\n✅ SUCESSO!")
        print(f"Order ID: {result.get('order_id')}")
        print(f"QR Code Text: {result.get('qr_code_text')[:50]}...")
        print(f"QR Code Image URL: {result.get('qr_code_image')}")
    else:
        print("\n❌ FALHA na geração do PIX. Verifique os logs.")

if __name__ == "__main__":
    test_pix_generation()
