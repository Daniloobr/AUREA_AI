"""
Prompt Engine — Maternity Photography (Realistic, Identity‑First)
Optimized for openai/gpt-image-2 via Replicate
================================================================
Prompt structure (OpenAI recommended order):
  Scene → Subject → Important details → Use case → Beauty styling →
  Feminine direction → Visual simplicity → Quality brief → Face priority → Identity anchor

Target: 600–800 chars. Hard limit: 800 chars enforced at runtime.

Aesthetic goal: Premium maternity photography with natural smartphone quality,
professional styling, elegant poses, clean composition, and strong identity preservation.
"""

import logging
from typing import Literal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
# BEAUTY STYLING (premium, natural makeup and hair)
# ══════════════════════════════════════════════════════════════
BEAUTY_STYLING = (
    "Professional luxury maternity makeup and hairstyling. "
    "Soft glam makeup with elegant skin finish, softly defined eyes, natural lashes, "
    "subtle blush, refined neutral lip color, professionally styled hair with soft volume and movement. "
    "Looks professionally produced for a premium maternity photoshoot."
)

# ══════════════════════════════════════════════════════════════
# FEMININE DIRECTION (elegant posture and body language)
# ══════════════════════════════════════════════════════════════
FEMININE_DIRECTION = (
    "Elegant feminine posture and confident body language."
)

# ══════════════════════════════════════════════════════════════
# VISUAL SIMPLICITY (avoids excessive fabric, props, clutter)
# ══════════════════════════════════════════════════════════════
VISUAL_SIMPLICITY = (
    "Clean composition with realistic visual balance. "
    "No excessive props, no exaggerated fabric volume, no cluttered background."
)

# ══════════════════════════════════════════════════════════════
# QUALITY BRIEF – iPhone 17 Pro Max aesthetic
# ══════════════════════════════════════════════════════════════
QUALITY_BRIEF = (
    "Shot on iPhone 17 Pro Max – natural smartphone photography. "
    "Realistic skin texture, authentic colors, subtle depth of field. "
    "No heavy retouching, no CGI, no artificial smoothing."
)

# ══════════════════════════════════════════════════════════════
# FACE PRIORITY (ensures facial visibility and likeness)
# ══════════════════════════════════════════════════════════════
FACE_PRIORITY = (
    "Natural facial rendering with clear facial visibility and authentic resemblance."
)

# ══════════════════════════════════════════════════════════════
# IDENTITY ANCHOR (shorter, stronger, placed at the very end)
# ══════════════════════════════════════════════════════════════
IDENTITY_ANCHOR = (
    "CRITICAL: The generated image MUST show the exact same person as the 3 reference photos – "
    "same face, bone structure, eyes, nose, lips, skin tone, hair. "
    "Do NOT change identity, do NOT beautify, do NOT idealize."
)

