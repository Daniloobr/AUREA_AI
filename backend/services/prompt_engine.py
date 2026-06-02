"""
AUREA AI — Premium Maternity Photography Prompt Engine
=======================================================
Optimized for openai/gpt-image-2 via Replicate with 3 reference photos.

Engineering Principles:
  1. Identity anchor once at the START — no repetition.
  2. Concrete visual facts only: scene, lighting, outfit, pose, framing, processing.
  3. Camera/lens language activates photorealistic behavior.
  4. No vague adjectives ("beautiful", "elegant", "stunning").
  5. Prompts ≤ 1000 chars to ensure full delivery.
  6. Each style describes a real photoshoot a photographer would direct.

Context:
  - Subject: pregnant woman, belly visible and celebrated.
  - Input: 3 natural reference photos of the real woman.
  - Output: professional studio-quality maternity portrait.
"""

import logging
from typing import Literal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════
MAX_PROMPT_LENGTH = 1000

# ══════════════════════════════════════════════════════════════
# IDENTITY — single sentence at prompt start
# ══════════════════════════════════════════════════════════════
IDENTITY_TEXT = (
    "Preserve exact identity from the 3 reference photos. "
    "Same face, facial structure, skin tone, body proportions, and pregnancy features. "
    "This woman is pregnant, with a visible pregnant belly."
)

# ══════════════════════════════════════════════════════════════
# QUALITY BLOCK — global quality instructions after identity
# ══════════════════════════════════════════════════════════════
QUALITY_BLOCK = (
    "Ultra photorealistic maternity photography. "
    "Soft, smooth skin texture, subtle makeup look. "
    "Light foundation, even skin tone, natural glow. "
    "No visible pores, no blemishes, no plastic skin effect. "
    "Realistic eyes, realistic hands, realistic anatomy. "
    "Professional studio lighting. Medium format camera. "
    "Shallow depth of field. Editorial magazine quality, high dynamic range. "
    "Direct eye contact, sharp focus on eyes."
)

# ══════════════════════════════════════════════════════════════
# LENS PRESETS — override library (backward compat)
# ══════════════════════════════════════════════════════════════
LENS_PRESETS = {
    "portrait":    "Medium format camera, 85mm portrait lens, shallow depth of field.",
    "cinematic":   "Medium format camera, 50mm lens, cinematic depth of field.",
    "wide":        "Medium format camera, 35mm lens, environmental context.",
    "telephoto":   "Medium format camera, 135mm telephoto lens, background compression.",
    "close":       "Medium format camera, 100mm macro lens, sharp focus on face.",
}

# ══════════════════════════════════════════════════════════════
# EXPRESSIONS — override library (backward compat)
# ══════════════════════════════════════════════════════════════
EXPRESSION_LIBRARY = {
    "warm":           "warm gentle smile, eyes full of joy.",
    "serene":         "calm peaceful expression, eyes slightly closed.",
    "editorial":      "composed introspective look, chin lowered, gaze distant.",
    "laughing":       "genuine candid laugh, head tilted back.",
    "tender_belly":   "looking down at belly with love, soft smile.",
    "window_dream":   "gazing toward light, dreamy faraway expression.",
    "proud":          "confident gaze toward camera, empowered expression.",
}

# ══════════════════════════════════════════════════════════════
# POSES — override library (backward compat)
# ══════════════════════════════════════════════════════════════
POSE_LIBRARY = {
    "front_cradle":     "facing camera, hands cupped gently under belly.",
    "side_profile":     "standing in profile, belly silhouette visible.",
    "walking_natural":  "mid-stride, natural movement, fabric in motion.",
    "window_lean":      "leaning against window frame, one hand on belly.",
    "seated_grace":     "seated, one hand on belly, the other relaxed.",
    "hair_belly":       "one hand touching hair, other on belly.",
    "looking_down":     "standing tall, looking tenderly down at belly.",
}

# ══════════════════════════════════════════════════════════════
# FRAMING VARIANTS — override library (backward compat)
# ══════════════════════════════════════════════════════════════
FRAMING_VARIANTS = {
    "full_body":          "full body, floor to crown.",
    "three_quarters":     "three-quarter shot from knees up.",
    "medium":             "medium portrait from waist up.",
    "close_up_emotional": "tight portrait, face fills frame.",
    "detail_hands_belly": "close detail of hands on belly.",
    "silhouette":         "side silhouette, belly outlined by backlight.",
}

