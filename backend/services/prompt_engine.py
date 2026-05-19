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
# Bloco único de preservação de identidade. Prepended a todo
# prompt para garantir que o modelo use as 3 fotos de referência
# como fonte de verdade absoluta para rosto e corpo.
# ══════════════════════════════════════════════════════════════
IDENTITY_ANCHOR = (
    "The client has uploaded 3 reference photos of herself. "
    "Your PRIMARY TASK is to preserve the identity of this exact person. "
    "The generated image MUST use the SAME FACE from the reference photos — "
    "do not modify, beautify, idealize, or change facial features in any way. "
    "Identity preservation is more important than style, lighting, or composition. "
    "If there is any conflict between aesthetics and identity, ALWAYS prioritize identity. "
    "Same bone structure, same eyes, same nose, same lips, same skin tone, same hairline. "
    "Do not change ethnicity, facial structure, or age. No beauty filters or symmetry corrections. "
    "The body should look natural and consistent with a pregnant woman. "
    "Use the reference images as the sole source of truth for the face — "
    "the face must remain consistent under all conditions, angles, lighting, and expressions. "
)

# ══════════════════════════════════════════════════════════════
# SMARTPHONE QUALITY CORE — "shot on a high-end smartphone"
# ══════════════════════════════════════════════════════════════
QUALITY_CORE = (
    "Shot on a high-end smartphone. "
    "The image must look indistinguishable from a real photograph taken on a flagship phone — "
    "natural computational bokeh, authentic depth-of-field, realistic highlight roll-off, "
    "subtle shadow noise, and that distinctive smartphone clarity and sharpness. "
    "Hyper-realistic skin: visible pores, fine peach fuzz, real skin texture under natural light. "
    "No DSLR look, no medium-format grain, no cinematic anamorphic flare. "
    "No beauty filter, no artificial smoothing, no porcelain-doll skin. "
    "Natural color science, true-to-life white balance. "
    "Ultra high resolution, 8K quality, photorealistic, indistinguishable from a real mobile photo."
)

# ══════════════════════════════════════════════════════════════
# NATURALNESS BOOSTER (Imperfeições Orgânicas)
# ══════════════════════════════════════════════════════════════
NATURALNESS_BOOSTER = (
    "Authentic pregnancy glow — slightly luminous skin with natural oil sheen on forehead and nose bridge. "
    "Subtle stretch marks on the belly rendered as organic silver or pink lines, never hidden. "
    "Real fabric behavior: gravity-correct draping, natural creases where fabric meets skin. "
    "Genuine relaxed expression — soft natural smile, real eye crinkles, unstaged emotion. "
    "Stray baby hairs at the hairline catching the light. "
    "Hands with real knuckle detail, natural nail beds, visible tendons when cradling the belly. "
    "Absolutely no plastic skin, no uncanny valley artificiality, no AI artifacts."
)

# ══════════════════════════════════════════════════════════════
# FRAMING VARIANTS
# ══════════════════════════════════════════════════════════════
FRAMING_VARIANTS = {
    "full_body": (
        "Full-length composition, subject centered with breathing room above the head and below the feet. "
        "Full pregnant silhouette visible from crown to toes, slight three-quarter body angle "
        "to accentuate the belly curve. Natural body proportions preserved, zero barrel distortion."
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
        "Shallow depth of field blurs lower frame, attention drawn to face and hands on belly."
    ),
    "close_up_emotional": (
        "Intimate chest-up portrait, face fills the upper frame. "
        "Soft focus on the shoulder and collarbone area. "
        "Catchlights visible in the eyes, gentle downward gaze toward the belly. "
        "Emotional and tender expression, never posed or stiff."
    ),
    "detail_hands_belly": (
        "Macro-intimate detail shot focused on hands cradling the pregnant belly. "
        "Fingers tack-sharp, belly skin softly blurred behind. "
        "Visible skin texture, natural nail detail, authentic finger placement with gentle pressure dimples. "
        "Rim light catching the peach fuzz on the belly surface. Tender, quiet, reverent mood."
    ),
}

