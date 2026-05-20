""" 
Prompt Engine — Premium Realistic Maternity Photography
Optimized for openai/gpt-image-2
=======================================================

Goals:
- Real maternity photography feeling
- Luxury premium aesthetic
- Strong identity preservation
- Natural studio realism
- Feminine polished appearance
- Avoid artificial AI look
- Avoid overprompting
- Stable commercial SaaS generation

IMPORTANT:
This engine intentionally avoids:
- Overly technical photography instructions
- Excessive cinematic jargon
- Unrealistic fantasy environments
- Hyper-detailed facial manipulation
- Artificial perfection
"""

import logging
from typing import Optional, Literal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
# IDENTITY PRESERVATION (UPDATED: consistency across images)
# ══════════════════════════════════════════════════════════════

IDENTITY_ANCHOR = (
    "The client has uploaded 3 reference photos of herself. "
    "Preserve the identity of this exact person. "
    "Maintain the same face, facial proportions, eyes, nose, lips, "
    "skin tone, and hairline. "
    "Do not alter ethnicity, age, or facial structure. "
    "Identity preservation takes priority over artistic styling. "
    "Consistent facial identity across all generated images."
)

# ══════════════════════════════════════════════════════════════
# REALISM FOUNDATION
# ══════════════════════════════════════════════════════════════

BASE_REALISM = (
    "Real professional maternity photography. "
    "Authentic body proportions. "
    "Pregnant belly naturally visible and central to the composition. "
    "Natural emotional expression. "
    "Looks like a real premium maternity photoshoot captured by a professional photographer."
)

# ══════════════════════════════════════════════════════════════
# REALISM GUARDRAILS
# ══════════════════════════════════════════════════════════════

REALISM_GUARDRAILS = (
    "Avoid CGI appearance, artificial beauty filter aesthetics, "
    "plastic skin, fantasy atmosphere, or over-retouched photography. "
    "Avoid raw unretouched skin appearance or casual cellphone selfie aesthetics. "
    "The image should feel indistinguishable from a real luxury maternity session."
)

# ══════════════════════════════════════════════════════════════
# PROFESSIONAL CAMERA AESTHETIC
# ══════════════════════════════════════════════════════════════

IPHONE_PHOTOGRAPHY = (
    "Captured with a modern full-frame professional camera aesthetic. "
    "Natural premium skin rendering with soft dynamic range, balanced highlights, "
    "subtle depth-of-field and realistic professional portrait tonality. "
    "Luxury modern maternity photography aesthetic with authentic studio realism."
)

# ══════════════════════════════════════════════════════════════
# LENS STYLES
# ══════════════════════════════════════════════════════════════

LENS_PRESETS = {
    "portrait": (
        "50mm portrait photography aesthetic with natural perspective."
    ),

    "cinematic": (
        "85mm cinematic portrait aesthetic with soft background compression."
    ),

    "documentary": (
        "35mm documentary photography aesthetic with natural environmental feeling."
    ),
}

# ══════════════════════════════════════════════════════════════
# LIGHTING GUIDELINES
# ══════════════════════════════════════════════════════════════

LIGHTING_GUIDELINES = (
    "Soft front or side-front lighting with natural falloff. "
    "Balanced exposure on the face and body. "
    "No harsh shadows, no silhouette lighting, no overexposed highlights."
)

# ══════════════════════════════════════════════════════════════
# NATURAL POSE GUIDELINES
# ══════════════════════════════════════════════════════════════

POSE_GUIDELINES = (
    "Natural relaxed posture with authentic body language. "
    "Comfortable pose, natural hand positioning, gentle movement. "
    "Avoid stiff mannequin poses or awkward body angles."
)

# ══════════════════════════════════════════════════════════════
# FEMININE PREMIUM DIRECTION
# ══════════════════════════════════════════════════════════════

FEMININE_DIRECTION = (
    "She looks elegant, feminine, confident, and naturally beautiful. "
    "The photoshoot feels emotionally warm, luxurious, and professionally styled."
)

# ══════════════════════════════════════════════════════════════
# PROFESSIONAL MAKEUP & HAIR
# ══════════════════════════════════════════════════════════════

SKIN_MAKEUP_NATURAL = (
    "Professional studio-quality soft maternity makeup. "
    "Skin appears naturally refined and softly perfected while preserving authentic skin texture and pores. "
    "Subtle skin evening, gentle under-eye brightening and soft healthy glow. "
    "Light natural foundation appearance with realistic texture retention. "
    "Softly defined eyes, delicate lashes, subtle blush and hydrated neutral lips. "
    "Luxury beauty studio finish without looking over-retouched or artificial. "
    "Hair professionally styled with soft volume and polished natural movement."
)

