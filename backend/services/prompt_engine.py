"""
Prompt Engine — Otimizado para openai/gpt-image-2 (iPhone 17 Pro Max estética)
================================================================================
Modelo recebe `input_images` com as 3 fotos de referência.
Prompts minimalistas, realistas, sem overcontrol.
"""
import logging
from typing import Optional, Literal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
# IDENTITY ANCHOR (forte, mas conciso)
# ══════════════════════════════════════════════════════════════
IDENTITY_ANCHOR = (
    "The client has uploaded 3 reference photos of herself. "
    "Preserve the identity of this exact person – same face, bone structure, "
    "eyes, nose, lips, skin tone, and hairline. "
    "Do not beautify, idealize, or alter facial features. "
    "Do not change ethnicity, age, or apply symmetry corrections. "
    "Identity preservation takes priority over stylistic choices."
)

# ══════════════════════════════════════════════════════════════
# IPHONE 17 PRO MAX PHOTOGRAPHY (estética de celular)
# ══════════════════════════════════════════════════════════════
IPHONE_PHOTOGRAPHY = (
    "Shot on iPhone 17 Pro Max. Computational photography style: "
    "natural skin texture with subtle smoothing, realistic HDR, "
    "gentle depth-of-field (bokeh), no artificial sharpening, "
    "true-to-life colors, balanced exposure, natural highlights and shadows. "
    "Looks like a real photo taken with a high‑end smartphone."
)

# ══════════════════════════════════════════════════════════════
# LENS PRESETS (simples)
# ══════════════════════════════════════════════════════════════
LENS_PRESETS = {
    "portrait": "50mm portrait lens aesthetic.",
    "cinematic": "85mm cinematic portrait lens aesthetic.",
    "documentary": "35mm documentary photography aesthetic.",
}

# ══════════════════════════════════════════════════════════════
# BASE REALISM & GUARDRAILS
# ══════════════════════════════════════════════════════════════
BASE_REALISM = (
    "Real professional maternity photography. "
    "The pregnant belly is naturally visible and central to the composition. "
    "Authentic emotional expression, natural body proportions. "
    "Real skin texture visible. Soft natural lighting. "
    "Feels like a real captured moment, not an AI render."
)

REALISM_GUARDRAILS = (
    "Avoid CGI appearance, beauty filter aesthetics, or over-retouched skin. "
    "Looks indistinguishable from a real maternity photoshoot."
)

# ══════════════════════════════════════════════════════════════
# SKIN & MAKEUP — VERSÃO EXTREMAMENTE SIMPLES (sem overcontrol)
# ══════════════════════════════════════════════════════════════
SKIN_MAKEUP_NATURAL = (
    "Minimal natural makeup. Healthy natural skin. Real skin texture preserved."
)

SKIN_MAKEUP_EDITORIAL = (
    "Soft polished makeup with natural texture preserved. Minimal elegance, no heavy retouching."
)

# ══════════════════════════════════════════════════════════════
# NATURALNESS BOOSTER (apenas glow suave, sem exageros)
# ══════════════════════════════════════════════════════════════
NATURALNESS_BOOSTER = (
    "Healthy pregnancy glow – soft natural warmth, gentle relaxed expression, "
    "real fabric behavior, authentic smile."
)

# ══════════════════════════════════════════════════════════════
# EXPRESSIONS — VERSÃO CANDID (natural, não posada)
# ══════════════════════════════════════════════════════════════
EXPRESSION_LIBRARY = {
    "warm": "Expression feels candid and emotionally genuine, as if captured naturally between poses.",
    "neutral": "Calm neutral expression, relaxed face, authentic.",
    "editorial": "Soft introspective expression with natural emotional depth.",
}

# ══════════════════════════════════════════════════════════════
# POSE LIBRARY (simples, sem over‑description)
# ══════════════════════════════════════════════════════════════
POSE_LIBRARY = {
    "front_cradle": "Facing camera, both hands gently resting on the belly. Natural relaxed posture.",
    "walking": "Captured mid-step during a slow relaxed walk.",
    "window_light": "Standing near a large window with relaxed posture, gently touching the belly.",
    "looking_down": "Looking softly down toward the belly with natural emotional connection.",
}

# ══════════════════════════════════════════════════════════════
# FRAMING (enxuto)
# ══════════════════════════════════════════════════════════════
FRAMING_VARIANTS = {
    "full_body": "Full body composition, natural proportions.",
    "three_quarters": "Three-quarter framing emphasizing the belly naturally.",
    "medium": "Medium portrait, emotional connection.",
    "close_up_emotional": "Close emotional portrait, shallow depth of field.",
    "detail_hands_belly": "Intimate detail of hands resting on the belly.",
}