# ══════════════════════════════════════════════════════════════
# STYLE PRESETS — Otimizados para google/nano-banana-pro
# Cada prompt inclui a instrução de fidelidade às 3 fotos
# e a estética "shot on a high-end smartphone".
# ══════════════════════════════════════════════════════════════
STYLE_PRESETS = {
    "luxury_studio": {
        "name": "Luxury Studio",
        "category": "Clássico",
        "description": "Fundo neutro, iluminação de estúdio profissional e elegância atemporal.",
        "cover": "https://images.unsplash.com/photo-1544126592-807daa2b565b?auto=format&fit=crop&q=80&w=600",
        "prompt": (
            "A stunning luxury studio maternity portrait of a pregnant woman — "
            "the SAME woman from the 3 reference photos the client uploaded. "
            "Seamless dove-gray paper backdrop with subtle gradient falloff to darker edges. "
            "Professional clamshell lighting: large octabox above at 45 degrees as key light, "
            "white bounce fill below chin, delicate rim glow along the belly curve and shoulder line. "
            "She wears a flowing ivory silk organza gown with a long train pooling on the floor, "
            "fabric catching light with natural luster and subtle translucency over the belly. "
            "Hands gently cradling the lower belly, fingers relaxed and naturally spread. "
            "Soft butterfly shadow under the nose, catchlights in both eyes. "
            "Warm neutral color palette: cream, taupe, champagne, and brushed gold accents. "
            "Generous negative space, subject placed on the golden ratio intersection. "
            "Shot on a high-end smartphone, photorealistic, 8K resolution, museum print quality."
        ),
    },
    "golden_hour_nature": {
        "name": "Golden Hour Nature",
        "category": "Natureza",
        "description": "Campo aberto com a luz mágica do pôr do sol.",
        "cover": "https://images.unsplash.com/photo-1594434296621-507bc67a78c1?auto=format&fit=crop&q=80&w=600",
        "prompt": (
            "A breathtaking outdoor maternity portrait of a pregnant woman — "
            "the SAME woman from the 3 reference photos the client uploaded. "
            "Vast open wildflower meadow during the last 20 minutes of golden hour. "
            "Rich amber and honey-toned directional sunlight coming from behind the subject, "
            "creating a luminous backlit halo around the hair and a warm glow through "
            "the sheer fabric of her flowing maxi dress in dusty rose or soft terracotta. "
            "Natural lens flare streaking gently across the frame, soft circular bokeh "
            "from wildflowers and tall grass in the foreground and background. "
            "Relaxed contrapposto pose, one hand beneath the belly, the other gently touching the hair. "
            "Wind softly moving the dress and hair, creating organic motion. "
            "Rolling hills or gentle tree line in the far background, slightly out of focus. "
            "Warm lifted shadows, desaturated greens, rich golden skin tones. "
            "Shot on a high-end smartphone, photorealistic, 8K resolution, editorial outdoor quality."
        ),
    },
    "boho_chic": {
        "name": "Boho Chic",
        "category": "Artístico",
        "description": "Decoração rústica, flores secas e tons pastéis.",
        "cover": "https://images.unsplash.com/photo-1583939003579-730e3918a45a?auto=format&fit=crop&q=80&w=600",
        "prompt": (
            "An artistic bohemian maternity portrait of a pregnant woman — "
            "the SAME woman from the 3 reference photos the client uploaded. "
            "Warm natural window light streaming through sheer linen curtains, "
            "creating soft diffused illumination with gentle directional shadows. "
            "Abundant dried floral arrangements: pampas grass plumes, dried eucalyptus garlands, "
            "preserved roses in muted blush and dusty mauve, scattered dried lavender. "
            "She wears a hand-crocheted or macramé crop top paired with a flowing earth-toned skirt, "
            "bare pregnant belly prominently visible between the pieces. "
            "Layered boho accessories: delicate gold body chain over the belly, stacked thin rings, "
            "a woven flower crown with dried baby's breath and small roses. "
            "Background: woven jute rug, raw wood textures, hanging macramé wall art, vintage rattan chair. "
            "Muted earthy palette: warm sand, terracotta, sage green, dusty pink, antique cream. "
            "Soft painterly quality to the light, reminiscent of a Renaissance Madonna. "
            "Shot on a high-end smartphone, photorealistic, 8K resolution, fine art aesthetic."
        ),
    },
    "black_white_editorial": {
        "name": "Black & White Editorial",
        "category": "Vogue Style",
        "description": "Alto contraste, estilo revista de moda.",
        "cover": "https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&q=80&w=600",
        "prompt": (
            "A high-fashion black and white editorial maternity portrait of a pregnant woman — "
            "the SAME woman from the 3 reference photos the client uploaded. "
            "Dramatic Rembrandt lighting with a single hard key light at 45 degrees camera-left, "
            "casting a sharp triangular highlight on the shadow-side cheek. "
            "Deep rich blacks and clean bright whites with a full tonal range. "
            "She wears a sculptural minimalist outfit: tailored black bodysuit hugging the belly, "
            "or elegant draped black silk charmeuse creating strong geometric folds. "
            "Powerful confident pose — chin slightly raised, shoulders back, one hand on hip, "
            "the other placed firmly on the side of the belly. Strong S-curve body line. "
            "Stark minimalist background: pure solid seamless paper, either deep black or bright white, "
            "creating maximum figure-ground separation. "
            "Fine silver gelatin print aesthetic with rich analog film grain and deep contrast. "
            "Inspired by Herb Ritts, Peter Lindbergh, and Irving Penn. "
            "Shot on a high-end smartphone, photorealistic, 8K resolution, iconic and timeless."
        ),
    },
    "classic": {
        "name": "Clássico",
        "category": "Clássico",
        "description": "Estilo clássico com iluminação suave e cenário neutro.",
        "cover": "https://picsum.photos/seed/classic/600/800",
        "prompt": (
            "A classic maternity studio portrait of a pregnant woman — "
            "the SAME woman from the 3 reference photos the client uploaded. "
            "Soft even studio lighting, neutral warm-toned backdrop, sharp focus on the face and belly. "
            "Elegant and timeless composition, natural colors, gentle expression. "
            "She wears a simple flowing white or cream dress that drapes naturally over the belly. "
            "Hands cradling the belly, relaxed shoulders, warm genuine smile. "
            "No heavy retouching, real skin texture, authentic pregnancy glow. "
            "Shot on a high-end smartphone, photorealistic, 8K resolution."
        ),
    },
    "bw": {
        "name": "Preto e Branco",
        "category": "Preto e Branco",
        "description": "Estilo em preto e branco com alto contraste e iluminação dramática.",
        "cover": "https://picsum.photos/seed/bw/600/800",
        "prompt": (
            "A dramatic black and white maternity portrait of a pregnant woman — "
            "the SAME woman from the 3 reference photos the client uploaded. "
            "High contrast, deep shadows, bright highlights, bold tonal separation. "
            "Dramatic side lighting sculpting the belly curve and facial features. "
            "Timeless elegance, powerful maternal silhouette, raw emotional depth. "
            "Real skin texture preserved in the monochrome conversion, authentic grain. "
            "Shot on a high-end smartphone, photorealistic, 8K resolution, editorial quality."
        ),
    },
    "nature": {
        "name": "Natureza",
        "category": "Natureza",
        "description": "Cenário natural ao ar livre, luz do sol dourada.",
        "cover": "https://picsum.photos/seed/nature/600/800",
        "prompt": (
            "A beautiful outdoor maternity portrait of a pregnant woman in nature — "
            "the SAME woman from the 3 reference photos the client uploaded. "
            "Natural setting: a sunlit clearing in a lush green forest, or a field of wildflowers. "
            "Golden afternoon sunlight filtering through tree leaves, dappled light on her skin. "
            "She wears a flowing floral or earth-toned dress, barefoot on soft grass. "
            "Natural depth of field, background softly blurred with green and golden tones. "
            "Peaceful expression, hands on belly, connected to nature. Real skin, real colors. "
            "Shot on a high-end smartphone, photorealistic, 8K resolution."
        ),
    },
    "minimalist": {
        "name": "Minimalista",
        "category": "Minimalista",
        "description": "Estilo minimalista com fundo limpo e foco no sujeito.",
        "cover": "https://picsum.photos/seed/minimalist/600/800",
        "prompt": (
            "A minimalist maternity portrait of a pregnant woman — "
            "the SAME woman from the 3 reference photos the client uploaded. "
            "Clean solid white background, simple soft lighting, zero distractions. "
            "She wears a minimal neutral outfit — a form-fitting bodysuit or simple cotton wrap — "
            "that highlights the belly silhouette without competing for attention. "
            "Composition focuses purely on the belly curve, her face, and her hands. "
            "Negative space dominates the frame, elegant simplicity, quiet beauty. "
            "Real skin texture, no retouching, authentic pregnancy glow. "
            "Shot on a high-end smartphone, photorealistic, 8K resolution."
        ),
    },
    "romantic": {
        "name": "Romântico",
        "category": "Romântico",
        "description": "Atmosfera romântica com luz suave e tons pastel.",
        "cover": "https://picsum.photos/seed/romantic/600/800",
        "prompt": (
            "A romantic maternity portrait of a pregnant woman — "
            "the SAME woman from the 3 reference photos the client uploaded. "
            "Soft diffused light, warm pastel tones: blush pink, lavender, soft peach, champagne. "
            "Dreamy atmosphere with delicate fabric — sheer tulle or chiffon — floating around her. "
            "Fresh flowers: peonies, garden roses, or baby's breath arranged nearby or held gently. "
            "Intimate and tender expression, eyes soft, gentle smile, one hand on belly. "
            "Background has a soft ethereal blur with warm pastel hues. "
            "Real skin texture, natural pregnancy glow, authentic emotion. "
            "Shot on a high-end smartphone, photorealistic, 8K resolution."
        ),
    },
    "urban": {
        "name": "Urbano",
        "category": "Urbano",
        "description": "Cenário urbano contemporâneo com grafites e iluminação de rua.",
        "cover": "https://picsum.photos/seed/urban/600/800",
        "prompt": (
            "A contemporary urban maternity portrait of a pregnant woman — "
            "the SAME woman from the 3 reference photos the client uploaded. "
            "City setting: textured concrete wall with artistic graffiti mural behind her, "
            "or a modern architectural backdrop with clean lines and glass reflections. "
            "Golden hour street light mixed with warm artificial neon glow. "
            "She wears a stylish modern outfit — leather jacket over a fitted dress, or trendy streetwear — "
            "that shows off the belly with urban confidence and attitude. "
            "Strong pose, direct gaze to camera, empowered maternal energy. "
            "Real skin texture, natural city lighting, authentic atmosphere. "
            "Shot on a high-end smartphone, photorealistic, 8K resolution, street photography style."
        ),
    },
}

