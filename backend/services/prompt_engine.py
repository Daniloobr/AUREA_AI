"""
AUREA AI
Premium Realistic Maternity Photography Prompt Engine
Optimized for openai/gpt-image-2

Based on official GPT-Image-2 guidelines:
- Keep prompts concise (≤700 chars)
- Put identity preservation both early and late
- Use "photorealistic" to activate high-fidelity mode
- Avoid vague adjectives; describe concrete visual facts
"""

import logging
from typing import Optional, Literal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════
MAX_PROMPT_LENGTH = 700          # redutor para prompts mais enxutos

# ══════════════════════════════════════════════════════════════
# REFERENCE & IDENTITY (início - contexto forte)
# ══════════════════════════════════════════════════════════════
REFERENCE_PRIORITY = (
    "The client uploaded 3 real reference photos. "
    "These photos are the only source of truth for identity. "
    "Use the text prompt for artistic direction only."
)

IDENTITY_PRIORITY = (
    "Preserve the exact same woman: same face, eyes, nose, lips, skin tone, hair. "
    "Do NOT change identity, do NOT beautify, do NOT idealize. "
    "Identity is more important than any aesthetic choice."
)

# ══════════════════════════════════════════════════════════════
# FACE-BODY CONSISTENCY
# ══════════════════════════════════════════════════════════════
FACE_BODY_CONSISTENCY = (
    "The face and body must match exactly the same person shown in the reference photos. "
    "Do not generate a face from one person and a body from another. "
    "The entire figure (head, torso, belly, limbs) must belong to the same individual."
)

# ══════════════════════════════════════════════════════════════
# UNIFIED DIRECTION (câmera, luz, pose, realismo, elegância)
# ══════════════════════════════════════════════════════════════
UNIFIED_DIRECTION = (
    "Professional full-frame camera, soft natural front lighting, natural relaxed pose, elegant presence. "
    "Photorealistic – real skin texture, authentic body proportions, no CGI, no heavy retouching."
)

# ══════════════════════════════════════════════════════════════
# BEAUTY (maquiagem e cabelo, sem risco de pele artificial)
# ══════════════════════════════════════════════════════════════
SKIN_AND_BEAUTY = (
    "Natural polished makeup: softly defined eyes, subtle blush, neutral lip color. "
    "Healthy natural skin with realistic texture, no heavy foundation."
)

EDITORIAL_BEAUTY = (
    "Luxury editorial beauty styling: soft refined makeup, natural complexion, polished hair. "
    "Realistic texture preserved, no artificial smoothing."
)

# ══════════════════════════════════════════════════════════════
# LENS PRESETS (simples, diretos)
# ══════════════════════════════════════════════════════════════
LENS_PRESETS = {
    "portrait":    "50mm portrait lens, natural perspective.",
    "cinematic":   "85mm lens, soft background compression.",
    "documentary": "35mm documentary lens, environmental feel.",
}

# ══════════════════════════════════════════════════════════════
# EXPRESSIONS (curtas, autênticas)
# ══════════════════════════════════════════════════════════════
EXPRESSION_LIBRARY = {
    "warm":          "gentle natural smile, warmth in the eyes.",
    "neutral":       "calm relaxed expression.",
    "editorial":     "soft introspective look.",
    "laughing_soft": "soft candid laughter.",
    "looking_down":  "looking gently toward the belly.",
    "window_gaze":   "soft thoughtful gaze toward the window.",
}

# ══════════════════════════════════════════════════════════════
# POSES (naturais, elegantes)
# ══════════════════════════════════════════════════════════════
POSE_LIBRARY = {
    "front_cradle":      "facing camera, both hands gently resting on the belly.",
    "walking":           "captured naturally while walking slowly.",
    "window_light":      "standing near a window, relaxed posture.",
    "looking_down_pose": "looking softly toward the belly, gentle hand placement.",
    "soft_hair_touch":   "one hand softly touching the hair, the other on the belly.",
}

# ══════════════════════════════════════════════════════════════
# FRAMING
# ══════════════════════════════════════════════════════════════
FRAMING_VARIANTS = {
    "full_body":          "full body composition, realistic proportions.",
    "three_quarters":     "three-quarter framing, belly naturally emphasized.",
    "medium":             "medium portrait, emotional connection.",
    "close_up_emotional": "close emotional portrait, shallow depth of field.",
    "detail_hands_belly": "intimate detail of hands on the belly.",
}