# ══════════════════════════════════════════════════════════════
# STYLE PRESETS — com iluminação genérica (soft directional)
# ══════════════════════════════════════════════════════════════
STYLE_PRESETS = {
    "classic": {
        "name": "Clássico",
        "prompt": (
            "Classic maternity studio portrait. "
            "Soft directional studio lighting, neutral background. "
            "She wears a simple flowing white or cream dress."
        ),
    },
    "luxury_studio": {
        "name": "Estúdio Luxo",
        "prompt": (
            "Luxury studio maternity portrait. "
            "Soft directional studio lighting with gentle rim glow. "
            "She wears a flowing ivory silk gown. Warm neutral tones."
        ),
    },
    "ivory_satin": {
        "name": "Cetim Imperial",
        "prompt": (
            "Elegant luxury studio portrait. "
            "She wears an ivory satin backless gown. "
            "Soft cinematic lighting, refined shadows."
        ),
    },
    "black_white_editorial": {
        "name": "Preto & Branco Editorial",
        "prompt": (
            "Elegant black and white maternity portrait. "
            "Soft directional lighting, rich tonal range. "
            "Clean minimalist background, timeless monochrome."
        ),
    },
    "dramatic_black_gown": {
        "name": "Vestido Preto Dramático",
        "prompt": (
            "Dramatic black and white fine art portrait. "
            "She wears a stunning black gown. "
            "Strong chiaroscuro lighting, minimalist composition."
        ),
    },
    "golden_hour_nature": {
        "name": "Pôr do Sol na Natureza",
        "prompt": (
            "Outdoor maternity portrait in a wildflower meadow during sunset. "
            "Warm golden backlight, soft bokeh, wind movement. "
            "Dewy natural glow."
        ),
    },
    "boho_chic": {
        "name": "Boho Chic",
        "prompt": (
            "Bohemian maternity portrait. "
            "Large window natural light, dried floral accents, earth tones. "
            "Soft painterly light, intimate atmosphere."
        ),
    },
    "taupe_wings": {
        "name": "Asas de Chiffon Nude",
        "prompt": (
            "Ethereal studio portrait. "
            "She wears a deep taupe-nude chiffon gown with wide fabric panels. "
            "Soft overhead light, gentle shadow roll-off."
        ),
    },
    "red_lotus": {
        "name": "Lótus Vermelho",
        "prompt": (
            "Cozy holiday maternity portrait. "
            "Lotus position on white sofa, red silk pajamas, popcorn box. "
            "On-axis ring flash plus warm Christmas tree lights, dark lounge setting."
        ),
    },
}

# ══════════════════════════════════════════════════════════════
# NEGATIVE PROMPT (mantido)
# ══════════════════════════════════════════════════════════════
NEGATIVE_PROMPT = (
    "cartoon, anime, 3d render, cgi, illustration, painting, drawing, sketch, digital art, "
    "airbrushed skin, plastic texture, fake skin, over-smoothed, porcelain doll, wax figure, "
    "bad anatomy, extra fingers, distorted belly, floating hands, "
    "harsh shadows, neon colors, oversaturated, over-sharpened, HDR artifacts, "
    "watermark, text, logo, selfie angle, fisheye, on-camera flash, "
    "stiff mannequin pose, generic beauty filter, excessive retouching, "
    "uncanny valley, dead eyes, visible AI artifacts, "
    "face mismatch, identity drift, different person, swapped identity, "
    "overly shiny skin, oily T-zone, plastic texture, wax face."
)

# ══════════════════════════════════════════════════════════════
# PROMPT GENERATOR
# ══════════════════════════════════════════════════════════════
def generate_prompt(
    tipo_ensaio: str,
    subject_description: str = "",
    framing: Literal["full_body", "three_quarters", "medium", "close_up_emotional", "detail_hands_belly"] = "full_body",
    use_naturalness_booster: Optional[bool] = None,
    use_identity_text: bool = True,
    pose_key: str = "front_cradle",
    expression_key: str = "warm",
    lens_type: str = "portrait",
) -> str:
    # Determina uso do naturalness booster
    no_booster_styles = ["black_white_editorial", "dramatic_black_gown"]
    if use_naturalness_booster is None:
        use_naturalness_booster = tipo_ensaio not in no_booster_styles

    preset = STYLE_PRESETS.get(tipo_ensaio)
    if not preset:
        logger.warning(f"Unknown style: {tipo_ensaio}")
        style_prompt = "Real professional maternity photography."
    else:
        style_prompt = preset["prompt"]

    parts = []

    if use_identity_text:
        parts.append(IDENTITY_ANCHOR)

    parts.append(style_prompt)
    parts.append(FRAMING_VARIANTS.get(framing, FRAMING_VARIANTS["full_body"]))
    parts.append(POSE_LIBRARY.get(pose_key, POSE_LIBRARY["front_cradle"]))
    parts.append(EXPRESSION_LIBRARY.get(expression_key, EXPRESSION_LIBRARY["warm"]))

    if subject_description:
        parts.append(f"Subject details: {subject_description}")

    parts.append(IPHONE_PHOTOGRAPHY)
    parts.append(LENS_PRESETS.get(lens_type, LENS_PRESETS["portrait"]))

    # Pele/maquiagem
    editorial_skin_styles = ["black_white_editorial", "dramatic_black_gown", "ivory_satin"]
    if tipo_ensaio in editorial_skin_styles:
        parts.append(SKIN_MAKEUP_EDITORIAL)
    else:
        parts.append(SKIN_MAKEUP_NATURAL)

    if use_naturalness_booster:
        parts.append(NATURALNESS_BOOSTER)

    parts.append(BASE_REALISM)
    parts.append(REALISM_GUARDRAILS)

    final_prompt = " ".join(parts)
    logger.info(f"Prompt generated: {tipo_ensaio} ({len(final_prompt)} chars)")
    return final_prompt

def generate_negative_prompt() -> str:
    return NEGATIVE_PROMPT

def get_available_styles() -> list:
    return [{"id": k, "name": v["name"]} for k, v in STYLE_PRESETS.items()]

def get_framing_options() -> list:
    return [{"id": k, "name": k.replace("_", " ").title()} for k in FRAMING_VARIANTS]

if __name__ == "__main__":
    prompt = generate_prompt("luxury_studio", "Mulher de pele morena, cabelos cacheados", lens_type="cinematic")
    print("\n--- POSITIVE PROMPT ---\n", prompt)
    print("\n--- NEGATIVE PROMPT ---\n", generate_negative_prompt())