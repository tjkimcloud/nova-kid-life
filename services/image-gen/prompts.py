"""
Prompt library for image generation.
Two prompt systems:
  - WEBSITE: warm editorial photography (realistic, credible)
  - SOCIAL:  flat editorial illustration (brand-consistent, scroll-stopping)

Warm color grade is applied in post-processing regardless of prompt style.
"""
from __future__ import annotations

# ── Shared style constants ────────────────────────────────────────────────────

_PHOTO_BASE = (
    "Professional editorial photography, warm golden hour lighting, "
    "amber and sage color tones, sharp focus, no text or watermarks, "
    "Northern Virginia suburban setting"
)

_ILLUSTRATION_BASE = (
    "Flat editorial illustration, warm amber and sage green color palette, "
    "rounded friendly shapes, clean vector art style, no text or logos, "
    "families and children, joyful community atmosphere"
)

_NEGATIVE = (
    "No text, no watermarks, no logos, no scary content, no violence, "
    "no dark themes, no cold blue tones"
)


# ── Website hero prompts (16:9, photorealistic) ───────────────────────────────

WEBSITE_PROMPTS: dict[str, str] = {
    "library": (
        f"{_PHOTO_BASE}. "
        "Cozy modern public library interior, children sitting on colorful cushions "
        "at storytime with a librarian reading aloud, warm amber lighting, "
        "bookshelves in background, parents watching, welcoming atmosphere. "
        f"{_NEGATIVE}"
    ),
    "outdoor": (
        f"{_PHOTO_BASE}. "
        "Families with young children enjoying a sunny outdoor festival in a "
        "Northern Virginia park, green trees, autumn or spring light, "
        "children laughing and playing, wide open community space. "
        f"{_NEGATIVE}"
    ),
    "arts-crafts": (
        f"{_PHOTO_BASE}. "
        "Children doing arts and crafts at colorful tables, paints and brushes, "
        "smiling kids and parents, bright indoor community center, "
        "warm amber light through windows. "
        f"{_NEGATIVE}"
    ),
    "sports": (
        f"{_PHOTO_BASE}. "
        "Children playing youth sports on a green field in Northern Virginia, "
        "sunny afternoon, families watching from sidelines, "
        "warm golden light, suburban park setting. "
        f"{_NEGATIVE}"
    ),
    "educational": (
        f"{_PHOTO_BASE}. "
        "Children engaged in hands-on STEM learning at a modern community center, "
        "science experiments, building blocks, curious expressions, "
        "warm lighting, encouraging educators nearby. "
        f"{_NEGATIVE}"
    ),
    "music": (
        f"{_PHOTO_BASE}. "
        "Children and families enjoying a live music performance outdoors, "
        "musicians on a small stage, families on blankets and chairs, "
        "warm evening light, Northern Virginia park amphitheater setting. "
        f"{_NEGATIVE}"
    ),
    "nature": (
        f"{_PHOTO_BASE}. "
        "Children exploring nature at a Northern Virginia nature center, "
        "examining insects or plants with magnifying glasses, trees and greenery, "
        "warm dappled sunlight, excited expressions. "
        f"{_NEGATIVE}"
    ),
    "holiday": (
        f"{_PHOTO_BASE}. "
        "Families celebrating a seasonal holiday event at a community park, "
        "festive decorations in warm amber and red tones, children in costumes "
        "or seasonal outfits, joyful outdoor gathering, golden light. "
        f"{_NEGATIVE}"
    ),
    "swimming": (
        f"{_PHOTO_BASE}. "
        "Children swimming and splashing at a bright outdoor community pool "
        "in Northern Virginia, sunny summer day, families watching from deck, "
        "warm golden tones, safe suburban setting. "
        f"{_NEGATIVE}"
    ),
    "theater": (
        f"{_PHOTO_BASE}. "
        "Families watching a children's theatrical performance at a community theater, "
        "warm stage lighting, excited young audience, colorful set design, "
        "Northern Virginia suburban venue. "
        f"{_NEGATIVE}"
    ),
    "food": (
        f"{_PHOTO_BASE}. "
        "Family enjoying a meal together at a bright, welcoming restaurant, "
        "warm amber interior lighting, smiling children and parents, "
        "appetizing food on table, clean modern casual dining. "
        f"{_NEGATIVE}"
    ),
    "deal_restaurant": (
        "Editorial food photography, warm amber lighting, appetizing close-up "
        "of a fresh meal at a casual family restaurant, "
        "clean modern presentation, warm tones, no text, no logos. "
        f"{_NEGATIVE}"
    ),
    "deal_birthday": (
        f"{_PHOTO_BASE}. "
        "Child blowing out birthday candles on a colorful cake surrounded by "
        "smiling family, warm golden light, celebratory confetti in amber "
        "and gold tones, joyful kitchen or restaurant setting. "
        f"{_NEGATIVE}"
    ),
    "deal_amusement": (
        f"{_PHOTO_BASE}. "
        "Children and parents having fun at an indoor family entertainment center, "
        "trampolines or climbing walls, warm colorful lighting, "
        "excited expressions, safe modern facility. "
        f"{_NEGATIVE}"
    ),
    "default": (
        f"{_PHOTO_BASE}. "
        "Happy family with young children enjoying an outdoor community event "
        "in Northern Virginia, warm amber sunlight, green trees, "
        "smiling faces, welcoming suburban setting. "
        f"{_NEGATIVE}"
    ),
}


