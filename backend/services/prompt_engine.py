"""
Prompt Engine — Otimizado para google/nano-banana-pro
=====================================================
Este modelo recebe `image_input` com as 3 fotos de referência
do cliente e preserva a identidade facial na imagem gerada.
O prompt textual serve como guia de estilo, enquadramento e qualidade.
"""
import logging
from typing import Optional, Literal

# Configuração de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
# IDENTITY ANCHOR — google/nano-banana-pro
# ══════════════════════════════════════════════════════════════
IDENTITY_ANCHOR = (
    "The client has uploaded 3 reference photos of herself. "
    "Preserve the identity of this exact person in the generated image. "
    "Use the same face from the reference photos — same bone structure, "
    "same eyes, nose, lips, skin tone, and hairline. "
    "Do not beautify, idealize, or alter facial features. "
    "Do not change ethnicity, age, or apply symmetry corrections. "
    "Identity preservation takes priority over stylistic choices. "
    "The body should look natural and consistent with a pregnant woman."
)

# ══════════════════════════════════════════════════════════════
# QUALITY CORE — premium photography aesthetic
# ══════════════════════════════════════════════════════════════
QUALITY_CORE = (
    "Premium modern photography aesthetic with natural optical depth. "
    "Photorealistic, authentic skin texture, natural pores, soft tonal variation. "
    "Natural computational bokeh, realistic highlight roll-off, gentle shadow transitions. "
    "No beauty filter, no artificial smoothing, no porcelain-doll skin. "
    "True-to-life white balance, natural color science, elegant composition."
)

# ══════════════════════════════════════════════════════════════
# NATURALNESS BOOSTER (Realismo Orgânico)
# ══════════════════════════════════════════════════════════════
NATURALNESS_BOOSTER = (
    "Authentic pregnancy glow — soft luminous skin with gentle natural warmth. "
    "Natural skin texture, realistic pores, soft tonal variation across the belly. "
    "Real fabric behavior: gravity-correct draping, natural creases where fabric meets skin. "
    "Genuine relaxed expression — soft natural smile, real warmth in the eyes. "
    "Hands with real detail, natural nail beds, relaxed fingers cradling the belly."
)

# ══════════════════════════════════════════════════════════════
# FRAMING VARIANTS
# ══════════════════════════════════════════════════════════════
FRAMING_VARIANTS = {
    "full_body": (
        "Full-length composition, subject centered with breathing room above the head and below the feet. "
        "Full pregnant silhouette visible from crown to toes, slight three-quarter body angle "
        "to accentuate the belly curve. Natural body proportions preserved."
    ),
    "three_quarters": (
        "Three-quarter composition, framing from mid-thigh to just above the head. "
        "Slight low camera angle at belly height to emphasize the maternal silhouette. "
        "Subject turned 30-40 degrees from camera with face toward lens. "
        "Belly prominently featured in the mid-frame with hands naturally resting on it."
    ),
    "medium": (
        "Medium shot, waist-up composition with the belly curve as the visual anchor. "
        "Tight enough to capture the emotion in the eyes while showing the cradling gesture. "
        "Shallow depth of field, attention drawn to face and hands on belly."
    ),
    "close_up_emotional": (
        "Intimate chest-up portrait, face fills the upper frame. "
        "Soft focus on the shoulder and collarbone area. "
        "Catchlights visible in the eyes, gentle downward gaze toward the belly. "
        "Tender and warm expression, never posed or stiff."
    ),
    "detail_hands_belly": (
        "Intimate detail shot focused on hands cradling the pregnant belly. "
        "Fingers sharp, belly skin with soft natural texture. "
        "Natural nail detail, gentle finger placement. "
        "Soft rim light, tender and reverent mood."
    ),
}

