import os
import sys
from pathlib import Path

# Adiciona o backend ao path
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

from config import Config
from services.replicate_service import generate_images
from services.prompt_engine import generate_prompt

def test_internal_gen():
    # Setup env
    os.environ["REPLICATE_API_TOKEN"] = Config.REPLICATE_API_TOKEN
    
    # Simula uma imagem de entrada (usando uma existente para teste se possível, ou apenas testando o fluxo)
    # Procuramos por qualquer imagem em uploads
    uploads_dir = Path(Config.UPLOAD_FOLDER)
    test_images = list(uploads_dir.glob("*.jpg")) + list(uploads_dir.glob("*.png"))
    
    if not test_images:
        print("Nenhuma imagem de teste encontrada em uploads. Por favor, faça um upload primeiro.")
        return

    image_path = str(test_images[0])
    print(f"Usando imagem de teste: {image_path}")
    
    prompt = generate_prompt("gestante_outdoor")
    print(f"Prompt gerado: {prompt[:100]}...")
    
    print("Iniciando geração real (Replicate)...")
    result = generate_images(
        image_path=image_path,
        prompt=prompt,
        negative_prompt="cartoon, anime, bad quality",
        id_weight=1.0
    )
    
    if result["success"]:
        print(f"SUCESSO! Imagens: {result['images']}")
    else:
        print(f"FALHA: {result['error']}")

if __name__ == "__main__":
    test_internal_gen()
