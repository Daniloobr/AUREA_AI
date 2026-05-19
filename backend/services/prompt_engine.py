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
    "Shot on medium format digital camera (80mm equivalent), aperture f/2.8, shallow depth of field. "
    "Sharp focus on eyes and belly. Natural perspective compression, no wide-angle distortion. "
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
# POSE LIBRARY & EXPRESSION LIBRARY
# ══════════════════════════════════════════════════════════════
POSE_LIBRARY = {
    "elegant_profile": "Three-quarter profile, body turned 30 degrees away from camera, one hand gently under the belly, other hand relaxed at side, chin slightly lowered.",
    "front_cradle": "Facing camera, both hands gently cradling the belly, shoulders relaxed, soft confident posture.",
    "editorial_side": "Full side profile emphasizing the belly silhouette, elongated posture, strong editorial presence.",
}

EXPRESSION_LIBRARY = {
    "warm": "gentle natural smile, warmth in the eyes",
    "neutral": "calm neutral expression, relaxed face",
    "editorial": "serious, introspective, powerful expression",
}

# Estilos editoriais/dramáticos que não devem usar NATURALNESS_BOOSTER por padrão
NO_BOOSTER_STYLES = ["black_white_editorial", "dramatic_black_gown"]

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
# ══════════════════════════════════════════════════════════════
STYLE_PRESETS = {
    "classic": {
        "name": "Clássico",
        "category": "Clássico",
        "description": "Estúdio minimalista com iluminação suave e fundo neutro, destacando a beleza natural da gestação. Elegante e atemporal.",
        "cover": "/thumbnails/classic.png",
        "prompt": (
            "A classic maternity studio portrait of a pregnant woman. "
            "Two large softboxes at 45 degrees camera-left and camera-right, equal intensity, creating soft even studio lighting with minimal shadows, set against a neutral warm-toned backdrop. "
            "Elegant and timeless composition, natural colors. "
            "She wears a simple flowing white or cream dress that drapes naturally over the belly."
        ),
    },
    "luxury_studio": {
        "name": "Estúdio Luxo",
        "category": "Clássico",
        "description": "Fundo cinza-pomba com iluminação de contorno que realça a silhueta, transmitindo sofisticação e alta costura.",
        "cover": "/thumbnails/luxury_studio.png",
        "prompt": (
            "A luxury studio maternity portrait of a pregnant woman. "
            "Seamless dove-gray paper backdrop with subtle gradient falloff. "
            "Single key light at 45 degrees, large octabox with medium diffusion, fill reflector at 30 degrees, backlight at 135 degrees, low intensity, creating gentle rim glow along the belly curve and shoulders. "
            "She wears a flowing ivory silk gown with natural luster and subtle translucency over the belly. "
            "Warm neutral color palette: cream, taupe, champagne. "
            "Elegant composition with generous negative space."
        ),
    },
    "ivory_satin": {
        "name": "Cetim Imperial",
        "category": "Vogue Style",
        "description": "Vestido de cetim marfim sem costas, cauda longa sobre piso polido e iluminação lateral cinematográfica que cria sombras refinadas.",
        "cover": "/thumbnails/image3.png",
        "prompt": (
            "An elegant and luxurious studio maternity portrait of a pregnant woman. "
            "She wears a sophisticated ivory satin backless gown with a long flowing train pooling gracefully on a polished neutral studio floor. "
            "Key light at 45 degrees camera-left, 30-degree grid, no fill, dark environment, casting refined chiaroscuro shadows across her body, accentuating the natural pregnancy curve. "
            "Warm monochromatic tones and a high-fashion Vogue-style composition."
        ),
    },
    "black_white_editorial": {
        "name": "Preto & Branco Editorial",
        "category": "Vogue Style",
        "description": "Alto contraste com sombras suaves esculpindo a silhueta, evocando o visual de uma revista de moda em preto e branco.",
        "cover": "/thumbnails/black_white_editorial.png",
        "prompt": (
            "An elegant black and white maternity portrait of a pregnant woman. "
            "Key light at 45 degrees camera-left, large softbox with grid, shadow fill reflector at 45 degrees camera-right at 10% intensity, sculpting the face and belly curve with gentle shadows. "
            "Rich tonal range from deep blacks to clean whites. "
            "She wears a simple elegant dark outfit that drapes beautifully over the belly. "
            "Clean minimalist background for figure-ground separation. "
            "Timeless monochrome aesthetic with subtle film grain and natural contrast."
        ),
    },
    "dramatic_black_gown": {
        "name": "Vestido Preto Dramático",
        "category": "Especial",
        "description": "Iluminação lateral Chiaroscuro destaca um vestido preto sem costas, com cauda longa sobre piso escuro polido.",
        "cover": "/thumbnails/vestidoBlack.png",
        "prompt": (
            "A dramatic black and white fine art maternity portrait of a pregnant woman. "
            "She wears a stunning backless black gown with a long dramatic train pooling on a polished dark studio floor. "
            "Key light at 90 degrees camera-left, bare bulb with snoot, dark environment with no fill, sculpting her silhouette and creating strong, high-contrast chiaroscuro shadows that elegantly highlight the curve of her belly and back. "
            "Minimalist and powerful Vogue-style composition."
        ),
    },
    "golden_hour_nature": {
        "name": "Pôr do Sol na Natureza",
        "category": "Natureza",
        "description": "Campo aberto de flores silvestres iluminadas pela luz dourada do fim de tarde, criando aura mágica ao redor da gestante.",
        "cover": "/thumbnails/golden_hour_nature.png",
        "prompt": (
            "An outdoor maternity portrait of a pregnant woman. "
            "Open wildflower meadow during sunset. "
            "Natural sunlight at low angle, backlight at 135 degrees, warm amber gel effect, intensity 30% of key light, creating a luminous halo around the hair and a gentle glow through her flowing dress in dusty rose. "
            "Soft bokeh from wildflowers in the foreground and background. "
            "Wind softly moving the dress and hair, warm golden skin tones, lifted shadows, natural greens."
        ),
    },
    "boho_chic": {
        "name": "Boho Chic",
        "category": "Artístico",
        "description": "Luz natural de janela filtrada sobre cenário rústico de capim dos pampas, com tons terrosos que transmitam aconchego.",
        "cover": "/thumbnails/boho_chic.png",
        "prompt": (
            "A bohemian maternity portrait of a pregnant woman. "
            "Large window light at 90 degrees camera-left, double-diffused through sheer curtains, white bounce card at 45 degrees camera-right, creating soft diffused illumination. "
            "Dried floral accents: pampas grass and soft blush tones in the scene. "
            "She wears a flowing earth-toned outfit with the pregnant belly visible. "
            "Delicate accessories: a simple flower crown or gold accents. "
            "Muted earthy palette: warm sand, terracotta, sage green, dusty pink. "
            "Soft painterly quality to the light, intimate and warm atmosphere."
        ),
    },
    "taupe_wings": {
        "name": "Asas de Chiffon Nude",
        "category": "Artístico",
        "description": "Chiffon nude escuro forma asas ao vento, sobre fundo cinza iluminado suavemente.",
        "cover": "/thumbnails/image2.png",
        "prompt": (
            "An ethereal and artistic studio maternity portrait of a pregnant woman. "
            "She is dressed in a luxurious deep taupe-nude chiffon gown, with two wide fabric panels elegantly extended in mid-air on both sides in a natural wing-like shape. "
            "Key light from an elevated large softbox at 45 degrees overhead, with a silver reflector below at 30 degrees, creating gentle, gradual shadow roll-off, set against a warm gray studio background."
        ),
    },
    "red_lotus": {
        "name": "Lótus Vermelho",
        "category": "Especial",
        "description": "Ensaio natalino com pose de lótus em sofá branco, usando pijama de seda vermelho e balde de pipoca.",
        "cover": "/thumbnails/image.png",
        "prompt": (
            "A warm and cozy holiday maternity portrait of a pregnant woman. "
            "She is sitting in a relaxed lotus position on a comfortable white sofa, wearing soft red silk pajamas with her pregnant belly exposed. "
            "She holds a classic red and white striped popcorn box in one hand, smiling gently while eating with the other. "
            "Her hair is styled in a casual, elegant bun with two soft strands framing her face. "
            "On-axis ring flash at low intensity, combined with ambient warm light from a decorated Christmas tree at 135 degrees behind the sofa, creating a warm glowing edge on an atmospheric dark lounge setting. "
            "Intimate, authentic holiday mood."
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
    "nudity, nsfw, inappropriate content, suggestive pose, "
    "face mismatch, identity drift, different person, altered facial structure, swapped identity, generic face, not the same person."
)

# ══════════════════════════════════════════════════════════════
# FUNÇÕES PRINCIPAIS
# ══════════════════════════════════════════════════════════════

def generate_prompt(
    tipo_ensaio: str,
    subject_description: str = "",
    framing: Literal["full_body", "three_quarters", "medium", "close_up_emotional", "detail_hands_belly"] = "full_body",
    use_naturalness_booster: Optional[bool] = None,
    use_identity_text: bool = True,
    pose_key: str = "front_cradle",
    expression_key: str = "warm"
) -> str:
    """
    Gera um prompt completo e otimizado para openai/gpt-image-2.
    
    Ordem dos componentes:
    1. IDENTITY_ANCHOR — preservação de identidade
    2. Prompt do estilo (scene_prompt)
    3. Enquadramento (framing)
    4. Pose (POSE_LIBRARY)
    5. Expressão (EXPRESSION_LIBRARY)
    6. Descrição física do sujeito (se fornecida)
    7. NATURALNESS_BOOSTER (condicional)
    8. QUALITY_CORE (com câmera)
    """
    
    # Determina o uso do naturalness booster se não for especificado explicitamente
    if use_naturalness_booster is None:
        use_naturalness_booster = tipo_ensaio not in NO_BOOSTER_STYLES

    preset = STYLE_PRESETS.get(tipo_ensaio)

    if not preset:
        logger.warning(f"Unknown tipo_ensaio: {tipo_ensaio}, using fallback")
        scene_prompt = (
            "A beautiful professional maternity portrait of a pregnant woman. "
            "Soft natural light, natural skin texture, authentic pregnancy glow. "
            "Premium photography, photorealistic, natural optical depth."
        )
    else:
        scene_prompt = preset["prompt"]

    parts = []

    if use_identity_text:
        parts.append(IDENTITY_ANCHOR)

    parts.append(scene_prompt)
    
    # Enquadramento (framing)
    parts.append(FRAMING_VARIANTS.get(framing, FRAMING_VARIANTS["full_body"]))
    
    # Pose (POSE_LIBRARY)
    pose_text = POSE_LIBRARY.get(pose_key, POSE_LIBRARY["front_cradle"])
    parts.append(pose_text)
    
    # Expressão (EXPRESSION_LIBRARY)
    expression_text = EXPRESSION_LIBRARY.get(expression_key, EXPRESSION_LIBRARY["warm"])
    parts.append(expression_text)

    # Detalhes adicionais do sujeito
    if subject_description:
        parts.append(f"Additional details about the subject: {subject_description}")

    # NATURALNESS_BOOSTER (condicional)
    if use_naturalness_booster:
        parts.append(NATURALNESS_BOOSTER)

    # QUALITY_CORE (com controle de câmera)
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
    """Retorna a lista de estilos disponíveis."""
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