# ══════════════════════════════════════════════════════════════
# STYLE PRESETS — structured JSON
# Each preset contains the concrete facts a photographer would
# communicate to produce the shot: scene, lighting, outfit,
# pose, framing, processing, and default camera lens.
# ══════════════════════════════════════════════════════════════
STYLE_PRESETS = {

    # ─── CLÁSSICOS ATEMPORAIS ───────────────────────────────────────

    "classic_studio": {
        "name": "Estúdio Clássico",
        "category": "Clássicos Atemporais",
        "description": "Retrato clássico em estúdio com fundo neutro cinza-pérola, iluminação suave e vestido de musselina branco.",
        "cover": "/thumbnails/classic.png",
        "camera": "85mm lens.",
        "scene": "Minimalist studio, pearl-gray seamless backdrop.",
        "lighting": "Two softboxes: main at 45 deg left, fill from right, even diffuse light.",
        "outfit": "White muslin wrap dress with natural folds.",
        "pose": "Standing centered, hands resting gently on belly, warm smile toward camera.",
        "framing": "Three-quarter length.",
        "processing": "Color, warm ivory tones, clean professional finish.",
    },

    "luxury_studio": {
        "name": "Estúdio Luxo Couture",
        "category": "Clássicos Atemporais",
        "description": "Estúdio luxuoso com fundo degradê cinza-pomba, rim light dourado e vestido de seda marfim.",
        "cover": "/thumbnails/luxury_studio.png",
        "camera": "50mm lens.",
        "scene": "Luxury studio, dove-gray gradient backdrop, polished concrete floor.",
        "lighting": "Warm gold rim light from behind right, soft front fill.",
        "outfit": "Backless ivory silk gown with long train on floor.",
        "pose": "Standing in profile, hands on belly, composed look toward camera.",
        "framing": "Full body.",
        "processing": "Color, warm gold tones, editorial finish.",
    },

    "ivory_satin": {
        "name": "Cetim Imperial",
        "category": "Clássicos Atemporais",
        "description": "Vestido imperial de cetim marfim sem costas com cauda longa sobre piso polido, iluminação lateral dramática.",
        "cover": "/thumbnails/image3.png",
        "camera": "135mm lens.",
        "scene": "Studio, dark gray backdrop, highly reflective white marble floor.",
        "lighting": "Directional side light from right, satin sheen catching light.",
        "outfit": "Ivory satin backless gown with long train.",
        "pose": "Standing in profile, hands on belly, eyes closed in serene expression.",
        "framing": "Full body.",
        "processing": "Color, crisp satin texture, fine art finish.",
    },

    # ─── EDITORIAIS VOGUE ───────────────────────────────────────────

    "black_white_editorial": {
        "name": "Preto & Branco Editorial",
        "category": "Editoriais Vogue",
        "description": "Editorial monocromático de alto contraste com luz dramática, granulação de filme e silhueta esculpida.",
        "cover": "/thumbnails/black_white_editorial.png",
        "camera": "50mm lens.",
        "scene": "Studio, seamless dark backdrop.",
        "lighting": "Single dramatic side light from left, deep shadows, bright highlights.",
        "outfit": "Flowing black silk chiffon gown.",
        "pose": "Standing in profile, hands on belly, composed editorial gaze off-camera.",
        "framing": "Full body.",
        "processing": "Black and white, high contrast, subtle film grain.",
    },

    "dramatic_black_gown": {
        "name": "Vestido Preto Dramático",
        "category": "Editoriais Vogue",
        "description": "Vestido longo preto sem costas com iluminação Chiaroscuro lateral sobre piso escuro polido.",
        "cover": "/thumbnails/vestidoBlack.png",
        "camera": "50mm lens.",
        "scene": "Studio, black backdrop, highly polished dark floor.",
        "lighting": "Single strong side light from left, bold shadow on half the body.",
        "outfit": "Backless black velvet gown with long trailing skirt.",
        "pose": "Standing in profile, hands on belly, confident gaze toward camera.",
        "framing": "Full body.",
        "processing": "Black and white, deep shadows, cinematic contrast.",
    },

    "red_velvet": {
        "name": "Veludo Borgonha",
        "category": "Editoriais Vogue",
        "description": "Vestido longo de veludo borgonha com cauda dramática, rim light dourado e fundo mármore preto.",
        "cover": "/thumbnails/red_velvet.png",
        "camera": "135mm lens.",
        "scene": "Studio, black marble backdrop and floor.",
        "lighting": "Warm golden rim light from behind right, soft front fill.",
        "outfit": "Deep burgundy velvet gown with floor-length train.",
        "pose": "Standing in profile, hands on belly, composed editorial expression.",
        "framing": "Full body.",
        "processing": "Color, opulent warm tones, rich velvet texture.",
    },

    
    "seated_cube_editorial": {
        "name": "Cubo Branco Editorial",
        "category": "Editoriais Vogue",
        "description": "Sentada em cubo branco matte, blazer preto, top cropped, calça pantalona e sandália plataforma.",
        "cover": "/thumbnails/CuboBranco.png",
        "camera": "35mm lens.",
        "scene": "Studio, warm dark taupe-mocha gradient backdrop, light polished floor.",
        "lighting": "Front-left warm diffused studio light, subtle floor spotlight.",
        "outfit": "Open long black blazer, scalloped black crop top, high-waist wide-leg black trousers, beige platform sandals, silver jewelry.",
        "pose": "Seated sideways on matte white cube, legs crossed at ankle, torso turned toward camera, calm gaze off-camera.",
        "framing": "Full body.",
        "processing": "Color, sophisticated warm tones, modern editorial finish.",
    },


    # ─── ORGÂNICOS & SONHADORES ─────────────────────────────────────

    "golden_hour_nature": {
        "name": "Pôr do Sol na Natureza",
        "category": "Orgânicos & Sonhadores",
        "description": "Campo aberto de flores silvestres ao pôr do sol com luz dourada lateral e vestido fluido rosa antigo.",
        "cover": "/thumbnails/golden.png",
        "camera": "85mm lens.",
        "scene": "Open wildflower meadow at golden hour.",
        "lighting": "Warm orange-gold sunlight from right side.",
        "outfit": "Flowing dusty rose chiffon maxi dress in gentle motion.",
        "pose": "Walking naturally through meadow, hands on belly, radiant smile toward camera.",
        "framing": "Full body.",
        "processing": "Color, warm 4500K golden tones, outdoor natural light.",
    },

    "boho_chic": {
        "name": "Boho Chic Rústico",
        "category": "Orgânicos & Sonhadores",
        "description": "Interior rústico com cortinas translúcidas, pampas grass e vestido de linho em tom terra.",
        "cover": "/thumbnails/boho_chic.png",
        "camera": "35mm lens.",
        "scene": "Rustic interior, sheer white linen curtains, pampas grass in terracotta vase, dried floral wreaths.",
        "lighting": "Diffused natural window light from left, soft warm fill.",
        "outfit": "Flowing earth-tone crinkle linen maxi dress.",
        "pose": "Leaning against window frame, one hand on belly, dreamy gaze toward light.",
        "framing": "Three-quarter length.",
        "processing": "Color, warm sand and terracotta palette, natural cozy finish.",
    },

    "taupe_wings": {
        "name": "Asas de Chiffon Nude",
        "category": "Orgânicos & Sonhadores",
        "description": "Vestido de chiffon nude fluindo como asas com luz de softbox overhead, etéreo e poético.",
        "cover": "/thumbnails/image2.png",
        "camera": "50mm lens.",
        "scene": "Studio, light gray seamless backdrop.",
        "lighting": "Overhead softbox light, soft top-light on face, translucent fabric backlit.",
        "outfit": "Ultra-light deep taupe-nude chiffon gown with wide draped sleeves.",
        "pose": "Walking forward, fabric billowing like wings, serene expression, eyes slightly closed.",
        "framing": "Full body.",
        "processing": "Color, ethereal airy tones, translucent fabric effect.",
    },


    # ─── TEMÁTICOS & ESPECIAIS ──────────────────────────────────────

    "red_lotus": {
        "name": "Natal Aconchegante",
        "category": "Temáticos & Especiais",
        "description": "Sala de estar natalina com árvore iluminada, lareira acesa, sofá branco e pijama de seda vermelho.",
        "cover": "/thumbnails/red_lotus.png",
        "camera": "35mm lens.",
        "scene": "Cozy living room, lit Christmas tree with golden fairy lights, crackling fireplace, white plush sofa.",
        "lighting": "Warm amber firelight from right, golden fairy light glow, soft ambient fill.",
        "outfit": "Red silk pajamas.",
        "pose": "Seated in lotus on white sofa, hands on belly, genuine soft laugh.",
        "framing": "Three-quarter length.",
        "processing": "Color, warm amber and red candlelight tones, magical holiday warmth.",
    },
}

