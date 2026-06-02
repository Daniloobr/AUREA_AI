"""
AUREA AI — Premium Maternity Photography Prompt Engine
=======================================================
Optimized for openai/gpt-image-2 via Replicate with 3 reference photos.

Engineering Principles (GPT-Image-2 best practices):
  1. Identity anchor at the START and END of every prompt — combats identity drift.
  2. Concrete visual facts: lighting direction, color palette, fabric texture, set details.
  3. Camera/lens language activates photorealistic rendering behavior.
  4. Avoid negatives ("no", "don't") — describe what IS there instead.
  5. Keep prompts ≤ 580 chars to avoid truncation before identity anchor.
  6. Each style must feel like a real, premium editorial shoot — not stock photography.

Context:
  - Subject: pregnant woman (gestante), belly visible and celebrated.
  - Input: 3 natural photos of the real woman uploaded by the user.
  - Output: a produced, beautiful maternity photoshoot image.
"""

import logging
from typing import Literal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
# GLOBAL CONFIG
# ══════════════════════════════════════════════════════════════
MAX_PROMPT_LENGTH = 1200


# ══════════════════════════════════════════════════════════════
# IDENTITY ANCHORS — placed at start and end of every prompt
# to minimize identity drift in gpt-image-2
# ══════════════════════════════════════════════════════════════
IDENTITY_OPEN = (
    "Photorealistic maternity portrait. "
    "Preserve exact identity from the 3 reference photos: same face, skin tone, hair, body. "
)

IDENTITY_CLOSE = (
    "Same woman as reference photos. Pregnant belly clearly visible."
)


# ══════════════════════════════════════════════════════════════
# LENS PRESETS — short, technical, activates realism mode
# ══════════════════════════════════════════════════════════════
LENS_PRESETS = {
    "portrait":    "Shot on 85mm f/1.8, natural compression, silky background blur.",
    "cinematic":   "Shot on 50mm f/2, cinematic depth of field, film grain.",
    "wide":        "Shot on 35mm f/2.8, environmental context, editorial framing.",
    "telephoto":   "Shot on 135mm f/2, extreme background compression, subject isolation.",
    "close":       "Shot on 100mm macro, intimate detail, razor-sharp focus on face.",
}


# ══════════════════════════════════════════════════════════════
# EXPRESSIONS — specific, emotionally resonant
# ══════════════════════════════════════════════════════════════
EXPRESSION_LIBRARY = {
    "warm":           "gentle radiant smile, eyes soft and full of joy.",
    "serene":         "calm peaceful expression, eyes slightly closed in contentment.",
    "editorial":      "composed introspective look, chin slightly lowered, gaze distant.",
    "laughing":       "genuine candid laugh, head tilted back naturally.",
    "tender_belly":   "looking down at the belly with pure love, soft gentle smile.",
    "window_dream":   "gazing toward soft light, dreamy faraway expression.",
    "proud":          "proud confident gaze toward camera, empowered expression.",
}


# ══════════════════════════════════════════════════════════════
# POSES — elegant, natural maternity poses
# ══════════════════════════════════════════════════════════════
POSE_LIBRARY = {
    "front_cradle":     "facing camera, both hands cupped gently under the belly.",
    "side_profile":     "standing in soft profile, belly silhouette beautifully visible.",
    "walking_natural":  "mid-stride, natural movement, flowing fabric in gentle motion.",
    "window_lean":      "leaning softly against window frame, one hand on belly.",
    "seated_grace":     "seated elegantly, one hand on belly, the other relaxed.",
    "hair_belly":       "one hand lightly touching hair, other hand on belly.",
    "looking_down":     "standing tall, looking tenderly down at the belly.",
}


# ══════════════════════════════════════════════════════════════
# FRAMING VARIANTS
# ══════════════════════════════════════════════════════════════
FRAMING_VARIANTS = {
    "full_body":          "full body composition, floor to crown, elegant proportions.",
    "three_quarters":     "three-quarter shot from knees up, belly naturally centered.",
    "medium":             "medium portrait from waist up, emotional intimacy.",
    "close_up_emotional": "tight portrait, face fills frame, emotion in every detail.",
    "detail_hands_belly": "close detail of hands resting on belly, bokeh background.",
    "silhouette":         "dramatic side silhouette, belly and figure outlined by backlight.",
}


