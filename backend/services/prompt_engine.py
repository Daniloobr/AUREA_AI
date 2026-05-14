import logging
from typing import Optional, Literal

# Configuração de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
# IDENTITY PRESERVATION (REALISTA - via referência externa)
# ══════════════════════════════════════════════════════════════
IDENTITY_PRESERVATION = (
    "The face must be exactly the same as in the provided reference photo. "
    "Preserve facial structure, skin tone, eye shape, jawline, and all unique features. "
    "Same body morphology: shoulder width, natural proportions, authentic silhouette. "
    "The person should look like themselves, not like a generic model. "
)

# ══════════════════════════════════════════════════════════════
# NATURALNESS & TEXTURE BOOSTER (Imperfeições Orgânicas)
# ══════════════════════════════════════════════════════════════
NATURALNESS_BOOSTER = (
    "Hyper-realistic skin textures with visible pores, fine lines, and natural imperfections. "
    "Authentic candid feel, relaxed facial muscles, non-stiff posture. "
    "Subtle stray hairs, natural fabric drapes with real wrinkles and fibers. "
    "No plastic skin, no artificial smoothing, no over-sharpening. "
    "The person looks like a real human in a real moment, not a 3D render. "
)

# ══════════════════════════════════════════════════════════════
# LUXURY STUDIO CORE (Iluminação e Estética Fine Art)
# ══════════════════════════════════════════════════════════════
QUALITY_CORE = (
    "Shot on 35mm lens, f/2.8, professional studio lighting with softbox diffusion. "
    "Soft chiaroscuro effect, elegant highlights, and gentle shadows. "
    "Warm neutral color palette: cream, beige, champagne, and gold accents. "
    "Fine art photography style, clean composition, high-end editorial look. "
    "Subtle film grain, 8K resolution, incredibly detailed, masterpiece quality. "
)

# ══════════════════════════════════════════════════════════════
# FRAMING VARIANTS (Controle de enquadramento)
# ══════════════════════════════════════════════════════════════
FRAMING_VARIANTS = {
    "full_body": (
        "Camera at 4-5 meters distance, showing the entire body from head to toe. "
        "Full silhouette visible. Professional distance, no selfie distortion."
    ),
    "three_quarters": (
        "Camera at 3 meters distance, framing from mid-thigh up. "
        "Shows most of the body while allowing face detail."
    ),
    "medium": (
        "Camera at 2.5 meters distance, waist-up composition. "
        "Focus on upper body and expression, still showing context."
    ),
    "close_up_emotional": (
        "Camera at 1.5 meters distance, chest-up framing. "
        "Shows facial expression and shoulders. No selfie angle."
    ),
    "detail_hands_belly": (
        "Close but natural detail of hands, belly, or interaction. "
        "Shallow depth of field, intimate but not invasive."
    ),
}

# ══════════════════════════════════════════════════════════════
# STYLE PRESETS (NOVOS PROMPTS FORNECIDOS PELO USUÁRIO)
# ══════════════════════════════════════════════════════════════
STYLE_PRESETS = {
    "luxury_studio": {
        "name": "Luxury Studio",
        "category": "Clássico",
        "description": "Fundo neutro, iluminação de estúdio profissional e elegância atemporal.",
        "cover": "https://images.unsplash.com/photo-1544126592-807daa2b565b?auto=format&fit=crop&q=80&w=600",
        "prompt": (
            "Professional high-end luxury studio maternity photography. Neutral background, "
            "soft professional studio lighting, fine art style. Neutral color palette: cream, beige. "
            "Clean composition, elegant shadows. 8k resolution, masterpiece."
        ),
    },
    "golden_hour_nature": {
        "name": "Golden Hour Nature",
        "category": "Natureza",
        "description": "Campo aberto com a luz mágica do pôr do sol.",
        "cover": "https://images.unsplash.com/photo-1594434296621-507bc67a78c1?auto=format&fit=crop&q=80&w=600",
        "prompt": (
            "Maternity photography in an open field during golden hour. Warm magical sunset light, "
            "lens flare, soft bokeh. Natural environment, peaceful and serene atmosphere. "
            "Highly detailed, cinematic lighting, professional outdoor shoot."
        ),
    },
    "boho_chic": {
        "name": "Boho Chic",
        "category": "Artístico",
        "description": "Decoração rústica, flores secas e tons pastéis.",
        "cover": "https://images.unsplash.com/photo-1583939003579-730e3918a45a?auto=format&fit=crop&q=80&w=600",
        "prompt": (
            "Boho chic style maternity photography. Rustic decoration, dried flowers, pampas grass. "
            "Pastel color palette, soft natural textures. Warm and cozy atmosphere. "
            "Bohemian aesthetic, artistic and delicate. High resolution."
        ),
    },
    "black_white_editorial": {
        "name": "Black & White Editorial",
        "category": "Vogue Style",
        "description": "Alto contraste, estilo revista de moda.",
        "cover": "https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&q=80&w=600",
        "prompt": (
            "High-contrast black and white editorial maternity photography. Fashion magazine style, "
            "Rembrandt lighting, dramatic shadows. Strong silhouette, elegant and powerful. "
            "Minimalist background, grain texture, iconic look. Masterpiece."
        ),
    },
}