# ══════════════════════════════════════════════════════════════
# STYLE PRESETS – scene + light + wardrobe + spatial micro-details
# All styles now have rich yet concise descriptions, avoiding over‑technical lighting.
# Removed "stunning", "breathtaking" etc. Simplified lighting phrases.
# ══════════════════════════════════════════════════════════════
STYLE_PRESETS = {
    "classic": {
        "name": "Clássico",
        "prompt": (
            "Classic maternity studio portrait. Soft beige studio backdrop with subtle floor shadows, "
            "soft natural front lighting. She wears a flowing white cotton dress with natural folds."
        ),
    },
    "luxury_studio": {
        "name": "Estúdio Luxo",
        "prompt": (
            "Luxury studio maternity portrait. Dove-gray seamless backdrop with gentle gradient falloff, "
            "soft natural front lighting with gentle depth. "
            "She wears a flowing ivory silk gown with soft natural folds and delicate luster."
        ),
    },
    "ivory_satin": {
        "name": "Cetim Imperial",
        "prompt": (
            "Elegant studio portrait. Ivory satin backless gown with a long flowing train, "
            "polished studio floor reflecting soft light. Soft natural front lighting, refined shadows. "
            "The satin fabric catches light with a natural sheen."
        ),
    },
    "black_white_editorial": {
        "name": "Preto & Branco Editorial",
        "prompt": (
            "Black and white maternity portrait. Soft natural front lighting, clean minimalist background "
            "with subtle tonal graduation. Rich tonal range, timeless monochrome aesthetic. "
            "She wears a simple elegant dark outfit that drapes beautifully."
        ),
    },
    "dramatic_black_gown": {
        "name": "Vestido Preto Dramático",
        "prompt": (
            "Fine art maternity portrait. She wears an elegant black gown with soft matte texture, "
            "soft natural side lighting, minimalist composition, elegant shadows that sculpt the silhouette. "
            "Polished studio floor with subtle reflections."
        ),
    },
    "golden_hour_nature": {
        "name": "Pôr do Sol na Natureza",
        "prompt": (
            "Outdoor maternity portrait in a wildflower meadow during golden hour. "
            "Warm natural side light, soft bokeh from wildflowers, gentle wind movement through the grass. "
            "She wears a flowing dusty rose dress with delicate fabric movement."
        ),
    },
    "boho_chic": {
        "name": "Boho Chic",
        "prompt": (
            "Bohemian maternity portrait. Large window natural light, warm earth tones, dried floral accents "
            "(pampas grass and preserved roses). She wears a flowing earth-toned outfit with soft texture, "
            "cozy textured fabrics in the background (woven rug, raw wood)."
        ),
    },
    "taupe_wings": {
        "name": "Asas de Chiffon Nude",
        "prompt": (
            "Ethereal studio portrait. She wears a deep taupe-nude chiffon gown with wide fabric panels "
            "extended mid-air in a wing-like shape. Soft natural overhead light creating gentle shadow roll‑off, "
            "warm gray studio background with subtle gradient."
        ),
    },
    "red_lotus": {
        "name": "Lótus Vermelho",
        "prompt": (
            "Cozy holiday maternity portrait. Lotus position on a plush white sofa, "
            "red silk pajamas with soft sheen. Warm natural ring flash combined with ambient Christmas tree lights, "
            "dark lounge setting with soft glowing edges and subtle depth."
        ),
    },
}

# ══════════════════════════════════════════════════════════════
# EXPRESSION LIBRARY
# ══════════════════════════════════════════════════════════════
EXPRESSION_LIBRARY = {
    "warm":      "gentle natural smile, warmth in the eyes, relaxed facial muscles",
    "neutral":   "calm neutral expression, serene and composed",
    "editorial": "soft introspective look, natural emotional depth",
}

# ══════════════════════════════════════════════════════════════
# POSE LIBRARY (elegant and feminine)
# ══════════════════════════════════════════════════════════════
POSE_LIBRARY = {
    "front_cradle": "facing camera, both hands gently resting on the belly, elegant posture",
    "walking":      "slow natural walk, captured mid-step, graceful movement",
    "window_light": "standing near a window, one hand softly touching the belly, relaxed elegance",
    "looking_down": "looking softly down toward the belly, tender and maternal",
}

# ══════════════════════════════════════════════════════════════
# FRAMING VARIANTS
# ══════════════════════════════════════════════════════════════
FRAMING_VARIANTS = {
    "full_body":           "full body composition, natural proportions",
    "three_quarters":      "three-quarter framing, belly naturally emphasized",
    "medium":              "medium portrait framing, emotional connection",
    "close_up_emotional":  "close emotional portrait, shallow depth of field",
    "detail_hands_belly":  "intimate detail of hands resting gently on the belly",
}

# ══════════════════════════════════════════════════════════════
# NEGATIVE PROMPT (reference only)
# ══════════════════════════════════════════════════════════════
NEGATIVE_PROMPT = (
    "plastic skin, wax face, over-smoothed, stiff mannequin pose, "
    "identity drift, swapped face, CGI, 3d render, cartoon, anime, "
    "bad anatomy, extra fingers, watermark, text, uncanny valley."
)

_HARD_LIMIT = 800


