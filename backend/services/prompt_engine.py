"""
AUREA AI
Premium Realistic Maternity Photography Prompt Engine
Optimized for openai/gpt-image-2

GOALS
------
- Strong identity preservation
- Real luxury maternity photography
- Natural premium beauty
- Stable SaaS generation
- Reduced AI artifacts
- Consistent commercial output
- Optimized prompt size
- Better GPT-Image-2 behavior

IMPORTANT
---------
This engine assumes:
- The client uploads 3 reference photos
- The uploaded photos are the SOURCE OF TRUTH
- Identity preservation is more important than styling
"""

import logging
from typing import Optional, Literal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════

MAX_PROMPT_LENGTH = 900

# ══════════════════════════════════════════════════════════════
# REFERENCE PRIORITY
# ══════════════════════════════════════════════════════════════

REFERENCE_PRIORITY = (
    "The client uploaded 3 real reference photos of herself. "
    "The uploaded reference photos are the absolute source of truth for identity. "
    "Use the text prompt only as artistic direction while keeping the exact same person from the references."
)

# ══════════════════════════════════════════════════════════════
# IDENTITY PRESERVATION
# ══════════════════════════════════════════════════════════════

IDENTITY_PRIORITY = (
    "Preserve the exact same woman from the uploaded photos. "
    "Maintain the same face shape, eyes, nose, lips, skin tone, ethnicity, hairline and age. "
    "Do not generate a different woman inspired by the references. "
    "Do not beautify, idealize or modify facial structure. "
    "Identity preservation is more important than styling or artistic direction."
)

# ══════════════════════════════════════════════════════════════
# CAMERA & REALISM
# ══════════════════════════════════════════════════════════════

CAMERA_DIRECTION = (
    "Natural professional photography aesthetic with soft depth of field, "
    "balanced highlights and realistic tonal range."
)

REALISM_DIRECTION = (
    "Real premium maternity photography with authentic human appearance. "
    "Natural skin texture, believable body proportions and realistic pregnancy anatomy. "
    "Professional studio quality without artificial AI appearance. "
    "The image should feel like a real maternity photoshoot captured by a high-end photographer."
)

# ══════════════════════════════════════════════════════════════
# BEAUTY
# ══════════════════════════════════════════════════════════════

SKIN_AND_BEAUTY = (
    "Professional maternity hair and makeup styling. "
    "Refined natural beauty with realistic skin texture and preserved pores. "
    "Soft polished appearance without excessive retouching. "
    "Healthy natural skin tones and believable facial detail."
)

EDITORIAL_BEAUTY = (
    "Luxury editorial maternity beauty styling with realistic skin texture. "
    "Soft refined makeup, natural complexion, elegant eyes and polished hair styling. "
    "Premium studio beauty aesthetic while maintaining realism."
)

# ══════════════════════════════════════════════════════════════
# LIGHTING
# ══════════════════════════════════════════════════════════════

LIGHTING_GUIDELINES = (
    "Soft front or side-front lighting with natural falloff. "
    "Balanced exposure on face and body. "
    "No harsh shadows or blown highlights."
)

# ══════════════════════════════════════════════════════════════
# FEMININE DIRECTION
# ══════════════════════════════════════════════════════════════

FEMININE_DIRECTION = (
    "Elegant feminine presence with natural confidence and emotional warmth."
)

# ══════════════════════════════════════════════════════════════
# POSE DIRECTION
# ══════════════════════════════════════════════════════════════

POSE_GUIDELINES = (
    "Natural relaxed posture with authentic body language. "
    "Comfortable pose and believable hand positioning. "
    "Avoid stiff mannequin poses or unnatural body angles."
)

# ══════════════════════════════════════════════════════════════
# LENS STYLES
# ══════════════════════════════════════════════════════════════

LENS_PRESETS = {
    "portrait": (
        "50mm portrait photography aesthetic with natural perspective."
    ),

    "cinematic": (
        "85mm portrait aesthetic with soft background compression."
    ),

    "documentary": (
        "35mm documentary photography aesthetic with natural environmental feeling."
    ),
}

# ══════════════════════════════════════════════════════════════
# EXPRESSIONS
# ══════════════════════════════════════════════════════════════

EXPRESSION_LIBRARY = {

    "warm": (
        "Gentle natural smile with emotional warmth in the eyes."
    ),

    "neutral": (
        "Calm relaxed expression with authentic emotional presence."
    ),

    "editorial": (
        "Soft introspective expression with refined emotional depth."
    ),

    "laughing_soft": (
        "Soft candid laughter captured naturally."
    ),

    "looking_down": (
        "Looking gently toward the belly with emotional connection."
    ),

    "window_gaze": (
        "Soft thoughtful gaze toward the window."
    ),
}

