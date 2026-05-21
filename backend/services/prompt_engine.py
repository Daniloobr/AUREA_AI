"""
Prompt Engine — Maternity Photography (Realistic, Identity‑First)
Optimized for openai/gpt-image-2
===============================================================
Goal: Generate natural, authentic maternity portraits that preserve
the client's identity and look like real professional photography,
not AI renderings or heavy retouched montages.
"""

import logging
from typing import Optional, Literal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
# IDENTITY PRESERVATION (moved to the end – highest priority)
# ══════════════════════════════════════════════════════════════
IDENTITY_ANCHOR = (
    "CRITICAL: The client uploaded 3 reference photos. "
    "The generated image MUST show the exact same person – same face, "
    "same bone structure, same eyes, nose, lips, skin tone, hair. "
    "Do NOT change identity, do NOT beautify, do NOT idealize. "
    "Identity preservation is the most important instruction."
)

# ══════════════════════════════════════════════════════════════
# REALISM & AUTHENTICITY (no over-retouching)
# ══════════════════════════════════════════════════════════════
BASE_REALISM = (
    "Real maternity photography. Natural skin texture, "
    "authentic expression, believable body proportions. "
    "The pregnant belly is naturally visible. Looks like a real photo "
    "taken by a professional photographer, not an AI render."
)

# ══════════════════════════════════════════════════════════════
# LIGHTING & POSE (soft, natural)
# ══════════════════════════════════════════════════════════════
LIGHTING_GUIDELINES = (
    "Soft front or side-front lighting. Balanced exposure, "
    "no harsh shadows, no silhouette backlight."
)

POSE_GUIDELINES = (
    "Natural relaxed pose. Comfortable body language, "
    "hands gently resting on the belly. No stiff mannequin poses."
)

# ══════════════════════════════════════════════════════════════
# CAMERA AESTHETIC (professional, not overly technical)
# ══════════════════════════════════════════════════════════════
CAMERA_AESTHETIC = (
    "Professional full‑frame camera aesthetic. Natural depth of field, "
    "realistic colors, subtle contrast. Looks like a high‑end maternity session."
)

# ══════════════════════════════════════════════════════════════
# LENS PRESETS (simple, optional)
# ══════════════════════════════════════════════════════════════
LENS_PRESETS = {
    "portrait": "50mm portrait perspective, natural compression.",
    "cinematic": "85mm cinematic look, soft background separation.",
    "documentary": "35mm documentary style, environmental context.",
}

# ══════════════════════════════════════════════════════════════
# SKIN & MAKEUP (minimal, professional, no over‑retouching)
# ══════════════════════════════════════════════════════════════
SKIN_MAKEUP_NATURAL = (
    "Professional soft maternity makeup. Healthy natural skin. "
    "Real skin texture preserved. No heavy foundation, no artificial smoothing."
)

SKIN_MAKEUP_EDITORIAL = (
    "Soft polished makeup with natural texture preserved. "
    "Minimal elegance, no heavy retouching, real skin visible."
)

# ══════════════════════════════════════════════════════════════
# EXPRESSION & POSE LIBRARIES (short, natural)
# ══════════════════════════════════════════════════════════════
EXPRESSION_LIBRARY = {
    "warm": "Gentle natural smile, warmth in the eyes, relaxed face.",
    "neutral": "Calm neutral expression, authentic and relaxed.",
    "editorial": "Soft introspective look, natural emotional depth.",
}

POSE_LIBRARY = {
    "front_cradle": "Facing camera, both hands gently resting on the belly.",
    "walking": "Slow natural walk, captured mid‑step, relaxed.",
    "window_light": "Standing near a window, relaxed posture, one hand on belly.",
    "looking_down": "Looking softly down toward the belly, tender expression.",
}

FRAMING_VARIANTS = {
    "full_body": "Full body composition, natural proportions.",
    "three_quarters": "Three‑quarter framing, belly naturally emphasized.",
    "medium": "Medium portrait, emotional connection.",
    "close_up_emotional": "Close emotional portrait, shallow depth of field.",
    "detail_hands_belly": "Intimate detail of hands on the belly.",
}