# ══════════════════════════════════════════════════════════════
# MAIN PROMPT GENERATOR
# ══════════════════════════════════════════════════════════════
def generate_prompt(
    tipo_ensaio: str,
    subject_description: str = "",
    framing: Literal[
        "full_body",
        "three_quarters",
        "medium",
        "close_up_emotional",
        "detail_hands_belly",
    ] = "full_body",
    use_naturalness_booster: bool = True,   # kept for backward compat, unused
    use_identity_text: bool = True,
    pose_key: str = "front_cradle",
    expression_key: str = "warm",
    lens_type: str = "portrait",            # kept for backward compat, unused
) -> str:
    """
    Build a concise, conflict-free prompt (target 600-800 chars).

    Structure: Scene → Subject → Important details → Use case → Beauty styling →
               Feminine direction → Visual simplicity → Quality brief → Face priority → Identity anchor
    """
    # ── 1. Scene ──────────────────────────────────────────
    preset = STYLE_PRESETS.get(tipo_ensaio)
    if not preset:
        logger.warning("Unknown style '%s'. Using fallback.", tipo_ensaio)
        scene = "Professional maternity portrait in a studio setting with soft lighting."
    else:
        scene = preset["prompt"]

    # ── 2. Subject (pose + expression) ────────────────────
    pose = POSE_LIBRARY.get(pose_key, POSE_LIBRARY["front_cradle"])
    expression = EXPRESSION_LIBRARY.get(expression_key, EXPRESSION_LIBRARY["warm"])
    subject = f"Pregnant woman, {pose}, {expression}."

    # ── 3. Important details (framing + subject description) ──
    frame = FRAMING_VARIANTS.get(framing, FRAMING_VARIANTS["full_body"])
    details_parts = [frame.capitalize()]
    if subject_description:
        details_parts.append(subject_description.strip().rstrip("."))
    details = ". ".join(details_parts) + "."

    # ── 4. Use case ───────────────────────────────────────
    use_case = "Premium maternity editorial photography."

    # ── 5. Beauty styling ─────────────────────────────────
    beauty = BEAUTY_STYLING

    # ── 6. Feminine direction ─────────────────────────────
    feminine = FEMININE_DIRECTION

    # ── 7. Visual simplicity ──────────────────────────────
    simplicity = VISUAL_SIMPLICITY

    # ── 8. Quality brief ──────────────────────────────────
    quality = QUALITY_BRIEF

    # ── 9. Face priority ──────────────────────────────────
    face_priority = FACE_PRIORITY

    # ── 10. Identity anchor (only at the end) ─────────────
    identity = IDENTITY_ANCHOR if use_identity_text else ""

    # ── Assemble & normalise whitespace ───────────────────
    prompt = " ".join(
        f"{scene} {subject} {details} {use_case} {beauty} {feminine} {simplicity} {quality} {face_priority} {identity}".split()
    )

    # ── Hard-limit guard (graceful truncation) ────────────
    if len(prompt) > _HARD_LIMIT and subject_description:
        # Try to trim subject_description first
        prompt_without_desc = " ".join(
            f"{scene} {subject} {frame.capitalize()}. {use_case} {beauty} {feminine} {simplicity} {quality} {face_priority} {identity}".split()
        )
        overhead = len(prompt_without_desc)
        budget = _HARD_LIMIT - overhead - 5
        if budget > 10:
            trimmed_desc = subject_description.strip().rstrip(".")[:budget]
            details = f"{frame.capitalize()}. {trimmed_desc}."
            prompt = " ".join(
                f"{scene} {subject} {details} {use_case} {beauty} {feminine} {simplicity} {quality} {face_priority} {identity}".split()
            )
            logger.warning("subject_description trimmed to fit 800-char limit (%d chars).", len(prompt))
        else:
            # Drop subject_description entirely
            details = f"{frame.capitalize()}."
            prompt = " ".join(
                f"{scene} {subject} {details} {use_case} {beauty} {feminine} {simplicity} {quality} {face_priority} {identity}".split()
            )
            logger.warning("subject_description dropped entirely to stay within 800-char limit.")

    # Final safety check
    if len(prompt) > _HARD_LIMIT:
        logger.error("Prompt still exceeds 800 chars after trimming (%d).", len(prompt))
        # Fallback: remove subject_description and identity anchor (last resort)
        prompt = " ".join(
            f"{scene} {subject} {frame.capitalize()}. {use_case} {beauty} {feminine} {simplicity} {quality} {face_priority}".split()
        )
        if len(prompt) > _HARD_LIMIT:
            prompt = prompt[:_HARD_LIMIT]

    logger.info("Prompt generated: %s (%d chars)", tipo_ensaio, len(prompt))
    return prompt