# ══════════════════════════════════════════════════════════════
# STYLE PRESETS — Otimizados para google/nano-banana-pro
# (Apenas 5 estilos mantidos)
# ══════════════════════════════════════════════════════════════
STYLE_PRESETS = {
    "luxury_studio": {
        "name": "Luxury Studio",
        "category": "Clássico",
        "description": "Fundo neutro, iluminação de estúdio profissional e elegância atemporal.",
        "cover": "https://images.unsplash.com/photo-1544126592-807daa2b565b?auto=format&fit=crop&q=80&w=600",
        "prompt": (
            "A luxury studio maternity portrait of a pregnant woman — "
            "the same woman from the 3 reference photos the client uploaded. "
            "Seamless dove-gray paper backdrop with subtle gradient falloff. "
            "Soft clamshell lighting with gentle rim glow along the belly curve and shoulders. "
            "She wears a flowing ivory silk gown with natural luster and subtle translucency over the belly. "
            "Hands gently cradling the lower belly, fingers relaxed. "
            "Warm neutral color palette: cream, taupe, champagne. "
            "Elegant composition with generous negative space. "
            "Premium photography, photorealistic, natural optical depth."
        ),
    },
    "golden_hour_nature": {
        "name": "Golden Hour Nature",
        "category": "Natureza",
        "description": "Campo aberto com a luz mágica do pôr do sol.",
        "cover": "https://images.unsplash.com/photo-1594434296621-507bc67a78c1?auto=format&fit=crop&q=80&w=600",
        "prompt": (
            "An outdoor maternity portrait of a pregnant woman — "
            "the same woman from the 3 reference photos the client uploaded. "
            "Open wildflower meadow during golden hour. "
            "Warm amber backlight creating a luminous halo around the hair "
            "and a gentle glow through her flowing dress in dusty rose. "
            "Soft bokeh from wildflowers in the foreground and background. "
            "Relaxed pose, one hand beneath the belly, wind softly moving the dress and hair. "
            "Warm golden skin tones, lifted shadows, natural greens. "
            "Premium photography, photorealistic, natural optical depth."
        ),
    },
    "boho_chic": {
        "name": "Boho Chic",
        "category": "Artístico",
        "description": "Decoração rústica, flores secas e tons pastéis.",
        "cover": "https://images.unsplash.com/photo-1583939003579-730e3918a45a?auto=format&fit=crop&q=80&w=600",
        "prompt": (
            "A bohemian maternity portrait of a pregnant woman — "
            "the same woman from the 3 reference photos the client uploaded. "
            "Warm natural window light through sheer curtains, soft diffused illumination. "
            "Dried floral accents: pampas grass and soft blush tones in the scene. "
            "She wears a flowing earth-toned outfit with the pregnant belly visible. "
            "Delicate accessories: a simple flower crown or gold accents. "
            "Muted earthy palette: warm sand, terracotta, sage green, dusty pink. "
            "Soft painterly quality to the light, intimate and warm atmosphere. "
            "Premium photography, photorealistic, natural optical depth."
        ),
    },
    "black_white_editorial": {
        "name": "Black & White Editorial",
        "category": "Vogue Style",
        "description": "Alto contraste, estilo elegante em preto e branco.",
        "cover": "https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&q=80&w=600",
        "prompt": (
            "An elegant black and white maternity portrait of a pregnant woman — "
            "the same woman from the 3 reference photos the client uploaded. "
            "Soft directional lighting sculpting the face and belly curve with gentle shadows. "
            "Rich tonal range from deep blacks to clean whites. "
            "She wears a simple elegant dark outfit that drapes beautifully over the belly. "
            "Graceful pose — soft expression, one hand gently on the belly, serene and maternal. "
            "Clean minimalist background for figure-ground separation. "
            "Timeless monochrome aesthetic with subtle film grain and natural contrast. "
            "Premium photography, photorealistic, natural optical depth."
        ),
    },
    "classic": {
        "name": "Clássico",
        "category": "Clássico",
        "description": "Estilo clássico com iluminação suave e cenário neutro.",
        "cover": "https://picsum.photos/seed/classic/600/800",
        "prompt": (
            "A classic maternity studio portrait of a pregnant woman — "
            "the same woman from the 3 reference photos the client uploaded. "
            "Soft even studio lighting, neutral warm-toned backdrop. "
            "Elegant and timeless composition, natural colors, gentle expression. "
            "She wears a simple flowing white or cream dress that drapes naturally over the belly. "
            "Hands cradling the belly, relaxed shoulders, warm genuine smile. "
            "Natural skin texture, authentic pregnancy glow. "
            "Premium photography, photorealistic, natural optical depth."
        ),
    },
    "red_lotus": {
        "name": "Lótus Vermelho",
        "category": "Especial",
        "description": "Clima natalino, sofá branco, pijama vermelho e pipoca – uma pose aconchegante e divertida.",
        "cover": "https://picsum.photos/seed/red_lotus/600/800",
        "prompt": (
            "A warm and cozy holiday maternity portrait of a pregnant woman — "
            "the same woman from the 3 reference photos the client uploaded. "
            "She is sitting in a relaxed lotus position on a comfortable white sofa, wearing soft red silk pajamas with her pregnant belly exposed. "
            "She holds a classic red and white striped popcorn box in one hand, smiling gently while eating with the other. "
            "Her hair is styled in a casual, elegant bun with two soft strands framing her face. "
            "Atmospheric dark lounge setting illuminated by a natural camera flash, "
            "with the warm glowing edge of a decorated Christmas tree softly blurred on the side. "
            "Intimate, authentic holiday mood. "
            "Premium photography, photorealistic, natural optical depth."
        ),
    },
}