# ══════════════════════════════════════════════════════════════
# NEGATIVE PROMPT — Otimizado para Imagen 4 Ultra
# (Imagen 4 Ultra não usa negative_prompt nativamente,
#  mas mantemos para uso interno de filtragem/logging)
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
    "nudity, nsfw, inappropriate content, suggestive pose."
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
    """
    Gera um prompt completo e otimizado para google/nano-banana-pro.
    
    Ordem dos componentes:
    1. IDENTITY_ANCHOR — preservação de identidade (prioridade máxima)
    2. Prompt do estilo (scene_prompt)
    3. Enquadramento (framing)
    4. Descrição física do sujeito (se fornecida)
    5. NATURALNESS_BOOSTER
    6. QUALITY_CORE
    """
    
    preset = STYLE_PRESETS.get(tipo_ensaio)

    if not preset:
        logger.warning(f"Unknown tipo_ensaio: {tipo_ensaio}, using fallback")
        scene_prompt = (
            "A beautiful professional maternity portrait of a pregnant woman — "
            "the SAME woman from the 3 reference photos the client uploaded. "
            "Soft natural light, real skin texture, authentic pregnancy glow. "
            "Shot on a high-end smartphone, photorealistic, 8K resolution."
        )
    else:
        scene_prompt = preset["prompt"]

    parts = []

    # 1. IDENTITY (prioridade máxima)
    if use_identity_text:
        parts.append(IDENTITY_ANCHOR)

    # 2. CENA (estilo)
    parts.append(scene_prompt)

    # 3. ENQUADRAMENTO
    parts.append(FRAMING_VARIANTS.get(framing, FRAMING_VARIANTS["full_body"]))

    # 4. DETALHES DO SUJEITO
    if subject_description:
        parts.append(f"Additional details about the subject: {subject_description}")

    # 5. NATURALNESS
    if use_naturalness_booster:
        parts.append(NATURALNESS_BOOSTER)

    # 6. QUALIDADE
    parts.append(QUALITY_CORE)

    final_prompt = " ".join(parts)
    logger.info(f"Prompt gerado com sucesso para o estilo: {tipo_ensaio} ({len(final_prompt)} chars)")
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
    # Exemplo: Gerando um ensaio do estilo Luxury Studio
    meu_prompt = generate_prompt(
        tipo_ensaio="luxury_studio",
        subject_description="Mulher de pele morena, cabelos cacheados escuros, olhos castanhos.",
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