import logging
from typing import Optional, Literal

# Configuração de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
# IDENTITY PRESERVATION (REALISTA - via referência externa)
# ══════════════════════════════════════════════════════════════
IDENTITY_PRESERVATION = (
    "The face must be a perfect match to the provided reference photo — identical bone structure, "
    "exact eye shape, same nose bridge, matching jawline contour, and identical lip proportions. "
    "Preserve the subject's unique skin tone including any natural undertones (warm, olive, cool). "
    "Maintain precise hairline, hair texture, and hair color as in the reference. "
    "Same body morphology: shoulder width, arm proportions, hand size, and authentic pregnant silhouette. "
    "The pregnant belly must look anatomically correct for the gestational stage — natural round shape, "
    "visible linea nigra if present, authentic skin stretch with subtle natural marks. "
    "The person must look unmistakably like themselves, never a generic model or idealized version. "
)

# ══════════════════════════════════════════════════════════════
# NATURALNESS & TEXTURE BOOSTER (Imperfeições Orgânicas)
# ══════════════════════════════════════════════════════════════
NATURALNESS_BOOSTER = (
    "Hyper-realistic skin with visible pores, fine peach fuzz, and micro-texture under directional light. "
    "Authentic pregnancy glow — slightly luminous skin with natural oil sheen on forehead and nose bridge. "
    "Subtle stretch marks on the belly rendered as organic silver or pink lines, never hidden. "
    "Visible veins on the belly and chest area as naturally occurs during pregnancy. "
    "Real fabric behavior: gravity-correct draping, natural creases where fabric meets skin, "
    "visible thread texture in lace or chiffon, authentic translucency in sheer materials. "
    "Genuine relaxed expression — soft asymmetrical smile, natural eye crinkles, unstaged emotion. "
    "Stray baby hairs at the hairline, imperfect flyaways catching the backlight. "
    "Hands with real knuckle detail, natural nail beds, visible tendons when cradling the belly. "
    "Absolutely no plastic skin, no porcelain smoothing, no uncanny valley artificiality. "
)

# ══════════════════════════════════════════════════════════════
# MOBILE QUALITY CORE (estética de smartphone topo de linha)
# ══════════════════════════════════════════════════════════════
QUALITY_CORE = (
    "Shot on iPhone 15 Pro Max in ProRAW mode, using the telephoto lens at 77mm equivalent (3x zoom), "
    "f/2.8 with natural computational bokeh. Smart HDR preserves every pore, hair strand, and fabric weave. "
    "Neutral color profile, no beauty filter, no artificial smoothing. "
    "The image looks exactly like a high-quality photo taken from a modern smartphone – "
    "slight natural lens distortion only at edges (not affecting face), realistic depth-of-field, "
    "authentic highlight roll-off and subtle shadow noise. "
    "No DSLR, no medium format, no cinematic anamorphic look. "
    "Pure mobile photography aesthetic: slightly cooler white balance, minimal chromatic aberration, "
    "natural grain in shadows, and that distinctive 'shot on iPhone' clarity and contrast. "
    "8K resolution output with smartphone characteristics, indistinguishable from a real mobile photo."
)

# ══════════════════════════════════════════════════════════════
# FRAMING VARIANTS (Controle de enquadramento)
# ══════════════════════════════════════════════════════════════
FRAMING_VARIANTS = {
    "full_body": (
        "Full-length composition at 4-5 meters, 77mm equivalent focal length, subject centered "
        "with breathing room above the head and below the feet. Full pregnant silhouette visible "
        "from crown to toes, slight three-quarter body angle to accentuate the belly curve. "
        "Professional studio distance — zero barrel distortion, natural body proportions preserved."
    ),
    "three_quarters": (
        "Three-quarter composition at 3 meters, framing from mid-thigh to just above the head. "
        "Slight low camera angle at belly height to emphasize the maternal silhouette. "
        "Subject turned 30-40 degrees from camera with face toward lens. "
        "Belly prominently featured in the mid-frame with hands naturally resting on it."
    ),
    "medium": (
        "Medium shot at 2.5 meters, waist-up composition with the belly curve as the visual anchor. "
        "Tight enough to capture the emotion in the eyes while showing the cradling gesture. "
        "Shallow depth of field blurs lower frame, attention drawn to face and hands on belly."
    ),
    "close_up_emotional": (
        "Intimate chest-up portrait at 1.5 meters, shot at 77mm for flattering compression. "
        "Face fills the upper frame, soft focus on the shoulder and collarbone area. "
        "Catchlights visible in the eyes, gentle downward gaze toward the belly. "
        "Emotional and tender expression, never posed or stiff. No selfie angle whatsoever."
    ),
    "detail_hands_belly": (
        "Macro-intimate detail shot focused on hands cradling the pregnant belly. "
        "Shot at f/2.8 with shallow depth of field — fingers tack-sharp, belly skin softly blurred. "
        "Visible skin texture, natural nail detail, authentic finger placement with gentle pressure dimples. "
        "Rim light catching the peach fuzz on the belly surface. Tender, quiet, reverent mood."
    ),
}