# ── Social illustration prompts (1:1, flat editorial illustration) ─────────────

SOCIAL_PROMPTS: dict[str, str] = {
    "library": (
        f"{_ILLUSTRATION_BASE}. "
        "Illustrated scene of children at storytime in a cozy library, "
        "open books floating around, warm amber background with sage green accents, "
        "rounded cheerful characters, spot illustration style. "
        f"{_NEGATIVE}"
    ),
    "outdoor": (
        f"{_ILLUSTRATION_BASE}. "
        "Illustrated family at an outdoor festival, trees with autumn amber leaves, "
        "children running, parents relaxing, Northern Virginia park setting, "
        "warm color palette with sage green nature elements. "
        f"{_NEGATIVE}"
    ),
    "arts-crafts": (
        f"{_ILLUSTRATION_BASE}. "
        "Illustrated children painting and crafting at colorful tables, "
        "paint splashes in amber, sage, and warm tones, "
        "joyful rounded characters, creative activity scene. "
        f"{_NEGATIVE}"
    ),
    "sports": (
        f"{_ILLUSTRATION_BASE}. "
        "Illustrated kids playing soccer on a green field, "
        "amber sun in the sky, sage green grass, parents cheering, "
        "friendly rounded character style, community sports vibe. "
        f"{_NEGATIVE}"
    ),
    "educational": (
        f"{_ILLUSTRATION_BASE}. "
        "Illustrated children doing science experiments, beakers and test tubes, "
        "lightbulb moments, amber and sage accent colors, "
        "curious and excited rounded characters. "
        f"{_NEGATIVE}"
    ),
    "deal_restaurant": (
        f"{_ILLUSTRATION_BASE}. "
        "Bold illustrated food deal graphic — stylized burger or meal icon "
        "with celebratory stars and confetti in amber and sage green, "
        "punchy energetic composition, no text. "
        f"{_NEGATIVE}"
    ),
    "deal_birthday": (
        f"{_ILLUSTRATION_BASE}. "
        "Illustrated birthday celebration with a cake, candles, confetti, "
        "and a happy child character, warm amber and gold palette, "
        "festive spot illustration style, circular composition. "
        f"{_NEGATIVE}"
    ),
    "deal_amusement": (
        f"{_ILLUSTRATION_BASE}. "
        "Illustrated family at a trampoline park or amusement center, "
        "kids bouncing with joy, stars and sparkles in amber tones, "
        "energetic but warm and safe editorial illustration. "
        f"{_NEGATIVE}"
    ),
    "holiday": (
        f"{_ILLUSTRATION_BASE}. "
        "Illustrated seasonal holiday scene with families, festive decorations "
        "in amber, gold, and sage green, pumpkins or snowflakes depending on season, "
        "rounded joyful characters. "
        f"{_NEGATIVE}"
    ),
    "default": (
        f"{_ILLUSTRATION_BASE}. "
        "Illustrated happy family with children at a Northern Virginia community "
        "event, amber sun, sage green trees, smiling rounded characters, "
        "warm welcoming flat illustration. "
        f"{_NEGATIVE}"
    ),
}


# ── Pokémon TCG prompts ────────────────────────────────────────────────────────