# ══════════════════════════════════════════════════════════════
# STYLE PRESETS (concisos, sem superlativos)
# ══════════════════════════════════════════════════════════════
STYLE_PRESETS = {
    "classic": {
        "name": "Clássico",
        "category": "Clássicos Atemporais",
        "description": "Um retrato clássico em estúdio refletindo a serenidade da gestação, com iluminação suave, fundo neutro e a gestante em vestido fluido, capturando a beleza atemporal do momento.",
        "cover": "/thumbnails/classic.png",
        "prompt": (
            "Classic maternity studio portrait. Neutral backdrop, soft diffused light. "
            "She wears a flowing white or cream dress."
        ),
    },
    "luxury_studio": {
        "name": "Estúdio Luxo",
        "category": "Clássicos Atemporais",
        "description": "Um ensaio luxuoso em estúdio com fundo cinza-pomba degradê, iluminação de contorno que realça a silhueta, apresentando um vestido marfim elegante, transmitindo sofisticação de alta costura.",
        "cover": "/thumbnails/luxury_studio.png",
        "prompt": (
            "Luxury studio portrait. Warm neutral tones, soft front lighting. "
            "She wears a flowing ivory silk gown with natural folds."
        ),
    },
    "ivory_satin": {
        "name": "Cetim Imperial",
        "category": "Clássicos Atemporais",
        "description": "Um vestido imperial de cetim marfim, sem costas, cauda longa sobre piso polido, iluminado lateralmente para realçar a textura sedosa, criando um efeito cinematográfico elegante.",
        "cover": "/thumbnails/image3.png",
        "prompt": (
            "Elegant studio portrait. Ivory satin backless gown, soft natural folds. "
            "Polished floor, refined shadows."
        ),
    },
    "black_white_editorial": {
        "name": "Preto & Branco Editorial",
        "category": "Editoriais Vogue",
        "description": "Um editorial em preto e branco com alto contraste, sombras suaves que esculpem o corpo, evocando a estética de revistas de moda com granulação de filme.",
        "cover": "/thumbnails/black_white_editorial.png",
        "prompt": (
            "Black and white maternity portrait. Soft directional light, clean background. "
            "Rich tonal range, timeless monochrome."
        ),
    },
    "dramatic_black_gown": {
        "name": "Vestido Preto Dramático",
        "category": "Editoriais Vogue",
        "description": "Um vestido preto dramático sem costas, cauda longa, iluminado com luz lateral Chiaroscuro sobre piso escuro polido, criando uma composição marcante e elegante.",
        "cover": "/thumbnails/vestidoBlack.png",
        "prompt": (
            "Fine art black and white portrait. Elegant black gown, soft side light. "
            "Minimalist composition, elegant shadows."
        ),
    },
    "golden_hour_nature": {
        "name": "Pôr do Sol na Natureza",
        "category": "Orgânicos & Sonhadores",
        "description": "Um ensaio ao ar livre ao pôr do sol, em um campo de flores silvestres, luz dourada banhando a gestante de vestido rosa antigo, criando uma aura mágica.",
        "cover": "/thumbnails/golden_hour_nature.png",
        "prompt": (
            "Outdoor portrait in a wildflower meadow during golden hour. "
            "Warm natural side light, soft bokeh. Flowing dusty rose dress."
        ),
    },
    "boho_chic": {
        "name": "Boho Chic",
        "category": "Orgânicos & Sonhadores",
        "description": "Um estilo boho chic com iluminação natural filtrada por cortinas translúcidas, cenário rústico de capim dos pampas, tons terrosos e detalhes de flores secas, transmitindo aconchego.",
        "cover": "/thumbnails/boho_chic.png",
        "prompt": (
            "Bohemian portrait. Large window natural light, earth tones, dried florals. "
            "Flowing earth-toned outfit."
        ),
    },
    "taupe_wings": {
        "name": "Asas de Chiffon Nude",
        "category": "Orgânicos & Sonhadores",
        "description": "Um vestido de chiffon nude escuro, fluindo como asas, posicionado contra fundo cinza suave, iluminado por softbox para realçar a leveza do tecido.",
        "cover": "/thumbnails/image2.png",
        "prompt": (
            "Ethereal studio portrait. Deep taupe-nude chiffon gown, soft overhead light. "
            "Light fabric flowing naturally."
        ),
    },
    "red_lotus": {
        "name": "Lótus Vermelho",
        "category": "Temáticos Divertidos",
        "description": "Um ensaio natalino encantador, com a gestante em pose de lótus sobre um sofá branco, usando pijama de seda vermelho vibrante, acompanhada de um balde de pipoca e iluminada por luz suave de árvore de Natal, trazendo um clima caloroso e festivo.",
        "cover": "/thumbnails/red_lotus.png",
        "prompt": (
            "Cozy holiday portrait. Lotus position on white sofa, red silk pajamas. "
            "Warm ambient light, Christmas tree glow."
        ),
    },
}