# ══════════════════════════════════════════════════════════════
# STYLE PRESETS (todos ajustados para estética mobile)
# ══════════════════════════════════════════════════════════════
STYLE_PRESETS = {
    "luxury_studio": {
        "name": "Luxury Studio",
        "category": "Clássico",
        "description": "Fundo neutro, iluminação de estúdio profissional e elegância atemporal.",
        "cover": "https://images.unsplash.com/photo-1544126592-807daa2b565b?auto=format&fit=crop&q=80&w=600",
        "prompt": (
            "Award-winning luxury studio maternity portrait captured on smartphone. "
            "Seamless dove-gray paper backdrop with subtle gradient falloff to darker edges. "
            "Clamshell lighting setup: large 150cm octabox directly above at 45 degrees as key light, "
            "white bounce fill below chin, accent strip light from behind camera-right creating a delicate "
            "rim glow along the belly curve and shoulder line. "
            "Subject wearing a flowing ivory silk organza gown with long cathedral train pooling on the floor, "
            "fabric catching light with natural luster and subtle translucency over the belly. "
            "Hands gently cradling the lower belly, fingers relaxed and naturally spread. "
            "Soft butterfly shadow under the nose, catchlights in both eyes. "
            "Warm neutral color palette: cream, taupe, champagne, and brushed gold accents. "
            "Composition with generous negative space, subject placed on the golden ratio intersection. "
            "Mobile fine art portrait, clean and crisp smartphone aesthetic. "
            "8K resolution, tack-sharp focus, museum print quality, masterpiece."
        ),
    },
    "golden_hour_nature": {
        "name": "Golden Hour Nature",
        "category": "Natureza",
        "description": "Campo aberto com a luz mágica do pôr do sol.",
        "cover": "https://images.unsplash.com/photo-1594434296621-507bc67a78c1?auto=format&fit=crop&q=80&w=600",
        "prompt": (
            "Breathtaking outdoor maternity portrait shot on a smartphone in a vast open wildflower meadow during the final "
            "20 minutes of golden hour. Rich amber and honey-toned directional sunlight coming from behind "
            "the subject at a low angle, creating a luminous backlit halo around the hair and a warm glow "
            "through the sheer fabric of a flowing maxi dress in dusty rose or soft terracotta. "
            "Natural lens flare streaking gently across the frame, soft circular bokeh from wildflowers "
            "and tall grass in the foreground and background. "
            "Subject standing in a relaxed contrapposto pose, one hand beneath the belly, "
            "the other gently touching the hair or resting at the side. Wind softly moving the dress "
            "and hair, creating organic motion and life in the frame. "
            "Rolling hills or gentle tree line visible in the far background, slightly out of focus. "
            "Color-graded with warm lifted shadows, desaturated greens, and rich golden skin tones. "
            "Cinematic depth of field using smartphone telephoto lens, maximum subject isolation. "
            "Professional outdoor editorial maternity photography, National Geographic portrait quality."
        ),
    },
    "boho_chic": {
        "name": "Boho Chic",
        "category": "Artístico",
        "description": "Decoração rústica, flores secas e tons pastéis.",
        "cover": "https://images.unsplash.com/photo-1583939003579-730e3918a45a?auto=format&fit=crop&q=80&w=600",
        "prompt": (
            "Artistic bohemian maternity portrait captured on smartphone in a carefully styled indoor set. "
            "Warm natural window light streaming through sheer linen curtains, creating soft diffused "
            "illumination with gentle directional shadows. "
            "Abundant dried floral arrangements: pampas grass plumes in tall ceramic vases, dried eucalyptus "
            "garlands, preserved roses in muted blush and dusty mauve tones, scattered dried lavender. "
            "Subject wearing a hand-crocheted or macramé crop top paired with a flowing earth-toned skirt, "
            "bare pregnant belly prominently visible between the pieces. "
            "Layered boho accessories: delicate gold body chain draping over the belly, stacked thin rings, "
            "a woven flower crown with dried baby's breath and small roses. "
            "Background elements: woven jute rug, raw wood textures, hanging macramé wall art, "
            "a vintage rattan peacock chair. "
            "Muted earthy color palette: warm sand, terracotta, sage green, dusty pink, and antique cream. "
            "Soft painterly quality to the light, reminiscent of a Renaissance Madonna painting. "
            "Shot on smartphone telephoto lens (77mm equivalent) with natural depth-of-field, no artificial blur. "
            "High-resolution fine art maternity photography with a handcrafted artisanal aesthetic."
        ),
    },
    "black_white_editorial": {
        "name": "Black & White Editorial",
        "category": "Vogue Style",
        "description": "Alto contraste, estilo revista de moda.",
        "cover": "https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&q=80&w=600",
        "prompt": (
            "High-fashion black and white editorial maternity portrait for Vogue or Harper's Bazaar cover, shot on smartphone. "
            "Dramatic Rembrandt lighting with a single hard key light through a 30-degree grid at 45 degrees "
            "camera-left, casting a sharp triangular highlight on the shadow-side cheek. "
            "Deep rich blacks and clean bright whites with a full zone-system tonal range. "
            "Subject in a sculptural minimalist outfit: either a tailored black bodysuit that hugs the belly, "
            "or elegant draped black silk charmeuse creating strong geometric folds. "
            "Powerful confident pose — chin slightly raised, shoulders back, one hand on hip, "
            "the other placed firmly on the side of the belly. Strong S-curve body line. "
            "Stark minimalist background: pure solid seamless paper, either deep black or bright white, "
            "creating maximum figure-ground separation. "
            "Fine silver gelatin print aesthetic with rich analog film grain, deep contrast, and luminous "
            "skin highlights. Inspired by Herb Ritts, Peter Lindbergh, and Irving Penn. "
            "High-resolution mobile photography, natural contrast, authentic black and white from computational processing. "
            "Powerful maternal elegance, iconic and timeless."
        ),
    },
    "classic": {
        "name": "Clássico",
        "category": "Clássico",
        "description": "Estilo clássico com iluminação suave e cenário neutro.",
        "cover": "https://picsum.photos/seed/classic/600/800",
        "prompt": (
            "Clássico fotografia de maternidade em estúdio com iluminação suave, fundo neutro, foco nítido no rosto e barriga, cores naturais e elegantes. "
            "Capturado com smartphone de alta qualidade, sem retoques artificiais."
        ),
    },
    "bw": {
        "name": "Preto e Branco",
        "category": "Preto e Branco",
        "description": "Estilo em preto e branco com alto contraste e iluminação dramática.",
        "cover": "https://picsum.photos/seed/bw/600/800",
        "prompt": (
            "Fotografia de maternidade em preto e branco com iluminação dramática, sombras marcadas, alto contraste, elegância atemporal. "
            "Estilo mobile editorial, sem granulação de filme médio formato."
        ),
    },
    "nature": {
        "name": "Natureza",
        "category": "Natureza",
        "description": "Cenário natural ao ar livre, luz do sol dourada.",
        "cover": "https://picsum.photos/seed/nature/600/800",
        "prompt": (
            "Fotografia de maternidade ao ar livre em cenário natural, luz dourada do fim da tarde, fundo de campo de flores silvestres. "
            "Foto tirada com smartphone, profundidade de campo natural, cores realistas."
        ),
    },
    "minimalist": {
        "name": "Minimalista",
        "category": "Minimalista",
        "description": "Estilo minimalista com fundo limpo e foco no sujeito.",
        "cover": "https://picsum.photos/seed/minimalist/600/800",
        "prompt": (
            "Fotografia de maternidade minimalista com fundo branco liso, iluminação suave, foco no rosto e barriga, simplicidade elegante. "
            "Qualidade de smartphone premium, sem exageros de nitidez."
        ),
    },
    "romantic": {
        "name": "Romântico",
        "category": "Romântico",
        "description": "Atmosfera romântica com luz suave e tons pastel.",
        "cover": "https://picsum.photos/seed/romantic/600/800",
        "prompt": (
            "Fotografia de maternidade romântica com luz suave, tons pastel, fundo delicado, atmosfera de carinho e intimidade. "
            "Captura mobile com leve desfoque natural, pele texturizada realista."
        ),
    },
    "urban": {
        "name": "Urbano",
        "category": "Urbano",
        "description": "Cenário urbano contemporâneo com grafites e iluminação de rua.",
        "cover": "https://picsum.photos/seed/urban/600/800",
        "prompt": (
            "Fotografia de maternidade urbana com fundo de cidade, grafite artístico, iluminação de rua noturna, estilo contemporâneo. "
            "Foto de smartphone com alta faixa dinâmica, ruído natural em sombras."
        ),
    },
}

