"""
Prompt Engineering Service — Ultra-Realistic Maternity Photography
====================================================================
Generates cinematic, hyper-detailed prompts optimized for InstantID/IP-Adapter.

Key principles:
- Identity preservation (face + body morphology) are FIRST (highest token weight)
- Camera/lens specifications force photorealistic rendering
- Negative prompts aggressively block cartoon/anime/deformed outputs
- Style presets are modular and extensible
"""
import logging

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
# IDENTITY PRESERVATION CORE (Face + Body - now includes body morphology)
# ══════════════════════════════════════════════════════════════
IDENTITY_PRESERVATION = (
    # Face preservation (original)
    "Photograph of the EXACT SAME person from the reference image. "
    "Identical facial identity, identical facial structure, identical bone structure, "
    "identical nose shape, identical eye shape, identical lip shape, identical jawline, "
    "identical skin tone, identical skin texture, identical hair color, identical hair texture. "
    # <-- NOVO: preservação do corpo inteiro (sem padrão genérico)
    "EXACT SAME body morphology from the reference image. "
    "Preserve their natural body shape: identical shoulder width, identical arm thickness and shape, "
    "identical waist-to-hip ratio, identical belly size and shape (pregnancy belly if applicable), "
    "identical leg thickness, identical overall body proportions. "
    "Do NOT impose a generic 'model body' or 'idealized body type'. "
    "Do NOT change the person's body shape. Do NOT make them thinner, thicker, or different proportioned. "
    "Every unique body feature must be preserved with absolute precision. "
)

# ══════════════════════════════════════════════════════════════
# QUALITY BOOSTERS (Camera & technical specifications) - REALISMO
# ══════════════════════════════════════════════════════════════
QUALITY_CORE = (
    "Ultra photorealistic, hyperrealistic, 8k UHD resolution, "
    "shot on Fujifilm GFX 100S medium format with GF 80mm f/1.7 or GF 110mm f/2 lens, "
    "natural skin imperfections visible, visible pores, fine downy hair (lanugo) on skin, "
    "soft messy hair, organic colors, no over-smoothing, "
    "natural subsurface scattering on skin, subtle stretch marks on belly (if applicable), "
    "global illumination, bounce light, unshadowed details for realistic depth, "
    "natural film grain, RAW photo, extremely detailed skin texture, "
    "professional color grading by a Hollywood colorist, "
    "award-winning photography, masterpiece. "
)

# ══════════════════════════════════════════════════════════════
# NEGATIVE PROMPT (Aggressive anti-artifact) - REFORÇADO
# ══════════════════════════════════════════════════════════════
NEGATIVE_PROMPT = (
    "different person, different face, wrong identity, changed face, "
    "deformed face, deformed eyes, asymmetrical face, asymmetrical eyes, "
    "cross-eyed, lazy eye, squinting, "
    "bad anatomy, bad proportions, extra limbs, extra fingers, mutated hands, "
    "fused fingers, missing fingers, too many fingers, "
    "thin arms, skinny arms, unnaturally thin arms, twig arms, deformed arms, mismatched arms, "
    "anorexic, unrealistic thinness, emaciated, starving model, bony shoulders, "
    # <-- NOVO: bloqueio contra corpo padronizado
    "standardized body, cookie-cutter shape, generic model body, unrealistic waist, "
    "belly too round, belly too flat, fake pregnancy belly, body not matching reference, "
    "fake background, green screen, digital composite background, painted backdrop, "
    "plastic skin, airbrushed skin, wax figure, doll face, mannequin, "
    "perfect skin, no pores, no imperfections, over-retouched, "
    "ugly, distorted, disfigured, mutation, "
    "cartoon, anime, 3d render, CGI, illustration, painting, drawing, sketch, "
    "watermark, text, logo, signature, username, "
    "low quality, blurry, out of focus, noise, grainy, pixelated, "
    "jpeg artifacts, compression artifacts, "
    "overexposed, underexposed, blown highlights, crushed blacks, "
    "duplicate face, multiple people, extra person, "
    "nsfw, nudity, naked, topless, motion blur, camera shake"
)