# ══════════════════════════════════════════════════════════════
# POSES
# ══════════════════════════════════════════════════════════════

POSE_LIBRARY = {

    "front_cradle": (
        "Facing camera with both hands gently resting on the belly."
    ),

    "walking": (
        "Captured naturally while walking slowly."
    ),

    "window_light": (
        "Standing naturally near a window with relaxed posture."
    ),

    "looking_down_pose": (
        "Looking softly toward the belly with gentle hand placement."
    ),

    "soft_hair_touch": (
        "One hand softly touching the hair while the other rests on the belly."
    ),
}

# ══════════════════════════════════════════════════════════════
# FRAMING
# ══════════════════════════════════════════════════════════════

FRAMING_VARIANTS = {

    "full_body": (
        "Full body composition with realistic proportions."
    ),

    "three_quarters": (
        "Three-quarter composition emphasizing the belly naturally."
    ),

    "medium": (
        "Medium portrait with emotional connection."
    ),

    "close_up_emotional": (
        "Close emotional portrait with shallow depth of field."
    ),

    "detail_hands_belly": (
        "Intimate detail shot focused on hands resting on the belly."
    ),
}

# ══════════════════════════════════════════════════════════════
# STYLE PRESETS
# ══════════════════════════════════════════════════════════════

STYLE_PRESETS = {

    "classic": {
        "name": "Clássico",

        "prompt": (
            "Classic luxury maternity studio portrait. "
            "Professional studio environment with neutral backdrop and soft diffused lighting. "
            "She wears a flowing white or cream maternity dress. "
            "Elegant timeless atmosphere."
        ),
    },

    "luxury_studio": {
        "name": "Estúdio Luxo",

        "prompt": (
            "Luxury maternity photography studio with warm neutral tones and soft lighting. "
            "She wears a flowing ivory silk gown with realistic fabric texture and natural folds. "
            "Sophisticated premium maternity atmosphere."
        ),
    },

    "ivory_satin": {
        "name": "Cetim Imperial",

        "prompt": (
            "Elegant maternity studio portrait with polished neutral environment. "
            "She wears an ivory satin gown with natural folds and realistic fabric movement. "
            "Refined premium fashion atmosphere."
        ),
    },

    "black_white_editorial": {
        "name": "Preto & Branco Editorial",

        "prompt": (
            "Elegant black and white maternity portrait with minimalist studio environment. "
            "Soft directional lighting and refined monochrome atmosphere."
        ),
    },

    "dramatic_black_gown": {
        "name": "Vestido Preto Dramático",

        "prompt": (
            "Fine art maternity portrait in black and white. "
            "Minimalist luxury studio environment. "
            "Elegant black gown with believable fabric texture and natural folds."
        ),
    },

    "golden_hour_nature": {
        "name": "Pôr do Sol na Natureza",

        "prompt": (
            "Outdoor maternity portrait in a real wildflower field during golden hour. "
            "Natural sunset tones, soft outdoor bokeh and realistic natural light. "
            "She wears a flowing dusty rose dress with natural fabric movement."
        ),
    },

    "boho_chic": {
        "name": "Boho Chic",

        "prompt": (
            "Bohemian luxury maternity portrait in a cozy interior environment. "
            "Warm earth tones, natural window light, linen textures and pampas grass accents."
        ),
    },

    "taupe_wings": {
        "name": "Asas de Chiffon Nude",

        "prompt": (
            "Luxury maternity studio portrait with soft neutral backdrop. "
            "Deep taupe chiffon gown with lightweight flowing fabric moving naturally."
        ),
    },

    "red_lotus": {
        "name": "Lótus Vermelho",

        "prompt": (
            "Cozy holiday maternity portrait in a luxury living room environment. "
            "Warm Christmas atmosphere with elegant red silk pajamas and soft ambient lighting."
        ),
    },
}

# ══════════════════════════════════════════════════════════════
# NEGATIVE PROMPT
# ══════════════════════════════════════════════════════════════

NEGATIVE_PROMPT = (
    "cgi, render, cartoon, anime, illustration, painting, digital art, "
    "plastic skin, wax skin, over-retouched skin, fake beauty filter, "
    "different person, identity drift, altered face, facial distortion, "
    "bad anatomy, distorted hands, extra fingers, malformed body, "
    "unrealistic lighting, fantasy environment, oversaturated colors, "
    "selfie look, influencer aesthetic, instagram filter, ai artifacts, "
    "uncanny valley, excessive glamour retouching."
)

