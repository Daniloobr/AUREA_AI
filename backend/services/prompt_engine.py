"""
AUREA AI — Premium Maternity Photography Prompt Engine
=======================================================
Optimized for openai/gpt-image-2 via Replicate with 3 reference photos.

Engineering Principles:
  1. Identity anchor once at the START — no repetition.
  2. Concrete visual facts only: scene, lighting, outfit, pose, framing, processing.
  3. Camera/lens language activates photorealistic behavior.
  4. No vague adjectives ("beautiful", "elegant", "stunning").
  5. Prompts ≤ 550 chars to ensure full delivery.
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
MAX_PROMPT_LENGTH = 600

# ══════════════════════════════════════════════════════════════
# IDENTITY — single sentence, placed once at prompt start
# ══════════════════════════════════════════════════════════════
IDENTITY_TEXT = "Preserve exact identity from the 3 reference photos: same face, skin, body."

# ══════════════════════════════════════════════════════════════
# LENS PRESETS — override library (backward compat)
# ══════════════════════════════════════════════════════════════
LENS_PRESETS = {
    "portrait":    "85mm lens, natural compression, soft background.",
    "cinematic":   "50mm lens, cinematic depth of field.",
    "wide":        "35mm lens, environmental context.",
    "telephoto":   "135mm lens, background compression, subject isolation.",
    "close":       "100mm macro, intimate detail, sharp focus on face.",
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
        "cover": "/thumbnails/luxury_studio.png",
        "camera": "135mm lens.",
        "scene": "Studio, black marble backdrop and floor.",
        "lighting": "Warm golden rim light from behind right, soft front fill.",
        "outfit": "Deep burgundy velvet gown with floor-length train.",
        "pose": "Standing in profile, hands on belly, composed editorial expression.",
        "framing": "Full body.",
        "processing": "Color, opulent warm tones, rich velvet texture.",
    },

    "editorial_black_blazer": {
        "name": "Editorial Blazer & Mesh",
        "category": "Editoriais Vogue",
        "description": "Blazer charcoal, body de tule preto transparente, barriga à mostra, calça pantalona e joias douradas.",
        "cover": "/thumbnails/black_white_editorial.png",
        "camera": "85mm lens.",
        "scene": "Studio, muted olive-khaki grey gradient backdrop.",
        "lighting": "Front diffused warm studio light, soft spotlight on belly.",
        "outfit": "Oversized charcoal blazer off-shoulder, sheer black mesh top, high-waist wide-leg black trousers, gold jewelry.",
        "pose": "Standing facing camera, hands cupped under belly, calm serene expression.",
        "framing": "Three-quarter length.",
        "processing": "Color, warm desaturated tones, editorial fashion grade.",
    },

    "seated_cube_editorial": {
        "name": "Cubo Branco Editorial",
        "category": "Editoriais Vogue",
        "description": "Sentada em cubo branco matte, blazer preto, top cropped, calça pantalona e sandália plataforma.",
        "cover": "/thumbnails/vestidoBlack.png",
        "camera": "35mm lens.",
        "scene": "Studio, warm dark taupe-mocha gradient backdrop, light polished floor.",
        "lighting": "Front-left warm diffused studio light, subtle floor spotlight.",
        "outfit": "Open long black blazer, scalloped black crop top, high-waist wide-leg black trousers, beige platform sandals, silver jewelry.",
        "pose": "Seated sideways on matte white cube, legs crossed at ankle, torso turned toward camera, calm gaze off-camera.",
        "framing": "Full body.",
        "processing": "Color, sophisticated warm tones, modern editorial finish.",
    },

    "bw_silhouette_profile": {
        "name": "P&B Silhueta Artística",
        "category": "Editoriais Vogue",
        "description": "Perfil puro a 90 graus mostrando silhueta da barriga, vestido bodycon preto gola rulê, P&B alto contraste.",
        "cover": "/thumbnails/black_white_editorial.png",
        "camera": "50mm lens.",
        "scene": "Studio, neutral grey gradient backdrop.",
        "lighting": "Front-left diffuse studio light, soft sculpting shadows along body.",
        "outfit": "Sleek black turtleneck bodycon maxi dress, long sleeves, matte stretch fabric.",
        "pose": "Pure 90-degree side profile, slight back arch accentuating belly curve, one hand on belly front, other on lower back.",
        "framing": "Full body.",
        "processing": "Black and white, high contrast, fine art monochrome.",
    },

    # ─── ORGÂNICOS & SONHADORES ─────────────────────────────────────

    "golden_hour_nature": {
        "name": "Pôr do Sol na Natureza",
        "category": "Orgânicos & Sonhadores",
        "description": "Campo aberto de flores silvestres ao pôr do sol com luz dourada lateral e vestido fluido rosa antigo.",
        "cover": "/thumbnails/golden_hour_nature.png",
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

    # ─── AO AR LIVRE & NATUREZA ─────────────────────────────────────

    "forest_fairy": {
        "name": "Floresta Encantada",
        "category": "Ao Ar Livre & Natureza",
        "description": "Floresta densa com raios de luz solar, musgo, samambaias e vestido de renda off-white etéreo.",
        "cover": "/thumbnails/classic.png",
        "camera": "85mm lens.",
        "scene": "Dense forest, tall trees, moss-covered ground, ferns, wildflowers.",
        "lighting": "Dappled sunlight breaking through canopy, volumetric light shafts.",
        "outfit": "Off-white lace boho gown with long sleeves.",
        "pose": "Standing among ferns, one hand touching hair, other on belly, serene expression.",
        "framing": "Full body.",
        "processing": "Color, soft green and warm gold tones, natural forest atmosphere.",
    },

    "beach_sunrise": {
        "name": "Praia ao Amanhecer",
        "category": "Ao Ar Livre & Natureza",
        "description": "Praia deserta ao amanhecer com luz rosada do horizonte, vestido branco fluido e pés descalços.",
        "cover": "/thumbnails/golden_hour_nature.png",
        "camera": "35mm lens.",
        "scene": "Empty sandy beach at sunrise, wet sand reflecting sky.",
        "lighting": "Warm pink-orange sunrise light from horizon, backlighting silhouette.",
        "outfit": "Flowing white organza dress touching sand, bare feet.",
        "pose": "Standing in profile at water edge, hands on belly, serene expression, eyes slightly closed.",
        "framing": "Full body.",
        "processing": "Color, warm pastel pink and gold tones, soft sunrise glow.",
    },

    "lavender_fields": {
        "name": "Campo de Lavanda",
        "category": "Ao Ar Livre & Natureza",
        "description": "Campos infinitos de lavanda roxa ao entardecer com vestido lavanda coordenado e buquê de lavanda.",
        "cover": "/thumbnails/boho_chic.png",
        "camera": "85mm lens.",
        "scene": "Endless rows of purple lavender under soft blue sky.",
        "lighting": "Warm afternoon sunlight, soft golden glow.",
        "outfit": "Flowing dusty lavender chiffon maxi dress, holding fresh lavender bouquet.",
        "pose": "Walking through lavender rows, one hand holding bouquet, other on belly, warm smile.",
        "framing": "Three-quarter length.",
        "processing": "Color, pastel purple and sage palette, romantic Provence tones.",
    },

    # ─── AMBIENTES ÍNTIMOS & ELEGANTES ──────────────────────────────

    "paris_balcony": {
        "name": "Varanda Parisiense",
        "category": "Ambientes Elegantes",
        "description": "Varanda parisiense com grades de ferro forjado, flores brancas e vista de telhados ao fundo.",
        "cover": "/thumbnails/luxury_studio.png",
        "camera": "50mm lens.",
        "scene": "Parisian balcony, ornate wrought-iron railing with white roses and ivy, Paris rooftops visible.",
        "lighting": "Soft morning light from left, rooftops in soft bokeh background.",
        "outfit": "Champagne silk slip dress.",
        "pose": "Leaning on railing, one hand on belly, dreamy gaze toward the view.",
        "framing": "Three-quarter length.",
        "processing": "Color, warm golden morning palette, romantic European elegance.",
    },

    "luxury_bedroom": {
        "name": "Quarto Luxuoso",
        "category": "Ambientes Elegantes",
        "description": "Quarto de hotel luxuoso com cama king-size linho branco, peônias, cortinas de voile e robe de seda.",
        "cover": "/thumbnails/image3.png",
        "camera": "100mm lens.",
        "scene": "Luxury hotel bedroom, king bed with white linen, white peonies on nightstand, sheer curtains.",
        "lighting": "Warm morning window light diffused through sheer voile curtains.",
        "outfit": "Silk cream robe open to reveal belly.",
        "pose": "Seated on edge of bed, one hand on belly, looking down at belly with love, soft smile.",
        "framing": "Medium waist-up portrait.",
        "processing": "Color, warm 3200K intimate tones, soft shadow detail.",
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
    "scene": "Professional studio, neutral backdrop.",
    "lighting": "Soft natural studio light from front.",
    "outfit": "Flowing elegant maternity dress.",
    "pose": "Standing with hands on belly, warm expression toward camera.",
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