# ══════════════════════════════════════════════════════════════
# NEGATIVE PROMPT — reference only (not used by gpt-image-2)
# ══════════════════════════════════════════════════════════════
NEGATIVE_PROMPT = (
    "cgi, 3d render, cartoon, anime, illustration, painting, drawing, digital art, "
    "plastic skin, wax skin, over-retouched, heavy beauty filter, uncanny valley, "
    "different person, identity drift, altered face, face swap, morphed features, "
    "bad anatomy, deformed hands, extra fingers, floating limbs, "
    "unrealistic lighting, oversaturated, neon colors, fantasy elements, "
    "instagram filter, influencer aesthetic, stock photo look, ai artifacts."
)

# ══════════════════════════════════════════════════════════════
# PROMPT GENERATOR
# ══════════════════════════════════════════════════════════════
FALLBACK_STYLE = {
    "camera": "85mm lens.",
    "scene": "Professional maternity studio, neutral backdrop, pregnant woman standing.",
    "lighting": "Soft natural studio light from front, even fill.",
    "outfit": "Flowing maternity dress with soft fabric over the pregnant belly.",
    "pose": "Standing with hands on pregnant belly, warm expression toward camera.",
    "framing": "Three-quarter length.",
    "processing": "Color, professional finish.",
}

def generate_prompt(
    tipo_ensaio: str,
    subject_description: str = "",
    framing: Literal[
        "full_body", "three_quarters", "medium",
        "close_up_emotional", "detail_hands_belly", "silhouette"
    ] = None,
    pose_key: str = None,
    expression_key: str = None,
    lens_type: str = None,
    use_identity_text: bool = True,
) -> str:
    preset = STYLE_PRESETS.get(tipo_ensaio)
    if not preset:
        logger.warning(f"Unknown style '{tipo_ensaio}' — using fallback.")
        style = FALLBACK_STYLE
    else:
        style = preset

    if framing:
        framing_part = FRAMING_VARIANTS.get(framing, style["framing"])
    else:
        framing_part = style["framing"]

    if lens_type:
        lens_part = LENS_PRESETS.get(lens_type, style["camera"])
    else:
        lens_part = style["camera"]

    pose_parts = []
    if pose_key:
        pose_parts.append(POSE_LIBRARY.get(pose_key, style["pose"]))
    else:
        pose_parts.append(style["pose"])
    if expression_key:
        expr_text = EXPRESSION_LIBRARY.get(expression_key, "")
        if expr_text:
            pose_parts.append(expr_text)
    pose_part = ", ".join(pose_parts)

    parts = []
    if use_identity_text:
        parts.append(IDENTITY_TEXT)
    parts.append(QUALITY_BLOCK)
    parts.append(style["scene"])
    parts.append(style["lighting"])
    parts.append(style["outfit"])
    parts.append(pose_part)
    parts.append(framing_part)
    parts.append(lens_part)
    parts.append(style["processing"])
    if subject_description:
        parts.append(f"Subject: {subject_description}")

    final = " ".join(parts)
    final = " ".join(final.split())

    if len(final) > MAX_PROMPT_LENGTH:
        logger.warning(
            f"Prompt exceeded {MAX_PROMPT_LENGTH} chars ({len(final)}). Truncating."
        )
        final = final[:MAX_PROMPT_LENGTH].rstrip()

    logger.info(f"Prompt built: style='{tipo_ensaio}' | {len(final)} chars")
    return final


def generate_negative_prompt() -> str:
    return NEGATIVE_PROMPT


def get_available_styles() -> list:
    return [
        {
            "id": k,
            "name": v["name"],
            "category": v.get("category", ""),
            "description": v.get("description", ""),
            "cover": v.get("cover", ""),
        }
        for k, v in STYLE_PRESETS.items()
    ]