# ══════════════════════════════════════════════════════════════
# PROMPT GENERATOR
# ══════════════════════════════════════════════════════════════

def generate_prompt(
    tipo_ensaio: str,

    subject_description: str = "",

    framing: Literal[
        "full_body",
        "three_quarters",
        "medium",
        "close_up_emotional",
        "detail_hands_belly"
    ] = "full_body",

    pose_key: str = "front_cradle",

    expression_key: str = "warm",

    lens_type: str = "portrait",

    use_identity_text: bool = True,
):

    editorial_styles = [
        "black_white_editorial",
        "dramatic_black_gown",
        "ivory_satin"
    ]

    preset = STYLE_PRESETS.get(tipo_ensaio)

    if not preset:
        logger.warning(f"Unknown style: {tipo_ensaio}")

        style_prompt = (
            "Real luxury maternity photography in a professional studio environment."
        )

    else:
        style_prompt = preset["prompt"]

    framing_prompt = FRAMING_VARIANTS.get(
        framing,
        FRAMING_VARIANTS["full_body"]
    )

    pose_prompt = POSE_LIBRARY.get(
        pose_key,
        POSE_LIBRARY["front_cradle"]
    )

    expression_prompt = EXPRESSION_LIBRARY.get(
        expression_key,
        EXPRESSION_LIBRARY["warm"]
    )

    lens_prompt = LENS_PRESETS.get(
        lens_type,
        LENS_PRESETS["portrait"]
    )

    beauty_prompt = (
        EDITORIAL_BEAUTY
        if tipo_ensaio in editorial_styles
        else SKIN_AND_BEAUTY
    )

    parts = []

    # PRIORIDADE MÁXIMA
    if use_identity_text:
        parts.append(REFERENCE_PRIORITY)
        parts.append(IDENTITY_PRIORITY)

    # ESTILO
    parts.append(style_prompt)

    # COMPOSIÇÃO
    parts.append(framing_prompt)
    parts.append(pose_prompt)
    parts.append(expression_prompt)

    # DETALHES DA PESSOA
    if subject_description:
        parts.append(
            f"Subject details: {subject_description}"
        )

    # CÂMERA
    parts.append(CAMERA_DIRECTION)
    parts.append(lens_prompt)

    # BELEZA
    parts.append(beauty_prompt)

    # LUZ
    parts.append(LIGHTING_GUIDELINES)

    # FEMININO
    parts.append(FEMININE_DIRECTION)

    # POSE REALISTA
    parts.append(POSE_GUIDELINES)

    # REALISMO
    parts.append(REALISM_DIRECTION)

    # FINAL
    final_prompt = " ".join(parts)

    # NORMALIZAÇÃO
    final_prompt = " ".join(final_prompt.split())

    # HARD LIMIT
    if len(final_prompt) > MAX_PROMPT_LENGTH:

        logger.warning(
            f"Prompt exceeded limit ({len(final_prompt)} chars). Truncating."
        )

        final_prompt = final_prompt[:MAX_PROMPT_LENGTH].rstrip()

    logger.info(
        f"Prompt generated: {tipo_ensaio} ({len(final_prompt)} chars)"
    )

    return final_prompt

# ══════════════════════════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════════════

def generate_negative_prompt() -> str:
    return NEGATIVE_PROMPT

def get_available_styles() -> list:

    return [
        {
            "id": key,
            "name": value["name"]
        }

        for key, value in STYLE_PRESETS.items()
    ]

def get_framing_options() -> list:

    return [
        {
            "id": key,
            "name": key.replace("_", " ").title()
        }

        for key in FRAMING_VARIANTS.keys()
    ]

# ══════════════════════════════════════════════════════════════
# EXAMPLE
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":

    prompt = generate_prompt(

        tipo_ensaio="luxury_studio",

        subject_description=(
            "Woman with medium-dark skin tone, dark curly hair and brown eyes."
        ),

        framing="three_quarters",

        pose_key="looking_down_pose",

        expression_key="warm",

        lens_type="cinematic"
    )

    print("\n" + "=" * 80)
    print("POSITIVE PROMPT")
    print("=" * 80 + "\n")

    print(prompt)

    print("\n")
    print("=" * 80)
    print("NEGATIVE PROMPT")
    print("=" * 80 + "\n")

    print(generate_negative_prompt())

    print("\n")
    print("=" * 80)
    print("AVAILABLE STYLES")
    print("=" * 80 + "\n")

    for style in get_available_styles():
        print(f"- {style['name']} ({style['id']})")

    print("\n" + "=" * 80)