# ══════════════════════════════════════════════════════════════
# NEGATIVE PROMPT (Filtro Anti-IA e Anti-Retoque + bloqueio DSLR)
# ══════════════════════════════════════════════════════════════
NEGATIVE_PROMPT = (
    "cartoon, anime, 3d render, cgi, illustration, painting, drawing, sketch, digital art, "
    "airbrushed skin, plastic texture, fake skin, over-smoothed, porcelain doll skin, wax figure, "
    "bad anatomy, deformed limbs, extra fingers, mutated hands, fused fingers, missing fingers, "
    "anatomically incorrect belly shape, unrealistic pregnancy proportions, "
    "distorted belly button, floating hands, disconnected limbs, "
    "harsh shadows, neon colors, oversaturated, over-sharpened, HDR artifacts, "
    "low resolution, blurry, out of focus, motion blur, jpeg artifacts, pixelated, "
    "watermark, text, logo, signature, copyright stamp, date stamp, "
    "selfie style, wide angle distortion, fisheye, cheap studio look, on-camera flash, "
    "stiff mannequin pose, T-pose, generic beauty filter, excessive retouching, "
    "perfectly symmetrical face, doll-like features, uncanny valley, dead eyes, "
    "visible AI artifacts, seam lines, inconsistent lighting direction, "
    "multiple light sources casting contradictory shadows, "
    "stock photo aesthetic, clip art, corporate headshot style, "
    "nudity, nsfw, inappropriate content, suggestive pose, "
    "dslr bokeh, medium format grain, cinematic anamorphic flare, studio strobe harshness, "
    "canon colors, fujifilm simulation, leica look, pro mist filter, anamorphic lens flare."
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
    """Gera um prompt completo e otimizado para ensaios fotográficos realistas com estética mobile."""
    
    preset = STYLE_PRESETS.get(tipo_ensaio)

    if not preset:
        logger.warning(f"Unknown tipo_ensaio: {tipo_ensaio}, using fallback")
        scene_prompt = "Professional but natural portrait photography. Soft natural light, real skin texture. Shot on smartphone."
    else:
        scene_prompt = preset["prompt"]

    parts = []

    # 1. Identidade (Reflexo da referência)
    if use_identity_text:
        parts.append(IDENTITY_PRESERVATION)

    # 2. Enquadramento
    parts.append(FRAMING_VARIANTS.get(framing, FRAMING_VARIANTS["full_body"]))

    # 3. Cena principal
    parts.append(scene_prompt)

    # 4. Descrição do sujeito
    if subject_description:
        parts.append(subject_description)

    # 5. Naturalidade (Boost de texturas)
    if use_naturalness_booster:
        parts.append(NATURALNESS_BOOSTER)

    # 6. Qualidade Mobile (Core)
    parts.append(QUALITY_CORE)

    final_prompt = " ".join(parts)
    logger.info(f"Prompt gerado com sucesso para o estilo: {tipo_ensaio}")
    return final_prompt

def generate_negative_prompt() -> str:
    """Retorna o negative prompt universal atualizado."""
    return NEGATIVE_PROMPT

# ══════════════════════════════════════════════════════════════
# FUNÇÕES DE UTILIDADE PARA FRONTEND / INTERFACE
# ══════════════════════════════════════════════════════════════

def get_available_styles() -> list:
    """
    Retorna a lista de estilos disponíveis com nomes amigáveis 
    para preencher menus de seleção no frontend.
    """
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
    """
    Retorna as opções de enquadramento disponíveis para o usuário escolher.
    """
    return [
        {
            "id": key, 
            "name": key.replace("_", " ").title(), 
            "description": val.split(".")[0]  # Pega apenas a primeira frase da descrição técnica
        }
        for key, val in FRAMING_VARIANTS.items()
    ]

# ══════════════════════════════════════════════════════════════
# EXEMPLO DE EXECUÇÃO
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Exemplo: Gerando um ensaio do estilo Luxury Studio com estética mobile
    meu_prompt = generate_prompt(
        tipo_ensaio="luxury_studio",
        subject_description="",
        framing="full_body"
    )
    
    print("--- POSITIVE PROMPT ---")
    print(meu_prompt)
    print("\n--- NEGATIVE PROMPT ---")
    print(generate_negative_prompt())

    # Listagem de estilos disponíveis
    print("\nESTILOS DISPONÍVEIS NO SISTEMA:")
    for style in get_available_styles():
        print(f"- {style['name']} (ID: {style['id']})")
        
    print("\n" + "="*80)