# ══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════
def generate_negative_prompt() -> str:
    return NEGATIVE_PROMPT


def get_available_styles() -> list:
    return [{"id": k, "name": v["name"]} for k, v in STYLE_PRESETS.items()]


def get_framing_options() -> list:
    return [{"id": k, "name": k.replace("_", " ").title()} for k in FRAMING_VARIANTS]


# ══════════════════════════════════════════════════════════════
# SELF-TEST
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    RESET = "\033[0m"
    GREEN = "\033[92m"
    RED   = "\033[91m"
    CYAN  = "\033[96m"

    def ok(cond): return f"{GREEN}✅{RESET}" if cond else f"{RED}❌{RESET}"

    print(f"\n{CYAN}{'=' * 68}{RESET}")
    print(f"{CYAN}  AUREA AI — Prompt Engine v5 (Premium Styling + Face Priority){RESET}")
    print(f"{CYAN}{'=' * 68}{RESET}\n")

    # 1. Char count audit
    print("── Char Count Audit (no subject_description) ──────────────────")
    for sid in STYLE_PRESETS:
        p = generate_prompt(sid)
        flag = ok(len(p) <= _HARD_LIMIT)
        print(f"  {flag}  {sid:<30}  {len(p)} chars")

    # 2. Example: luxury_studio
    print(f"\n── Example: luxury_studio ──────────────────────────────────────")
    ex = generate_prompt("luxury_studio", subject_description="Woman with dark curly hair, warm brown skin")
    print(f"  Length : {len(ex)} chars  {ok(len(ex) <= _HARD_LIMIT)}")
    print(f"\n  {ex}\n")

    # 3. Example: golden_hour_nature
    print("── Example: golden_hour_nature (all params) ────────────────────")
    ex2 = generate_prompt(
        "golden_hour_nature",
        subject_description="Woman with dark curly hair, warm brown skin",
        framing="three_quarters",
        pose_key="looking_down",
        expression_key="editorial",
    )
    print(f"  Length : {len(ex2)} chars  {ok(len(ex2) <= _HARD_LIMIT)}")
    print(f"\n  {ex2}\n")

    # 4. Integrity checks
    print("── Integrity Checks ────────────────────────────────────────────")
    FORBIDDEN = [
        "stunning", "gorgeous", "masterpiece", "8K", "ultra high resolution",
        "chiaroscuro", "rim glow", "octabox", "softbox",
        "soft even tone", "subtle natural glow", "real pores visible",
        "matte T-zone", "highlighter", "backlight at", "degrees",
    ]
    found = [w for w in FORBIDDEN if w.lower() in ex.lower()]
    print(f"  {ok(not found)}  No forbidden terms" + (f": {found}" if found else ""))

    anchor_n = ex.count("CRITICAL: The generated image MUST show the exact same person")
    print(f"  {ok(anchor_n == 1)}  IDENTITY_ANCHOR appears exactly once ({anchor_n}×)")

    # Check for presence of new blocks
    print(f"  {ok('Professional luxury maternity makeup' in ex)}  BEAUTY_STYLING present")
    print(f"  {ok('Clean composition with realistic visual balance' in ex)}  VISUAL_SIMPLICITY present")
    print(f"  {ok('Natural facial rendering' in ex)}  FACE_PRIORITY present")

    print(f"\n{CYAN}{'=' * 68}{RESET}\n")