POKEMON_PROMPTS: dict[str, str] = {
    "league": (
        f"{_PHOTO_BASE}. "
        "Children and teens playing Pokémon Trading Card Game at tables in a local game store, "
        "colorful card sleeves and binders visible, focused expressions, warm amber lighting, "
        "friendly competitive atmosphere, welcoming Northern Virginia game store setting. "
        f"{_NEGATIVE}"
    ),
    "prerelease": (
        f"{_PHOTO_BASE}. "
        "Excited kids and families at a Pokémon TCG prerelease event, opening booster packs, "
        "colorful cards spread on tables, big smiles, warm indoor lighting, "
        "game store tournament setting, celebratory atmosphere. "
        f"{_NEGATIVE}"
    ),
    "regional": (
        f"{_PHOTO_BASE}. "
        "Competitive Pokémon TCG regional championship, rows of players at tables, "
        "tournament scoreboard visible, intense focus, warm indoor venue lighting, "
        "families watching from sidelines, professional event atmosphere. "
        f"{_NEGATIVE}"
    ),
    "product_drop": (
        f"{_PHOTO_BASE}. "
        "New Pokémon TCG booster boxes and elite trainer boxes displayed on a bright shelf, "
        "colorful packaging with Pokémon artwork, warm amber lighting, "
        "clean retail product photography, inviting and exciting presentation. "
        f"{_NEGATIVE}"
    ),
    "product_drop_social": (
        f"{_ILLUSTRATION_BASE}. "
        "Bold flat illustration of a Pokémon TCG booster pack exploding open with cards, "
        "stars and sparkles in amber and sage green, energetic composition, "
        "no specific Pokémon characters — abstract colorful card art, hype aesthetic. "
        f"{_NEGATIVE}"
    ),
    "league_social": (
        f"{_ILLUSTRATION_BASE}. "
        "Illustrated children playing a trading card game at a cozy game store, "
        "colorful card illustrations floating around them, warm amber background, "
        "rounded friendly characters, community game night atmosphere. "
        f"{_NEGATIVE}"
    ),
    "default": (
        f"{_PHOTO_BASE}. "
        "Kids enjoying Pokémon Trading Card Game at a local Northern Virginia game store, "
        "colorful cards and accessories on table, warm amber lighting, "
        "friendly welcoming atmosphere, families in background. "
        f"{_NEGATIVE}"
    ),
}


def get_pokemon_prompt(event: dict, style: str = "website") -> str:
    """Return the best Pokémon TCG prompt for this event."""
    event_type = event.get("event_type", "")
    tags       = [t.lower() for t in event.get("tags", [])]

    if event_type == "product_drop":
        return POKEMON_PROMPTS["product_drop_social"] if style == "social" else POKEMON_PROMPTS["product_drop"]

    if "prerelease" in tags or "pre-release" in tags:
        return POKEMON_PROMPTS["prerelease"]

    if "regional" in tags or "championship" in tags:
        return POKEMON_PROMPTS["regional"]

    if "league" in tags or "weekly" in tags:
        return POKEMON_PROMPTS["league_social"] if style == "social" else POKEMON_PROMPTS["league"]

    return POKEMON_PROMPTS["league_social"] if style == "social" else POKEMON_PROMPTS["default"]


def get_website_prompt(event: dict) -> str:
    """Return the best website prompt for this event's type and tags."""
    return _match_prompt(WEBSITE_PROMPTS, event)


def get_social_prompt(event: dict) -> str:
    """Return the best social illustration prompt for this event."""
    return _match_prompt(SOCIAL_PROMPTS, event)


def _match_prompt(library: dict[str, str], event: dict) -> str:
    """Match an event to a prompt using event_type, deal_category, and tags."""
    event_type = event.get("event_type", "event")
    deal_category = event.get("deal_category", "")
    tags = [t.lower() for t in event.get("tags", [])]

    # Deal-type matching
    if event_type in ("deal", "birthday_freebie"):
        if event_type == "birthday_freebie":
            return library.get("deal_birthday", library["default"])
        if deal_category == "amusement":
            return library.get("deal_amusement", library["default"])
        return library.get("deal_restaurant", library["default"])

    # Event-type matching via tags
    tag_map = {
        "library": ["library", "storytime", "books"],
        "outdoor": ["outdoor", "festival", "park", "nature"],
        "arts-crafts": ["arts-crafts", "crafts", "art", "painting"],
        "sports": ["sports", "soccer", "swimming", "fitness"],
        "educational": ["educational", "stem", "science", "technology"],
        "music": ["music", "dance", "concert", "performance"],
        "nature": ["nature", "animals", "science", "environment"],
        "holiday": ["holiday", "seasonal", "halloween", "christmas", "easter"],
        "swimming": ["swimming", "water", "pool"],
        "theater": ["theater", "show", "performance", "circus"],
        "food": ["food", "cooking", "restaurant"],
    }

    for prompt_key, keywords in tag_map.items():
        if any(kw in tags for kw in keywords):
            if prompt_key in library:
                return library[prompt_key]

    return library["default"]