# ══════════════════════════════════════════════════════════════
# STYLE PRESETS — 15 premium environments
# Each prompt is crafted to:
#   - describe the PHYSICAL SET (colors, textures, objects, light source)
#   - describe the OUTFIT in concrete terms
#   - use LIGHTING language a photographer would recognize
# ══════════════════════════════════════════════════════════════
STYLE_PRESETS = {

    # ─── CLÁSSICOS ATEMPORAIS ─────────────────────────────────────────────────
    "classic_studio": {
        "name": "Estúdio Clássico",
        "category": "Clássicos Atemporais",
        "description": "Um retrato clássico em estúdio com fundo neutro cinza-pérola, iluminação suave de dois softboxes que esculpem a silhueta da gestante. Vestido de musselina fluida em branco gelo. Atemporal e elegante.",
        "cover": "/thumbnails/classic.png",
        "lens": "portrait",
        "pose": "front_cradle",
        "expression": "warm",
        "framing": "three_quarters",
        "prompt": (
            "High-end maternity studio portrait. Pearl-gray seamless backdrop. "
            "Two large softbox lights: one main at 45° left, one fill from right. "
            "She wears a flowing white muslin wrap dress with natural folds. "
            "Skin lit evenly, warm ivory tones. Clean professional photography."
        ),
    },

    "luxury_studio": {
        "name": "Estúdio Luxo Couture",
        "category": "Clássicos Atemporais",
        "description": "Estúdio luxuoso com fundo degradê cinza-pomba, iluminação de rim que realça a silhueta e um vestido de seda marfim com decote elegante. Sofisticação de alta costura.",
        "cover": "/thumbnails/luxury_studio.png",
        "lens": "cinematic",
        "pose": "side_profile",
        "expression": "editorial",
        "framing": "full_body",
        "prompt": (
            "Luxury couture maternity portrait. Dove-gray gradient studio backdrop. "
            "Rim light outlining her silhouette in warm gold. Front soft fill light. "
            "She wears a backless ivory silk gown with long train pooling on the floor. "
            "Polished concrete floor reflecting her silhouette. Vogue editorial quality."
        ),
    },

    "ivory_satin": {
        "name": "Cetim Imperial",
        "category": "Clássicos Atemporais",
        "description": "Vestido imperial de cetim marfim, sem costas, cauda longa sobre piso polido refletido. Iluminação lateral dramática que realça a textura sedosa. Cinematográfico e atemporal.",
        "cover": "/thumbnails/image3.png",
        "lens": "telephoto",
        "pose": "side_profile",
        "expression": "serene",
        "framing": "full_body",
        "prompt": (
            "Imperial maternity portrait. Ivory satin backless gown with a long train. "
            "Side directional light source from the right casting elegant shadows. "
            "Highly reflective polished white marble floor. Dark gray studio backdrop. "
            "Fabric texture crisp, satin sheen catching the light. Fine art photograph."
        ),
    },

    # ─── EDITORIAIS VOGUE ─────────────────────────────────────────────────────
    "black_white_editorial": {
        "name": "Preto & Branco Editorial",
        "category": "Editoriais Vogue",
        "description": "Editorial monocromático de alto contraste estilo Vogue. Luz dramática esculpindo o corpo. Granulação de filme analógico. Sombras profundas, realces nítidos. Intemporal.",
        "cover": "/thumbnails/black_white_editorial.png",
        "lens": "cinematic",
        "pose": "side_profile",
        "expression": "editorial",
        "framing": "full_body",
        "prompt": (
            "Black and white fine art maternity portrait, Vogue editorial style. "
            "Single dramatic side light from the left, deep shadows, bright highlights. "
            "Rich tonal range from near-black to crisp white. Subtle film grain texture. "
            "She wears a flowing black silk chiffon gown. Seamless dark backdrop. "
            "Timeless monochrome, high contrast, museum quality print."
        ),
    },

    "dramatic_black_gown": {
        "name": "Vestido Preto Dramático",
        "category": "Editoriais Vogue",
        "description": "Vestido longo preto sem costas com cauda. Iluminação Chiaroscuro lateral sobre piso escuro polido. Composição marcante e poderosa. Sombras profundas e elegantes.",
        "cover": "/thumbnails/vestidoBlack.png",
        "lens": "cinematic",
        "pose": "side_profile",
        "expression": "proud",
        "framing": "full_body",
        "prompt": (
            "Dramatic Chiaroscuro maternity portrait. She wears an elegant backless "
            "black velvet gown with a long trailing skirt. Single strong side light "
            "from left, creating bold shadow on one half of the body. "
            "Highly polished dark floor reflecting her silhouette. Black backdrop. "
            "Cinematic power, bold editorial composition."
        ),
    },

    "red_velvet": {
        "name": "Veludo Borgonha",
        "category": "Editoriais Vogue",
        "description": "Vestido longo de veludo borgonha com cauda dramática. Fundo escuro de mármore preto. Iluminação quente de rim em dourado que realça o tecido rico. Intensidade editorial.",
        "cover": "/thumbnails/luxury_studio.png",
        "lens": "telephoto",
        "pose": "side_profile",
        "expression": "editorial",
        "framing": "full_body",
        "prompt": (
            "Editorial maternity portrait. She wears a deep burgundy velvet gown "
            "with dramatic floor-length train. Warm golden rim light from behind right. "
            "Soft front fill preserving face detail. Black marble floor and backdrop. "
            "Rich velvet texture catching the warm rim light. Opulent, magazine editorial."
        ),
    },

    "editorial_black_blazer": {
        "name": "Editorial Blazer & Mesh",
        "category": "Editoriais Vogue",
        "description": "Estúdio minimalista com fundo degradê verde-oliva acinzentado. Blazer charcoal largo drapeado nos ombros sobre body de tule preto transparente revelando a barriga nua. Calça pantalona preta e joias douradas. Luz frontal difusa com destaque suave na barriga. Joyful, confiante, editorial.",
        "cover": "/thumbnails/black_white_editorial.png",
        "lens": "portrait",
        "pose": "front_cradle",
        "expression": "serene",
        "framing": "three_quarters",
        "prompt": (
            "Modern editorial maternity studio portrait. Muted olive-khaki grey gradient backdrop. "
            "She wears an oversized charcoal blazer draped loosely off-shoulder, "
            "sheer black mesh turtleneck bodysuit with bare pregnant belly visible through fabric, "
            "solid black bralette underneath, high-waist wide-leg black trousers. "
            "Delicate gold layered necklaces, crystal statement earrings, gold rings. "
            "Front-centered diffused warm studio light, subtle warm spotlight on belly. "
            "Warm-toned slightly desaturated color grade. Joyful, confident, chic, empowered editorial."
        ),
    },

    "seated_cube_editorial": {
        "name": "Cubo Branco Editorial",
        "category": "Editoriais Vogue",
        "description": "Estúdio com fundo degradê taupe-moca escuro e piso claro. Gestante sentada de lado em um cubo branco matte, pernas cruzadas no tornozelo, blazer longo preto aberto, top cropped com barra scalloped, calça pantalona preta e sandália plataforma bege. Joias prata. Sofisticado e moderno.",
        "cover": "/thumbnails/vestidoBlack.png",
        "lens": "wide",
        "pose": "seated_grace",
        "expression": "editorial",
        "framing": "full_body",
        "prompt": (
            "Modern editorial maternity studio portrait. Warm dark taupe-mocha gradient backdrop, "
            "light polished floor. Large matte white cube prop used as seat. "
            "She sits sideways on the cube, legs crossed at ankle, torso turned toward camera, "
            "gaze directed calmly off to the side. Open-front long black blazer/duster, "
            "scalloped-edge black crop bralette, high-waist wide-leg black trousers, "
            "beige chunky platform open-toe sandals. Delicate silver layered necklaces, silver rings. "
            "Front-left warm diffused studio light, subtle floor spotlight, gentle background vignette. "
            "Sophisticated, calm, modern editorial mood."
        ),
    },

    "bw_silhouette_profile": {
        "name": "P&B Silhueta Artística",
        "category": "Editoriais Vogue",
        "description": "Arte fotográfica em preto e branco de alto contraste. Perfil puro a 90° mostrando a silhueta da barriga. Vestido bodycon preto de gola rulê manga longa, body-hugging. Leve arqueamento nas costas acentuando a curva da barriga. Luz lateral esculpindo as formas. Elegante, atemporal, poderoso.",
        "cover": "/thumbnails/black_white_editorial.png",
        "lens": "cinematic",
        "pose": "side_profile",
        "expression": "editorial",
        "framing": "full_body",
        "prompt": (
            "Fine art maternity portrait, pure 90-degree side profile. "
            "Neutral grey gradient studio backdrop. "
            "She wears a form-fitting sleek black turtleneck bodycon maxi dress, "
            "long sleeves, smooth matte stretch fabric, no embellishments, body-hugging silhouette. "
            "One hand gently resting on belly from front, other hand on lower back, "
            "slight arch in the back accentuating the belly curve. "
            "Front-left diffused studio light creating soft sculpting shadows along the body. "
            "Processed in high contrast black and white monochrome. Elegant, timeless, powerful."
        ),
    },

    # ─── ORGÂNICOS & SONHADORES ───────────────────────────────────────────────

    "golden_hour_nature": {
        "name": "Pôr do Sol na Natureza",
        "category": "Orgânicos & Sonhadores",
        "description": "Campo aberto de flores silvestres ao pôr do sol. Luz dourada lateral banhando a gestante. Vestido fluido rosa antigo. Bokeh suave de flores desfocadas. Mágico e caloroso.",
        "cover": "/thumbnails/golden_hour_nature.png",
        "lens": "portrait",
        "pose": "walking_natural",
        "expression": "warm",
        "framing": "full_body",
        "prompt": (
            "Outdoor maternity portrait at golden hour. Open wildflower meadow: "
            "lavender, chamomile, and poppies in the foreground, soft bokeh background. "
            "Warm orange-gold sunlight from the right side bathing her face and body. "
            "She wears a flowing dusty rose chiffon maxi dress in gentle motion. "
            "Lens flare, warm 4500K color grade. Real outdoor natural beauty."
        ),
    },

    "boho_chic": {
        "name": "Boho Chic Rústico",
        "category": "Orgânicos & Sonhadores",
        "description": "Interior rústico com cortinas translúcidas brancas, pampas grass em vaso de barro, cobertor de tricô em tom areia. Luz natural filtrada suave. Aconchego e autenticidade.",
        "cover": "/thumbnails/boho_chic.png",
        "lens": "wide",
        "pose": "window_lean",
        "expression": "window_dream",
        "framing": "three_quarters",
        "prompt": (
            "Bohemian maternity portrait indoors. Sheer white linen curtains diffusing "
            "natural window light from the left. Pampas grass in a terracotta vase, "
            "dried floral wreaths, macramé wall hanging visible in background. "
            "She wears a flowing earth-tone crinkle linen maxi dress. "
            "Warm sand and terracotta color palette. Cozy, authentic, editorial boho."
        ),
    },

    "taupe_wings": {
        "name": "Asas de Chiffon Nude",
        "category": "Orgânicos & Sonhadores",
        "description": "Vestido de chiffon nude fluindo como asas em movimento. Fundo cinza suave. Luz de softbox overhead. Tecido ultra-leve capturado em movimento etéreo. Sonhador e poético.",
        "cover": "/thumbnails/image2.png",
        "lens": "cinematic",
        "pose": "walking_natural",
        "expression": "serene",
        "framing": "full_body",
        "prompt": (
            "Ethereal maternity portrait. She wears an ultra-light deep taupe-nude "
            "chiffon gown with wide draped sleeves flowing like wings in gentle motion. "
            "Overhead softbox light from above, creating soft top-light on her face. "
            "Light gray seamless backdrop. Fabric billowing naturally, translucent where "
            "backlit. Dreamy, otherworldly, poetic maternity art."
        ),
    },

    # ─── AO AR LIVRE & NATUREZA ───────────────────────────────────────────────
    "forest_fairy": {
        "name": "Floresta Encantada",
        "category": "Ao Ar Livre & Natureza",
        "description": "Floresta densa com raios de luz solar entre as árvores. Musgo verde, samambaias, raízes expostas. Vestido de renda off-white etéreo. Atmosfera de fada da floresta.",
        "cover": "/thumbnails/classic.png",
        "lens": "portrait",
        "pose": "hair_belly",
        "expression": "serene",
        "framing": "full_body",
        "prompt": (
            "Enchanted forest maternity portrait. Dense green forest: tall trees, "
            "dappled sunlight breaking through canopy, moss-covered ground, "
            "ferns and wild flowers at her feet. Volumetric light shafts from above. "
            "She wears an ethereal off-white lace boho gown with long sleeves. "
            "Soft green and warm gold tones. Fairy tale atmosphere."
        ),
    },

    "beach_sunrise": {
        "name": "Praia ao Amanhecer",
        "category": "Ao Ar Livre & Natureza",
        "description": "Praia deserta ao amanhecer com areia fina dourada e ondas suaves. Luz rosada e dourada do horizonte. Vestido branco fluido que toca a areia. Pés descalços. Livre e poderosa.",
        "cover": "/thumbnails/golden_hour_nature.png",
        "lens": "wide",
        "pose": "side_profile",
        "expression": "serene",
        "framing": "full_body",
        "prompt": (
            "Beach maternity portrait at sunrise. Empty sandy beach, wet sand "
            "reflecting pink and gold sky, gentle waves in background. "
            "Warm pink-orange sunrise light from the horizon backlighting her silhouette. "
            "She wears a flowing white organza dress touching the sand, bare feet. "
            "Fresh ocean breeze moving fabric. Freedom, power, natural beauty."
        ),
    },

    "lavender_fields": {
        "name": "Campo de Lavanda",
        "category": "Ao Ar Livre & Natureza",
        "description": "Campos infinitos de lavanda roxa sob céu azul suave. Luz de tarde quente. Vestido lavanda coordenado. Buquê de lavanda fresca nas mãos. Provence romântico e sonhador.",
        "cover": "/thumbnails/boho_chic.png",
        "lens": "portrait",
        "pose": "walking_natural",
        "expression": "warm",
        "framing": "three_quarters",
        "prompt": (
            "Lavender field maternity portrait. Endless rows of purple lavender "
            "stretching to the horizon, soft blue sky, warm afternoon sunlight. "
            "She wears a flowing dusty lavender chiffon maxi dress. "
            "Holding a loose bouquet of fresh lavender in one hand, "
            "other hand gently on belly. Bees and butterflies in soft bokeh. "
            "Romantic Provence atmosphere, pastel purple and sage palette."
        ),
    },

    # ─── AMBIENTES ÍNTIMOS & ELEGANTES ───────────────────────────────────────
    "paris_balcony": {
        "name": "Varanda Parisiense",
        "category": "Ambientes Elegantes",
        "description": "Varanda parisiense com grades de ferro forjado e flores brancas. Vista de telhados da cidade ao fundo. Vestido de seda champagne. Luz natural matinal. Elegância europeia.",
        "cover": "/thumbnails/luxury_studio.png",
        "lens": "cinematic",
        "pose": "window_lean",
        "expression": "window_dream",
        "framing": "three_quarters",
        "prompt": (
            "Parisian balcony maternity portrait. Ornate wrought-iron railing with "
            "white roses and ivy. Soft morning light from the left. Paris rooftops "
            "visible in soft bokeh background. She wears a champagne silk slip dress. "
            "Fresh flowers on railing, vintage bistro chair visible. "
            "Romantic European elegance, warm golden morning palette."
        ),
    },

    "luxury_bedroom": {
        "name": "Quarto Luxuoso",
        "category": "Ambientes Elegantes",
        "description": "Quarto de hotel de luxo com cama king-size de linho branco, cortinas de voile brancas filtrando luz natural. Flores de peônia brancas. Robe de seda creme. Íntimo e requintado.",
        "cover": "/thumbnails/image3.png",
        "lens": "close",
        "pose": "seated_grace",
        "expression": "tender_belly",
        "framing": "medium",
        "prompt": (
            "Intimate luxury bedroom maternity portrait. King-size bed with crisp "
            "white linen sheets, large white peony bouquet on nightstand, "
            "sheer white voile curtains diffusing warm morning window light. "
            "She wears a silk cream robe open to reveal the belly, seated elegantly "
            "on the edge of the bed. Soft shadows, warm 3200K light. "
            "Hotel suite intimacy, quiet tenderness."
        ),
    },

    # ─── TEMÁTICOS & ESPECIAIS ────────────────────────────────────────────────
    "red_lotus": {
        "name": "Natal Aconchegante",
        "category": "Temáticos & Especiais",
        "description": "Sala de estar aconchegante no Natal. Árvore iluminada com pisca-piscas dourados. Lareira acesa. Sofá branco. Pijama de seda vermelho. Pipoca. Magia natalina calorosa.",
        "cover": "/thumbnails/red_lotus.png",
        "lens": "wide",
        "pose": "seated_grace",
        "expression": "laughing",
        "framing": "three_quarters",
        "prompt": (
            "Cozy Christmas maternity portrait. Living room scene: lit Christmas tree "
            "with warm golden fairy lights, crackling fireplace glow from the right. "
            "White plush sofa with cream knit throw. She sits in lotus position "
            "wearing red silk pajamas, popcorn bowl on lap. "
            "Warm amber and red candlelight tones. Magical holiday warmth."
        ),
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
    """
    Assembles a full generation prompt for gpt-image-2.

    Priority:
      1. Caller-provided overrides (framing, pose, expression, lens).
      2. Style preset defaults.
      3. Global fallbacks.
    """
    preset = STYLE_PRESETS.get(tipo_ensaio)
    if not preset:
        logger.warning(f"Unknown style '{tipo_ensaio}' — using fallback.")
        style_prompt = "Professional maternity portrait in a beautiful natural setting."
        _framing  = FRAMING_VARIANTS["three_quarters"]
        _pose     = POSE_LIBRARY["front_cradle"]
        _expr     = EXPRESSION_LIBRARY["warm"]
        _lens     = LENS_PRESETS["portrait"]
    else:
        style_prompt = preset["prompt"]
        _framing  = FRAMING_VARIANTS.get(framing or preset.get("framing", "three_quarters"),
                                          FRAMING_VARIANTS["three_quarters"])
        _pose     = POSE_LIBRARY.get(pose_key or preset.get("pose", "front_cradle"),
                                      POSE_LIBRARY["front_cradle"])
        _expr     = EXPRESSION_LIBRARY.get(expression_key or preset.get("expression", "warm"),
                                            EXPRESSION_LIBRARY["warm"])
        _lens     = LENS_PRESETS.get(lens_type or preset.get("lens", "portrait"),
                                      LENS_PRESETS["portrait"])

    parts = []

    # 1. Identity anchor — OPEN (most important, gpt-image-2 reads first)
    if use_identity_text:
        parts.append(IDENTITY_OPEN)

    # 2. Style — the physical set, outfit, and lighting
    parts.append(style_prompt)

    # 3. Composition details
    parts.append(_framing)
    parts.append(_pose)
    parts.append(_expr)

    # 4. Optional subject details from user input
    if subject_description:
        parts.append(f"Additional details: {subject_description}")

    # 5. Technical lens info
    parts.append(_lens)

    # 6. Identity anchor — CLOSE (reinforces at end, combats drift on long prompts)
    if use_identity_text:
        parts.append(IDENTITY_CLOSE)

    final_prompt = " ".join(parts)
    # Normalize whitespace
    final_prompt = " ".join(final_prompt.split())

    if len(final_prompt) > MAX_PROMPT_LENGTH:
        logger.warning(
            f"Prompt exceeded {MAX_PROMPT_LENGTH} chars ({len(final_prompt)}). Truncating."
        )
        final_prompt = final_prompt[:MAX_PROMPT_LENGTH].rstrip()

    logger.info(f"Prompt built: style='{tipo_ensaio}' | {len(final_prompt)} chars")
    return final_prompt


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