# ══════════════════════════════════════════════════════════════
# NEGATIVE PROMPT (referência – não usado pelo gpt-image-2)
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
        "full_body", "three_quarters", "medium", "close_up_emotional", "detail_hands_belly"
    ] = "full_body",
    pose_key: str = "front_cradle",
    expression_key: str = "warm",
    lens_type: str = "portrait",
    use_identity_text: bool = True,
) -> str:
    editorial_styles = ["black_white_editorial", "dramatic_black_gown", "ivory_satin"]
    preset = STYLE_PRESETS.get(tipo_ensaio)
    if not preset:
        logger.warning(f"Unknown style: {tipo_ensaio}")
        style_prompt = "Professional maternity portrait in a studio setting."
    else:
        style_prompt = preset["prompt"]

    framing_prompt = FRAMING_VARIANTS.get(framing, FRAMING_VARIANTS["full_body"])
    pose_prompt = POSE_LIBRARY.get(pose_key, POSE_LIBRARY["front_cradle"])
    expr_prompt = EXPRESSION_LIBRARY.get(expression_key, EXPRESSION_LIBRARY["warm"])
    lens_prompt = LENS_PRESETS.get(lens_type, LENS_PRESETS["portrait"])
    beauty_prompt = EDITORIAL_BEAUTY if tipo_ensaio in editorial_styles else SKIN_AND_BEAUTY

    parts = []
    if use_identity_text:
        parts.append(REFERENCE_PRIORITY)
        parts.append(IDENTITY_PRIORITY)
        parts.append(FACE_BODY_CONSISTENCY)   # <-- ADICIONADO AQUI (corretamente)

    parts.append(style_prompt)
    parts.append(framing_prompt)
    parts.append(pose_prompt)
    parts.append(expr_prompt)

    if subject_description:
        parts.append(f"Subject details: {subject_description}")

    parts.append(lens_prompt)
    parts.append(beauty_prompt)
    parts.append(UNIFIED_DIRECTION)

    # ══════════════════════════════════════════════════════════════
    # REFORÇO DE IDENTIDADE NO FINAL (âncora para maior peso)
    # ══════════════════════════════════════════════════════════════
    if use_identity_text:
        parts.append("Preserve exact identity from reference photos – same face, same person.")

    final_prompt = " ".join(parts)
    final_prompt = " ".join(final_prompt.split())   # normaliza espaços

    if len(final_prompt) > MAX_PROMPT_LENGTH:
        logger.warning(f"Prompt exceeded limit ({len(final_prompt)} chars). Truncating.")
        final_prompt = final_prompt[:MAX_PROMPT_LENGTH].rstrip()

    logger.info(f"Prompt generated: {tipo_ensaio} ({len(final_prompt)} chars)")
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
            "cover": v.get("cover", "")
        }
        for k, v in STYLE_PRESETS.items()
    ]


def get_framing_options() -> list:
    return [{"id": k, "name": k.replace("_", " ").title()} for k in FRAMING_VARIANTS]


if __name__ == "__main__":
    prompt = generate_prompt(
        tipo_ensaio="luxury_studio",
        subject_description="Woman with medium-dark skin tone, dark curly hair and brown eyes.",
        framing="three_quarters",
        pose_key="looking_down_pose",
        expression_key="warm",
        lens_type="cinematic",
    )
    print("\n" + "=" * 80)
    print("POSITIVE PROMPT")
    print("=" * 80 + "\n")
    print(prompt)
    print("\n" + "=" * 80)
    print("NEGATIVE PROMPT")
    print("=" * 80 + "\n")
    print(generate_negative_prompt())
    print("\n" + "=" * 80)
    print("AVAILABLE STYLES")
    print("=" * 80 + "\n")
    for style in get_available_styles():
        print(f"- {style['name']} ({style['id']})")
    print("\n" + "=" * 80)