# ══════════════════════════════════════════════════════════════
# STYLE PRESETS (concise, descriptive, no over‑promising)
# ══════════════════════════════════════════════════════════════
STYLE_PRESETS = {
    "classic": {
        "name": "Clássico",
        "prompt": (
            "Classic maternity studio portrait. Neutral background, soft front lighting. "
            "She wears a simple flowing white or cream dress. Timeless elegance."
        ),
    },
    "luxury_studio": {
        "name": "Estúdio Luxo",
        "prompt": (
            "Luxury studio maternity portrait. Dove‑gray backdrop, soft directional light from front‑left. "
            "She wears a flowing ivory silk gown. Warm neutral tones, elegant composition."
        ),
    },
    "ivory_satin": {
        "name": "Cetim Imperial",
        "prompt": (
            "Elegant studio portrait. Ivory satin backless gown, polished floor. "
            "Soft cinematic front lighting, refined shadows. High‑fashion elegance."
        ),
    },
    "black_white_editorial": {
        "name": "Preto & Branco Editorial",
        "prompt": (
            "Elegant black and white maternity portrait. Soft directional front light, "
            "clean minimalist background. Rich tonal range, timeless monochrome aesthetic."
        ),
    },
    "dramatic_black_gown": {
        "name": "Vestido Preto Dramático",
        "prompt": (
            "Dramatic fine art maternity portrait in black and white. "
            "She wears a stunning black gown, soft side‑front lighting (no harsh backlight). "
            "Minimalist composition, elegant shadows."
        ),
    },
    "golden_hour_nature": {
        "name": "Pôr do Sol na Natureza",
        "prompt": (
            "Outdoor maternity portrait in a wildflower meadow during golden hour. "
            "Warm natural front‑side light, soft bokeh, gentle wind movement. "
            "She wears a flowing dusty rose dress. Natural sun‑kissed glow."
        ),
    },
    "boho_chic": {
        "name": "Boho Chic",
        "prompt": (
            "Bohemian maternity portrait. Large window natural light, earth tones, "
            "dried floral accents. She wears a flowing earth‑toned outfit. "
            "Soft painterly light, intimate cozy atmosphere."
        ),
    },
    "taupe_wings": {
        "name": "Asas de Chiffon Nude",
        "prompt": (
            "Ethereal studio portrait. She wears a deep taupe‑nude chiffon gown "
            "with wide fabric panels. Soft overhead light, gentle shadow roll‑off."
        ),
    },
    "red_lotus": {
        "name": "Lótus Vermelho",
        "prompt": (
            "Cozy holiday maternity portrait. Lotus position on white sofa, "
            "red silk pajamas, popcorn box. Soft on‑axis ring flash plus "
            "warm Christmas tree lights from the side. Candid, intimate mood."
        ),
    },
}

# ══════════════════════════════════════════════════════════════
# NEGATIVE PROMPT (strongly avoids AI artifacts)
# ══════════════════════════════════════════════════════════════
NEGATIVE_PROMPT = (
    "cartoon, anime, 3d render, cgi, illustration, painting, sketch, "
    "plastic skin, wax face, over‑smoothed, porcelain doll, "
    "bad anatomy, extra fingers, distorted body, floating hands, "
    "harsh shadows, neon colors, oversaturated, watermark, text, "
    "selfie angle, fisheye, cheap studio look, "
    "stiff mannequin pose, excessive retouching, uncanny valley, "
    "identity drift, different person, swapped face, "
    "fantasy atmosphere, unrealistic lighting, fake fabric."
)

# ══════════════════════════════════════════════════════════════
# MAIN PROMPT GENERATOR
# ══════════════════════════════════════════════════════════════
def generate_prompt(
    tipo_ensaio: str,
    subject_description: str = "",
    framing: Literal["full_body", "three_quarters", "medium", "close_up_emotional", "detail_hands_belly"] = "full_body",
    use_naturalness_booster: bool = True,   # kept for compatibility, but not used
    use_identity_text: bool = True,
    pose_key: str = "front_cradle",
    expression_key: str = "warm",
    lens_type: str = "portrait",
) -> str:
    preset = STYLE_PRESETS.get(tipo_ensaio)
    if not preset:
        logger.warning(f"Unknown style: {tipo_ensaio}")
        style_prompt = "Professional maternity photography in a studio setting."
    else:
        style_prompt = preset["prompt"]

    parts = []

    # 1. Style and scene
    parts.append(style_prompt)

    # 2. Framing
    parts.append(FRAMING_VARIANTS.get(framing, FRAMING_VARIANTS["full_body"]))

    # 3. Pose
    parts.append(POSE_LIBRARY.get(pose_key, POSE_LIBRARY["front_cradle"]))

    # 4. Expression
    parts.append(EXPRESSION_LIBRARY.get(expression_key, EXPRESSION_LIBRARY["warm"]))

    # 5. Subject details (if provided)
    if subject_description:
        parts.append(f"Subject details: {subject_description}")

    # 6. Camera and lens aesthetic
    parts.append(CAMERA_AESTHETIC)
    parts.append(LENS_PRESETS.get(lens_type, LENS_PRESETS["portrait"]))

    # 7. Skin and makeup (simple, natural)
    editorial_styles = ["black_white_editorial", "dramatic_black_gown", "ivory_satin"]
    if tipo_ensaio in editorial_styles:
        parts.append(SKIN_MAKEUP_EDITORIAL)
    else:
        parts.append(SKIN_MAKEUP_NATURAL)

    # 8. Lighting and pose guidelines (soft, natural)
    parts.append(LIGHTING_GUIDELINES)
    parts.append(POSE_GUIDELINES)

    # 9. Base realism
    parts.append(BASE_REALISM)

    # 10. IDENTITY ANCHOR (placed at the end – highest priority)
    if use_identity_text:
        parts.append(IDENTITY_ANCHOR)

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
    prompt = generate_prompt("luxury_studio", "Woman with dark curly hair, warm brown skin.", lens_type="portrait")
    print("\n--- POSITIVE PROMPT ---\n", prompt)
    print("\n--- NEGATIVE PROMPT ---\n", generate_negative_prompt())
    print("\n--- AVAILABLE STYLES ---")
    for s in get_available_styles():
        print(f"  - {s['name']} ({s['id']})")