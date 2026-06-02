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

    # ─── NOVOS ESTILOS ADICIONADOS ─────────────────────────────────

    "tropical_dusk": {
        "name": "Tropical Dusk",
        "category": "Ao Ar Livre & Natureza",
        "description": "Joelhos na areia molhada, água na altura dos joelhos, floresta tropical ao fundo, vestido creme com aplicações florais 3D, serenidade e romance.",
        "cover": "/thumbnails/tropical_dusk.png",
        "camera": "Medium format camera, 85mm portrait lens, shallow depth of field.",
        "scene": "Tropical beach at dusk. Kneeling on wet sand at shoreline, shallow water lapping around knees, lush dense tropical palm tree forest as backdrop, clear soft blue dusk sky.",
        "lighting": "Natural ambient blue hour light. Even soft frontal ambient light, cool-toned, soft, low contrast, film-like quality. Soft shadows, warm skin contrast against cool background.",
        "outfit": "Cream/off-white fitted spaghetti strap maternity midi dress. Textured knit or crochet-like fabric, V-neckline, form-fitting. 3D floral appliqué rosettes scattered on skirt, hem resting on wet sand.",
        "pose": "Kneeling upright on both knees on wet sand, side profile with 3/4 turn toward camera, head tilted back with eyes closed, serene expression. One arm wrapped around top of bump, other hand on lower bump, back slightly arched.",
        "framing": "Full length kneeling figure with tropical background, sand and water in foreground.",
        "processing": "Color, slightly desaturated, film grain, cool-warm contrast, analog/film aesthetic. Subject sharp, background palm trees softly blurred.",
    },

    "ocean_goddess": {
        "name": "Ocean Goddess",
        "category": "Ao Ar Livre & Natureza",
        "description": "Em pé na água até a cintura em mar calmo, tecido branco flutuando na superfície, céu nublado dramático. Poderosa, etérea, primal.",
        "cover": "/thumbnails/ocean_goddess.png",
        "camera": "Medium format camera, 85mm portrait lens, shallow depth of field.",
        "scene": "Open ocean / calm sea, standing in waist-deep water. Fabric floating and spreading on water surface, vast open calm sea extending to horizon. Overcast moody sky, soft grey and white clouds.",
        "lighting": "Natural diffused overcast daylight. Even all-around soft light, flat, cool-toned, no harsh shadows. Moody ethereal atmosphere, no specular highlights.",
        "outfit": "Pure white draped fabric / strapless wrap. Lightweight semi-sheer chiffon or muslin, loosely draped and wrapped around the body, strapless. Fabric flows freely into water, floating and spreading. Wet fabric clinging to bump, translucent revealing baby bump beneath.",
        "pose": "3/4 front angle, standing in water, head dramatically tilted back with eyes closed, chin raised toward sky. One arm crossing chest holding draped fabric, other arm extended back with hand on lower back/hip, body arched slightly backward.",
        "framing": "Upper body to water level, vast sky occupying upper third.",
        "processing": "Color, desaturated cool tones, moody and cinematic, slight film quality. Subject sharp, background ocean softly blurred.",
    },

    "golden_couple": {
        "name": "Golden Couple",
        "category": "Ao Ar Livre & Natureza",
        "description": "Casal sentado à beira do lago ao pôr do sol, luz dourada intensa, vestido branco, colete jeans amarrado na frente, barriga exposta. Romântico e cinematográfico.",
        "cover": "/thumbnails/golden_couple.png",
        "camera": "Medium format camera, 85mm portrait lens, shallow depth of field.",
        "scene": "Lakeside at golden hour sunset. Sitting on grassy ground at water's edge, natural vegetation and reeds, silhouetted tree line on horizon, calm reflective water surface. Dramatic golden sunset sky with wispy streaked clouds.",
        "lighting": "Natural golden hour backlight. Intense warm golden rim light from behind, high contrast. Hair dramatically lit, strong rim lighting outlining body, golden reflections on water, lens flare from sun.",
        "outfit": "Denim halter crop vest open front tied with bow, sides open exposing bare bump. White/cream flowy maxi skirt, lightweight chiffon, pooling on ground.",
        "pose": "Seated on ground facing away from camera at 3/4 back angle, turned slightly to side with soft smile visible in profile. One hand resting on bump, legs to the side, relaxed and intimate. Male partner partially visible on left edge (arm/torso).",
        "framing": "Upper body to ground, vast sky and water in background.",
        "processing": "Color, warm and golden, high contrast, cinematic tones. Subject in focus, background landscape slightly soft.",
    },

    "cream_profile": {
        "name": "Cream Profile",
        "category": "Ao Ar Livre & Natureza",
        "description": "Perfil puro na praia ao entardecer, vestido longo justo creme, mãos na barriga, sorriso suave. Íntimo e cinematográfico.",
        "cover": "/thumbnails/cream_profile.png",
        "camera": "Medium format camera, 85mm portrait lens, shallow depth of field.",
        "scene": "Ocean beach at sunset/dusk. Standing on wet sand at shoreline, ocean waves crashing in background. Soft pastel sunset sky, pale peach and cream tones.",
        "lighting": "Natural ambient dusk light. Soft wrap-around light from horizon behind, very soft, low contrast, moody. Warm rim light on hair and shoulders, overall cool-warm mixed tones.",
        "outfit": "Cream/off-white form-fitting long sleeve maternity gown. Smooth matte stretch jersey or ribbed knit, body-hugging, long sleeves, scoop or boat neckline, floor-length fitted skirt, no slit.",
        "pose": "Pure side profile, standing still, head turned very slightly with soft gentle smile. Both hands cradling baby bump from below and side, relaxed and natural stance.",
        "framing": "Medium to full body, ocean background bokeh/soft blur.",
        "processing": "Color, moody and desaturated, cool-warm contrast, film-like grain, low light aesthetic. Subject sharp, background ocean softly blurred.",
    },

    "sunset_silhouette": {
        "name": "Sunset Silhouette",
        "category": "Ao Ar Livre & Natureza",
        "description": "De costas para o sol ao pôr do sol na praia, vestido branco, raios solares dramáticos, semi-silhueta. Épico e cinematográfico.",
        "cover": "/thumbnails/sunset_silhouette.png",
        "camera": "Medium format camera, 85mm portrait lens, shallow depth of field.",
        "scene": "Ocean beach at golden hour sunset. Standing in shallow ocean water, small waves around ankles, wet sand visible, rocky outcrops and distant figures on horizon. Dramatic sky with deep vivid blue, white and golden clouds, brilliant orange and golden sun rays bursting from horizon.",
        "lighting": "Natural golden hour sunlight directly from behind (backlit). Intense warm golden light creating strong rim light and silhouette effect. Sun rays radiating through clouds (crepuscular rays), golden reflections on wet sand and water.",
        "outfit": "White/off-white midi/maxi sundress. Lightweight cotton or linen, tiered or flowy, spaghetti straps, fitted bodice, hem wet from ocean water.",
        "pose": "Back facing camera completely, standing still in shallow water, head slightly bowed or in profile. Both hands cradling baby bump from the sides, silhouetted against sunset.",
        "framing": "Full length with vast sky occupying top 60% of frame, subject centered in lower third.",
        "processing": "Color, highly saturated, cinematic, warm golden tones with deep blue sky contrast. Subject slightly silhouetted, background sunset in sharp dramatic detail.",
    },

    # ─── NOVOS ESTILOS (TORCEDORA, BOUQUÊ, USG, MONOCROMÁTICO) ─────

    "sports_fan": {
        "name": "Torcedora Fanática",
        "category": "Temáticos & Especiais",
        "description": "Gestante usando camisa de time cropped e calça jeans, segurando miniatura da mesma camisa. Casual, divertido e patriótico.",
        "cover": "/thumbnails/sports_fan.png",
        "camera": "Medium format camera, 85mm portrait lens, shallow depth of field.",
        "scene": "Simple clean light grey/white wall background, minimal and casual, no studio setup.",
        "lighting": "Natural or soft indoor lighting, even ambient light from front, bright, clean, casual, no dramatic shadows.",
        "outfit": "Bright canary yellow cropped sports jersey (short sleeve, V-neck, green collar trim, blue sleeve stripe), low-rise light wash denim jeans unbuttoned below belly. Bump fully exposed.",
        "pose": "Pure side profile, standing naturally, head turned slightly to look at a tiny yellow baby jersey held up with both hands raised in front, gaze focused on the small jersey, casual and playful mood.",
        "framing": "Upper body to mid-thigh.",
        "processing": "Color, bright and clean, natural tones, slight warmth.",
    },

    "baby_breath_bouquet": {
        "name": "Bouquet de Nuvem",
        "category": "Ambientes Elegantes",
        "description": "Estúdio escuro e dramático, buquê gigante de gipsófila cobrindo o peito, barriga nua exposta, iluminação Rembrandt, atmosfera de pintura clássica.",
        "cover": "/thumbnails/baby_breath_bouquet.png",
        "camera": "Medium format camera, 85mm portrait lens, shallow depth of field.",
        "scene": "Dark moody studio with deep charcoal/dark olive grey seamless background, no floor visible.",
        "lighting": "Dramatic Rembrandt-style studio lighting. Single key light from upper front-left, high contrast, warm-toned, painterly. Strong directional light illuminating face, bouquet and bump, deep shadows on right side and background.",
        "outfit": "Blush pink / nude rose silky satin draped fabric from just below bump downward, floor-length. No top garment — bare chest and décolletage covered only by bouquet. Strapless low-cut wrap.",
        "pose": "3/4 front angle, slight body twist, head bowed downward with eyes closed and soft smile. Holding a large oversized pure white baby's breath bouquet pressed against the chest covering it, other hand on lower back/hip. Bump prominently exposed below bouquet.",
        "framing": "Upper body portrait, bouquet as central element.",
        "processing": "Color, warm and moody, dark shadows, rich tones, painterly quality reminiscent of Old Masters.",
    },

    "ultrasound_projection": {
        "name": "Projeção do Bebê",
        "category": "Temáticos & Especiais",
        "description": "Gestante ajoelhada em estúdio com projeção gigante de ultrassom na parede, vestido preto com recorte lateral, P&B. Terno e íntimo.",
        "cover": "/thumbnails/ultrasound_projection.png",
        "camera": "Medium format camera, 85mm portrait lens, shallow depth of field.",
        "scene": "Minimalist studio with large baby ultrasound/sonogram image projected onto light grey seamless background wall. Projection soft glowing white-grey, slightly blurred, baby profile visible, massive filling entire wall.",
        "lighting": "Soft studio lighting combined with projector light. Front key light, projector from behind/above. Soft contrast, clean and even. Projection creates subtle glow on hair and shoulders.",
        "outfit": "Solid black sleeveless fitted maternity dress with side cut-out window at waist exposing bare skin. Scoop neckline, thick shoulder straps, floor-length fitted skirt. Bump visible through cut-out.",
        "pose": "Kneeling on both knees on the floor, seated back on heels, pure side profile. Head bowed downward looking at bump with soft tender smile. One hand gently resting on top of bump, other hand cradling bump from below.",
        "framing": "Full body from head to floor, large ultrasound projection dominating background.",
        "processing": "Black and white, clean monochrome, moderate contrast, soft tones. Subject sharp, projection soft and glowing.",
    },

    "monochromatic_blue": {
        "name": "Azul Monocromático",
        "category": "Editoriais Vogue",
        "description": "Gestante ajoelhada em fundo azul céu, vestido azul exato ao fundo, painel de tecido voando fundindo-se ao cenário. Buquê de rosas brancas. Surreal e editorial.",
        "cover": "/thumbnails/monochromatic_blue.png",
        "camera": "Medium format camera, 85mm portrait lens, shallow depth of field.",
        "scene": "Flat solid sky blue / powder blue seamless studio background, bright and even, floor same color creating infinite look.",
        "lighting": "Bright even studio lighting. Front-centered, fully even, bright, flat, clean, no shadows.",
        "outfit": "Powder blue strapless fitted maternity gown with dramatic flying fabric panel. Strapless bandeau bodice, form-fitting. Attached extremely long flowing fabric panel frozen mid-air sweeping upward and to the right in large fluid wave shapes. Fabric matches background color exactly, creating surreal seamless effect.",
        "pose": "Kneeling on both knees on floor, seated back on heels, body turned slightly to side at 3/4 angle. Head bowed downward with warm joyful smile. Both arms hugging a large bouquet of white roses pressed against chest/bump, long stems visible hanging down.",
        "framing": "Full body with dramatic flying fabric extending to upper right corner.",
        "processing": "Color, bright and saturated, clean blue tones, slight airbrushed finish. Monochromatic concept: dress and background same color, flying fabric blends into background.",
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