# ══════════════════════════════════════════════════════════════
# STYLE PRESETS — Cada um com figurino realista, poses humanas E respeito à morfologia original
# ══════════════════════════════════════════════════════════════
STYLE_PRESETS = {
    # ─── GESTANTE (Maternity) ───────────────────────────
    "gestante_outdoor": {
        "name": "Gestante ao Ar Livre — Golden Hour",
        "prompt": (
            "Authentic maternity photoshoot outdoors during golden hour. "
            "The pregnant woman is standing in a vast field of wildflowers with rolling hills behind her. "
            "She is wearing a comfortable linen or cotton maxi dress, slightly wrinkled, natural fabric. "
            "Warm golden sunlight creating gentle rim lighting and soft sun flares. "
            "Hands gently cradling her belly. Arms naturally proportioned, healthy thickness. "
            "Healthy and glowing maternal form with real body proportions. "
            "Authentic maternal connection, natural weight distribution, slightly messy hair. "
            "Body morphology exactly matching the reference person. No idealized body type. "
            "Preserve their natural shoulder width, arm thickness, belly shape, hip-to-waist ratio. "
            "Serene, confident, glowing maternal expression. "
            "Cinematic composition, rule of thirds, natural bokeh. "
            "Shot on Fujifilm GFX 100S, GF 110mm f/2, natural light only. "
        ),
    },
    "gestante_estudio": {
        "name": "Gestante Estúdio Luxo — Rembrandt",
        "prompt": (
            "High-end luxury maternity portrait in a premium photography studio. "
            "The pregnant woman is posing elegantly with dramatic Rembrandt lighting. "
            "Seamless warm gray paper backdrop (#C4C4C4), no wrinkles, extending to the floor. "
            "Professional studio lighting: main light is a 48-inch octabox with grid at 45 degrees camera left, "
            "fill card at 30% from camera right, bounce light from white ceiling for natural fill. "
            "She is wearing a form-fitting knitted midi dress in dark charcoal or burgundy, soft stretchy fabric. "
            "One hand gently on her belly, the other resting naturally at her side. Relaxed shoulders, natural posture. "
            "Arms naturally proportioned, healthy thickness, real body proportions. "
            "Healthy and glowing maternal form. Authentic maternal connection, not stiff. "
            "Body morphology exactly matching the reference person. No standardized body shape. "
            "Hair slightly messy, not perfectly blown out. Natural skin texture, visible pores, fine lanugo. "
            "Powerful, regal, confident maternal expression. "
            "Shot on Fujifilm GFX 100S, GF 80mm f/1.7, studio strobe with octabox. "
        ),
    },
    "gestante_editorial": {
        "name": "Gestante Editorial Vogue — Alta Moda",
        "prompt": (
            "High fashion maternity editorial photography for Vogue magazine. "
            "The pregnant woman is posing with striking confidence like a model on a fashion shoot. "
            "Seamless pure white or deep charcoal paper backdrop, immaculately smooth. "
            "Wearing a structured cotton or linen architectural dress, bold geometric shapes, natural fibers. "
            "Bold, contemporary lighting with sharp shadows and pristine highlights. "
            "Striking composition with negative space. "
            "Arms naturally proportioned, healthy thickness. Real body proportions, healthy and glowing maternal form. "
            "Authentic maternal connection, natural weight distribution. "
            "Body morphology exactly matching the reference person. No idealized body type. "
            "Flawed skin visible: pores, fine lines, natural texture. Slightly messy hair, organic colors. "
            "Professional lighting: key light beauty dish, two rim lights, background light, global illumination. "
            "Shot on Fujifilm GFX 100S, GF 110mm f/2, color graded naturally. "
        ),
    },
    "gestante_floral": {
        "name": "Gestante Floral Goddess",
        "prompt": (
            "Enchanting maternity photoshoot surrounded by abundant fresh flowers. "
            "The pregnant woman is nestled among cascading roses, peonies, ranunculus, and hydrangeas. "
            "Wearing a delicate cotton or linen lace dress, slightly wrinkled, natural fabric. "
            "Soft, diffused natural light creating a dreamy, romantic atmosphere. "
            "Serene, blissful maternal expression with closed eyes or gentle smile. "
            "Arms naturally proportioned, healthy thickness. Healthy and glowing maternal form. "
            "Authentic maternal connection, natural weight distribution, slightly messy hair. "
            "Body morphology exactly matching the reference person. No generic pregnancy belly shape. "
            "Flowers artfully arranged around her, some in her hair. "
            "Shot on Fujifilm GFX 100S, GF 80mm f/1.7, natural light, pastel organic colors. "
        ),
    },
    "gestante_minimal": {
        "name": "Gestante Minimalista — Clean White",
        "prompt": (
            "Minimalist contemporary maternity portrait with clean white aesthetic. "
            "The pregnant woman is in a bright, airy all-white studio environment. "
            "Seamless white vinyl flooring and white paper backdrop, creating an infinite white look. "
            "Wearing a simple, elegant white organic cotton bodysuit or draped linen fabric. "
            "Soft, even lighting from large diffused sources — two 4x6 foot softboxes, bounce light from walls. "
            "Focus entirely on the beauty of the pregnant form and the woman's face. "
            "Arms naturally proportioned, healthy thickness. Real body proportions. "
            "Healthy and glowing maternal form. Authentic maternal connection, calm meditative expression. "
            "Body morphology exactly matching the reference person. No unrealistic waist. "
            "Natural skin texture, visible pores, fine downy hair, slightly messy hair. "
            "Shot on Fujifilm GFX 100S, GF 110mm f/2, high-key lighting, no shadows. "
        ),
    },
    "gestante_dark": {
        "name": "Gestante Dark Moody — Cinematográfica",
        "prompt": (
            "Dramatic dark moody maternity portrait with cinematic atmosphere. "
            "The pregnant woman emerges from deep shadows with only her face and belly illuminated. "
            "Seamless black velvet backdrop or matte black paper, completely light-absorbent. "
            "Rich, dark tones — deep navy, burgundy, charcoal. "
            "Wearing a luxurious cotton velvet or heavy knit dress in deep jewel tones. "
            "Intense, powerful, mysterious maternal expression. "
            "Arms naturally proportioned, healthy thickness. Real body proportions, healthy and glowing maternal form. "
            "Body morphology exactly matching the reference person. No cookie-cutter shape. "
            "Single dramatic light source creating strong contrast — gridded beauty dish or snoot. "
            "No fill light, allowing shadows to fall into pure black. "
            "Natural skin texture visible, pores, fine lanugo, slightly messy hair. "
            "Shot on Fujifilm GFX 100S, GF 110mm f/2, film noir aesthetic. "
        ),
    },

    # ─── BEBÊ (Newborn) — mantidos originais (corpo pequeno, menos crítico, mas adiciono referência)
    "bebe_neutro": {
        "name": "Bebê Neutro Clássico — Aconchegante",
        "prompt": (
            "Award-winning newborn baby photography in warm neutral tones. "
            "The infant is peacefully sleeping, swaddled in luxurious organic muslin or cashmere wrap "
            "in soft oat, cream, or warm beige tones. "
            "Placed on a fluffy textured blanket or in a handcrafted wooden bowl prop. "
            "Soft, diffused window light gently wrapping around the baby's delicate features. "
            "Tiny fingers and toes visible, serene sleeping expression. "
            "Body morphology exactly matching the reference baby. No standardized infant shape. "
            "Shot on Fujifilm GFX 100S, GF 110mm f/2 or macro lens, "
            "natural light studio, extremely detailed skin texture, "
            "warm and cozy atmosphere, heirloom quality portraiture. "
        ),
    },
    "bebe_fantasia": {
        "name": "Bebê Fantasia — Mundo Mágico",
        "prompt": (
            "Magical fantasy-themed newborn portrait in an enchanted miniature world. "
            "The baby is nestled comfortably in a whimsical fairy-tale scene — "
            "perhaps a tiny mossy nest, a flower petal bed, or a miniature enchanted garden. "
            "Soft bioluminescent glow, tiny fairy lights, ethereal mist. "
            "Rich jewel-tone colors — emerald, sapphire, amethyst — with warm golden accents. "
            "Baby sleeping peacefully with a serene angelic expression. "
            "Body morphology exactly matching the reference baby. Preserve their natural proportions. "
            "Shot on Fujifilm GFX 100S, GF 110mm f/2, "
            "carefully crafted practical miniature set with LED fairy lights, "
            "composite photography technique, fantasy film aesthetic. "
        ),
    },
    "bebe_estudio": {
        "name": "Bebê Estúdio Moderno — Clean Premium",
        "prompt": (
            "Modern premium newborn studio portrait with clean contemporary aesthetic. "
            "The baby is posed naturally on a soft, sculpted backdrop in gentle pastel tones. "
            "Wearing a tiny knitted outfit or delicate wrap in soft sage, dusty rose, or powder blue. "
            "Professional studio lighting — large softbox overhead creating even, flattering light. "
            "Crisp sharp focus on the baby's face, beautiful skin detail. "
            "Body morphology exactly matching the reference baby. No generic baby shape. "
            "Shot on Fujifilm GFX 100S, GF 110mm f/2, "
            "controlled studio environment, "
            "modern lifestyle magazine quality, "
            "clean composition with plenty of negative space. "
        ),
    },
}