# ══════════════════════════════════════════════════════════════
# NEGATIVE PROMPT — Otimizado para google/nano-banana-pro
# ══════════════════════════════════════════════════════════════
NEGATIVE_PROMPT = (
    "cartoon, anime, 3d render, cgi, illustration, painting, drawing, sketch, digital art, "
    "airbrushed skin, plastic texture, fake skin, over-smoothed, porcelain doll, wax figure, "
    "bad anatomy, deformed limbs, extra fingers, mutated hands, fused fingers, missing fingers, "
    "distorted belly, unrealistic pregnancy proportions, floating hands, disconnected limbs, "
    "harsh shadows, neon colors, oversaturated, over-sharpened, HDR artifacts, "
    "low resolution, blurry, out of focus, motion blur, jpeg artifacts, pixelated, "
    "watermark, text, logo, signature, copyright stamp, date stamp, "
    "selfie angle, wide angle distortion, fisheye, cheap studio look, on-camera flash, "
    "stiff mannequin pose, T-pose, generic beauty filter, excessive retouching, "
    "perfectly symmetrical face, doll-like features, uncanny valley, dead eyes, "
    "visible AI artifacts, seam lines, inconsistent lighting direction, "
    "stock photo aesthetic, clip art, "
    "nudity, nsfw, inappropriate content, suggestive pose."
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
    """
    Gera um prompt completo e otimizado para google/nano-banana-pro.
    
    Ordem dos componentes:
    1. IDENTITY_ANCHOR — preservação de identidade
    2. Prompt do estilo (scene_prompt)
    3. Enquadramento (framing)
    4. Descrição física do sujeito (se fornecida)
    5. NATURALNESS_BOOSTER
    6. QUALITY_CORE
    """
    
    preset = STYLE_PRESETS.get(tipo_ensaio)

    if not preset:
        logger.warning(f"Unknown tipo_ensaio: {tipo_ensaio}, using fallback")
        scene_prompt = (
            "A beautiful professional maternity portrait of a pregnant woman — "
            "the same woman from the 3 reference photos the client uploaded. "
            "Soft natural light, natural skin texture, authentic pregnancy glow. "
            "Premium photography, photorealistic, natural optical depth."
        )
    else:
        scene_prompt = preset["prompt"]

    parts = []

    if use_identity_text:
        parts.append(IDENTITY_ANCHOR)

    parts.append(scene_prompt)
    parts.append(FRAMING_VARIANTS.get(framing, FRAMING_VARIANTS["full_body"]))

    if subject_description:
        parts.append(f"Additional details about the subject: {subject_description}")

    if use_naturalness_booster:
        parts.append(NATURALNESS_BOOSTER)

    parts.append(QUALITY_CORE)

    final_prompt = " ".join(parts)
    logger.info(f"Prompt gerado com sucesso para o estilo: {tipo_ensaio} ({len(final_prompt)} chars)")
    return final_prompt

def generate_negative_prompt() -> str:
    return NEGATIVE_PROMPT

# ══════════════════════════════════════════════════════════════
# FUNÇÕES DE UTILIDADE
# ══════════════════════════════════════════════════════════════

def get_available_styles() -> list:
    """Retorna a lista de estilos disponíveis (apenas os 5 mantidos)."""
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
    return [
        {
            "id": key, 
            "name": key.replace("_", " ").title(), 
            "description": val.split(".")[0]
        }
        for key, val in FRAMING_VARIANTS.items()
    ]

# ══════════════════════════════════════════════════════════════
# EXEMPLO DE EXECUÇÃO
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    meu_prompt = generate_prompt(
        tipo_ensaio="luxury_studio",
        subject_description="Mulher de pele morena, cabelos cacheados escuros, olhos castanhos.",
        framing="full_body"
    )
    
    print("--- POSITIVE PROMPT ---")
    print(meu_prompt)
    print("\n--- NEGATIVE PROMPT ---")
    print(generate_negative_prompt())

    print("\nESTILOS DISPONÍVEIS:")
    for style in get_available_styles():
        print(f"- {style['name']} (ID: {style['id']})")
    print("\n" + "="*80)