SKIN_MAKEUP_EDITORIAL = (
    "Luxury studio soft glam makeup with refined editorial elegance. "
    "Naturally perfected skin with preserved pores and realistic texture. "
    "Soft skin smoothing, subtle contour, elegant lashes and softly illuminated complexion. "
    "Balanced beauty retouch aesthetic commonly seen in premium maternity studios. "
    "Refined neutral lip tone and polished eyes without exaggerated makeup. "
    "Professional fashion maternity beauty finish while maintaining realism."
)

# ══════════════════════════════════════════════════════════════
# NATURALNESS BOOSTER
# ══════════════════════════════════════════════════════════════

NATURALNESS_BOOSTER = (
    "Healthy pregnancy glow with soft natural warmth. "
    "Authentic emotional connection and relaxed expression. "
    "Natural fabric behavior with realistic folds and believable texture."
)

# ══════════════════════════════════════════════════════════════
# ENVIRONMENT REALISM
# ══════════════════════════════════════════════════════════════

ENVIRONMENT_REALISM = (
    "Realistic spatial depth, subtle floor shadows, authentic environmental lighting, "
    "natural foreground and background separation, believable physical space."
)

# ══════════════════════════════════════════════════════════════
# PREMIUM RETOUCH DIRECTION
# ══════════════════════════════════════════════════════════════

PREMIUM_RETOUCH_DIRECTION = (
    "Subtle premium beauty retouching with realistic skin texture preservation. "
    "Professional maternity studio finishing with refined skin balance, "
    "natural luminosity and authentic facial detail retention."
)

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
        "Soft candid laughter captured naturally between poses."
    ),

    "looking_down": (
        "Looking gently toward the belly with emotional connection."
    ),

    "window_gaze": (
        "Soft thoughtful gaze toward the window with calm emotion."
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
        "Captured naturally while walking slowly and comfortably."
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
        "Full body composition with natural proportions and realistic posture."
    ),

    "three_quarters": (
        "Three-quarter composition emphasizing the belly naturally."
    ),

    "medium": (
        "Medium portrait with emotional connection and natural body framing."
    ),

    "close_up_emotional": (
        "Close emotional portrait with shallow depth-of-field."
    ),

    "detail_hands_belly": (
        "Intimate detail shot focused on hands resting naturally on the belly."
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
            "Professional photography studio environment with neutral backdrop, "
            "soft diffused front lighting and subtle floor shadows. "
            "She wears a flowing white or cream maternity dress. "
            "Elegant and timeless atmosphere. "
            "Subtle professional beauty retouching commonly seen in luxury maternity photography."
        ),
    },

    "luxury_studio": {
        "name": "Estúdio Luxo",

        "prompt": (
            "Luxury maternity photography studio environment with realistic spatial depth, "
            "warm neutral tones and soft directional lighting from the front-left. "
            "She wears a flowing ivory silk gown with realistic fabric texture and natural folds. "
            "Sophisticated premium editorial atmosphere. "
            "Premium maternity studio beauty retouch aesthetic."
        ),
    },

    "ivory_satin": {
        "name": "Cetim Imperial",

        "prompt": (
            "Elegant luxury maternity studio portrait. "
            "Luxury studio with polished floor, soft neutral walls and cinematic front lighting. "
            "She wears an elegant ivory satin gown with realistic fabric texture and natural folds. "
            "Refined premium fashion atmosphere. "
            "Premium maternity studio beauty retouch aesthetic."
        ),
    },

    "black_white_editorial": {
        "name": "Preto & Branco Editorial",

        "prompt": (
            "Elegant black and white maternity portrait. "
            "Minimalist luxury studio environment with soft directional front lighting "
            "and authentic analog film photography feeling. "
            "Rich tonal transitions and refined monochrome atmosphere. "
            "Subtle professional beauty retouching commonly seen in luxury maternity photography."
        ),
    },

   "dramatic_black_gown": {
    "name": "Vestido Preto Dramático",

    "prompt": (
        "Dramatic fine art maternity portrait in black and white. "
        "Urban luxury setting at night – high-end rooftop or sleek city apartment with large windows. "
        "Soft ambient city lights creating atmospheric depth, no harsh backlight. "
        "She wears an elegant black gown with believable fabric texture and natural folds. "
        "Sophisticated cinematic atmosphere with soft shadow transitions. "
        "Premium maternity studio beauty retouch aesthetic."
    ),
},

    "golden_hour_nature": {
        "name": "Pôr do Sol na Natureza",

        "prompt": (
            "Outdoor maternity portrait in a real wildflower field during golden hour. "
            "Natural sunlight exposure with realistic contrast and restrained highlights. "
            "Soft natural bokeh, believable outdoor atmosphere and authentic sunset tones. "
            "She wears a flowing dress – options: dusty rose (current), baby blue, or soft lavender. "
            "Natural fabric movement. "
            "Subtle professional beauty retouching commonly seen in luxury maternity photography."
        ),
    },

    "boho_chic": {
        "name": "Boho Chic",

        "prompt": (
            "Bohemian luxury maternity portrait in an authentic cozy interior environment. "
            "Large window natural light, warm earth tones, linen textures and pampas grass accents. "
            "Soft lived-in atmosphere with realistic environmental depth. "
            "Premium maternity studio beauty retouch aesthetic."
        ),
    },

    "taupe_wings": {
        "name": "Asas de Chiffon Nude",

        "prompt": (
            "Luxury maternity studio portrait with ethereal elegance. "
            "Soft neutral studio backdrop with realistic spatial depth and subtle floor shadows. "
            "She wears a deep taupe chiffon gown with lightweight flowing fabric "
            "moving naturally with gravity and gentle movement. "
            "Soft overhead lighting and refined premium atmosphere. "
            "Premium maternity studio beauty retouch aesthetic."
        ),
    },

    "red_lotus": {
        "name": "Lótus Vermelho",

        "prompt": (
            "Cozy holiday maternity portrait in a real luxury living room environment. "
            "Warm authentic Christmas decoration with realistic ambient depth. "
            "She sits comfortably on a white sofa wearing elegant red silk pajamas. "
            "Soft warm practical lighting creates a candid premium holiday atmosphere. "
            "Subtle professional beauty retouching commonly seen in luxury maternity photography."
        ),
    },
}