def generate_prompt(tipo_ensaio: str, subject_description: str = "") -> str:
    """
    Generates a complete, production-grade prompt by combining:
    1. Identity preservation (face + body morphology) - highest priority
    2. Style-specific scene description
    3. Quality boosters
    4. Optional subject description
    """
    preset = STYLE_PRESETS.get(tipo_ensaio)

    if preset:
        scene_prompt = preset["prompt"]
    else:
        # Fallback generic prompt
        logger.warning(f"Unknown tipo_ensaio: {tipo_ensaio}, using fallback")
        scene_prompt = (
            "Authentic portrait photography in a natural setting. "
            "Elegant pose, soft lighting, real human imperfections visible. "
        )

    # Build final prompt: Identity (now with body) first, then scene, then quality
    final_prompt = f"{IDENTITY_PRESERVATION}{scene_prompt}"
    
    if subject_description:
        final_prompt += f"{subject_description} "
    
    final_prompt += QUALITY_CORE

    logger.info(f"Generated prompt for '{tipo_ensaio}': {len(final_prompt)} chars")
    return final_prompt


def generate_negative_prompt() -> str:
    """Returns the universal negative prompt for all generations."""
    return NEGATIVE_PROMPT


def get_available_styles() -> list:
    """Returns list of available style presets for the frontend."""
    return [
        {"id": key, "name": val["name"]}
        for key, val in STYLE_PRESETS.items()
    ]