# ══════════════════════════════════════════════════════════════
# NEGATIVE PROMPT (Filtro Anti-IA e Anti-Retoque)
# ══════════════════════════════════════════════════════════════
NEGATIVE_PROMPT = (
    "cartoon, anime, 3d render, cgi, illustration, painting, drawing, sketch, "
    "airbrushed skin, plastic texture, fake skin, over-smoothed, "
    "bad anatomy, deformed limbs, extra fingers, mutated hands, "
    "harsh shadows, neon colors, oversaturated, over-sharpened, "
    "low resolution, blurry, out of focus, watermark, text, logo, "
    "selfie style, wide angle distortion, cheap studio look, "
    "stiff mannequin pose, generic beauty filter, excessive retouching, "
    "perfectly symmetrical face, doll-like features."
)

# ══════════════════════════════════════════════════════════════
# FUNÇÕES PRINCIPAIS
# ══════════════════════════════════════════════════════════════

def generate_prompt(
    tipo_ensaio: str,
    subject_description: str = "",
    framing: Literal["full_body", "three_quarters", "medium", "close_up_emotional", "detail_hands_belly"] = "full_body",
    use_naturalness_booster: bool = True,
    use_identity_text: bool = True
) -> str:
    """Gera um prompt completo e otimizado para ensaios fotográficos realistas."""
    
    preset = STYLE_PRESETS.get(tipo_ensaio)

    if not preset:
        logger.warning(f"Unknown tipo_ensaio: {tipo_ensaio}, using fallback")
        scene_prompt = "Professional but natural portrait photography. Soft natural light, real skin texture."
    else:
        scene_prompt = preset["prompt"]

    parts = []

    # 1. Identidade (Reflexo da referência)
    if use_identity_text:
        parts.append(IDENTITY_PRESERVATION)

    # 2. Enquadramento
    parts.append(FRAMING_VARIANTS.get(framing, FRAMING_VARIANTS["full_body"]))

    # 3. Cena principal
    parts.append(scene_prompt)

    # 4. Descrição do sujeito
    if subject_description:
        parts.append(subject_description)

    # 5. Naturalidade (Boost de texturas)
    if use_naturalness_booster:
        parts.append(NATURALNESS_BOOSTER)

    # 6. Qualidade de Estúdio (Core)
    parts.append(QUALITY_CORE)

    final_prompt = " ".join(parts)
    logger.info(f"Prompt gerado com sucesso para o estilo: {tipo_ensaio}")
    return final_prompt

def generate_negative_prompt() -> str:
    """Retorna o negative prompt universal."""
    return NEGATIVE_PROMPT

# ══════════════════════════════════════════════════════════════
# FUNÇÕES DE UTILIDADE PARA FRONTEND / INTERFACE
# ══════════════════════════════════════════════════════════════

def get_available_styles() -> list:
    """
    Retorna a lista de estilos disponíveis com nomes amigáveis 
    para preencher menus de seleção no frontend.
    """
    return [
        {
            "id": key, 
            "name": val["name"],
            "category": val.get("category", "General"),
            "description": val.get("description", ""),
            "cover": val.get("cover", "")
        }
        for key, val in STYLE_PRESETS.items()
    ]

def get_framing_options() -> list:
    """
    Retorna as opções de enquadramento disponíveis para o usuário escolher.
    """
    return [
        {
            "id": key, 
            "name": key.replace("_", " ").title(), 
            "description": val.split(".")[0] # Pega apenas a primeira frase da descrição técnica
        }
        for key, val in FRAMING_VARIANTS.items()
    ]

# ══════════════════════════════════════════════════════════════
# EXEMPLO DE EXECUÇÃO
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Exemplo: Gerando um ensaio do primeiro estilo (campo de trigo)
    meu_prompt = generate_prompt(
        tipo_ensaio="gestante_campo_trigo",
        subject_description="",
        framing="full_body"
    )
    
    print("--- POSITIVE PROMPT ---")
    print(meu_prompt)
    print("\n--- NEGATIVE PROMPT ---")
    print(generate_negative_prompt())

    # Listagem de estilos disponíveis
    print("\nESTILOS DISPONÍVEIS NO SISTEMA:")
    for style in get_available_styles():
        print(f"- {style['name']} (ID: {style['id']})")
        
    print("\n" + "="*80)