# ══════════════════════════════════════════════════════════════
# NEGATIVE PROMPT
# ══════════════════════════════════════════════════════════════

NEGATIVE_PROMPT = (
    "cartoon, anime, 3d render, cgi, illustration, painting, drawing, sketch, digital art, "
    "plastic skin, wax face, over-smoothed skin, fake skin texture, porcelain doll, "
    "bad anatomy, extra fingers, distorted hands, floating hands, malformed body, "
    "harsh shadows, overexposed highlights, neon colors, oversaturated colors, "
    "watermark, logo, text, selfie angle, fisheye distortion, cheap studio look, "
    "cheap beauty retouch, smartphone selfie skin, overly sharp pores, greasy skin texture, "
    "flat flash lighting, amateur instagram filter, "
    "stiff mannequin pose, awkward body angles, excessive retouching, uncanny valley, "
    "visible AI artifacts, identity drift, different person, swapped identity, "
    "fantasy atmosphere, unrealistic lighting, unrealistic fabric behavior."
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
    use_naturalness_booster: Optional[bool] = None,
    use_identity_text: bool = True,
    pose_key: str = "front_cradle",
    expression_key: str = "warm",
    lens_type: str = "portrait",
) -> str:

    no_booster_styles = [
        "black_white_editorial",
        "dramatic_black_gown"
    ]

    editorial_skin_styles = [
        "black_white_editorial",
        "dramatic_black_gown",
        "ivory_satin"
    ]

    if use_naturalness_booster is None:
        use_naturalness_booster = tipo_ensaio not in no_booster_styles

    preset = STYLE_PRESETS.get(tipo_ensaio)

    if not preset:
        logger.warning(f"Unknown style: {tipo_ensaio}")

        style_prompt = (
            "Real luxury maternity photography in a professional environment."
        )
    else:
        style_prompt = preset["prompt"]

    parts = []

    if use_identity_text:
        parts.append(IDENTITY_ANCHOR)

    parts.append(style_prompt)

    parts.append(
        FRAMING_VARIANTS.get(
            framing,
            FRAMING_VARIANTS["full_body"]
        )
    )

    parts.append(
        POSE_LIBRARY.get(
            pose_key,
            POSE_LIBRARY["front_cradle"]
        )
    )

    parts.append(
        EXPRESSION_LIBRARY.get(
            expression_key,
            EXPRESSION_LIBRARY["warm"]
        )
    )

    if subject_description:
        parts.append(
            f"Subject details: {subject_description}"
        )

    parts.append(IPHONE_PHOTOGRAPHY)

    parts.append(
        LENS_PRESETS.get(
            lens_type,
            LENS_PRESETS["portrait"]
        )
    )

    if tipo_ensaio in editorial_skin_styles:
        parts.append(SKIN_MAKEUP_EDITORIAL)
    else:
        parts.append(SKIN_MAKEUP_NATURAL)

    parts.append(FEMININE_DIRECTION)

    parts.append(LIGHTING_GUIDELINES)

    parts.append(POSE_GUIDELINES)

    parts.append(ENVIRONMENT_REALISM)

    parts.append(PREMIUM_RETOUCH_DIRECTION)

    if use_naturalness_booster:
        parts.append(NATURALNESS_BOOSTER)

    parts.append(BASE_REALISM)

    parts.append(REALISM_GUARDRAILS)

    final_prompt = " ".join(parts)

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

    print("\n--- POSITIVE PROMPT ---\n")
    print(prompt)

    print("\n--- NEGATIVE PROMPT ---\n")
    print(generate_negative_prompt())

    print("\n--- AVAILABLE STYLES ---\n")

    for style in get_available_styles():
        print(f"- {style['name']} ({style['id']})")

    print("\n" + "=" * 80)