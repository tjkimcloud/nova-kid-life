---
name: generate-image-source
description: Image sourcing logic for the NovaKidLife image-gen pipeline — how sourcer.py selects a source image, the Google Places pre-seeded venue list, Unsplash/Pexels fallback chain, and all three prompt libraries (WEBSITE_PROMPTS, SOCIAL_PROMPTS, POKEMON_PROMPTS). Reference when adding new venues, extending the prompt library, or debugging why an event got AI-generated instead of sourced.
triggers:
  - image sourcing
  - sourcer
  - prompt library
  - Google Places
  - Unsplash
  - Pexels
  - WEBSITE_PROMPTS
  - SOCIAL_PROMPTS
  - POKEMON_PROMPTS
---

# Skill: Image Sourcing Reference

**Service:** `services/image-gen/sourcer.py` + `services/image-gen/prompts.py`

---

## Sourcing Priority Chain

```
Event dict
    │
    1. event["image_url"]      — if present and looks like a real image (not placeholder/icon)
    2. Google Places Photos    — for known NoVa venues (pre-seeded Place IDs)
    3. Unsplash API            — keyword search from event tags
    4. Pexels API              — fallback if Unsplash returns nothing
    5. None                    → AI generation (Imagen 3 → DALL-E 3)
```

Sourced images (steps 1–4): **$0** — skip all AI generation calls.
AI fallback (step 5): ~$0.04/image (Imagen 3) or ~$0.08 (DALL-E 3).

---

## Google Places — Pre-seeded Venue IDs

Requires: `GOOGLE_PLACES_API_KEY` env var (falls back gracefully without it).

Pre-seeded Place IDs (edit `sourcer.py` to add more):
- Fairfax County Library system
- George Mason University
- Reston Town Center
- Wolf Trap National Park for the Performing Arts
- Burke Lake Park
- Meadowlark Botanical Gardens
- Claude Moore Colonial Farm
- Sully Historic Site

**To add a new venue:** Get the Google Places ID from the Google Places API or Maps URL, add it to the `VENUE_PLACE_IDS` dict in `sourcer.py`.

---

## Prompt Libraries (`prompts.py`)

### Website (photorealistic editorial photography)

`WEBSITE_PROMPTS` — 14 keys:
`library`, `outdoor`, `arts-crafts`, `sports`, `educational`, `music`, `nature`,
`holiday`, `swimming`, `theater`, `food`, `deal_restaurant`, `deal_birthday`,
`deal_amusement`, `default`

Style constant:
```
"Professional editorial photography, warm golden hour lighting, amber and sage color tones,
sharp focus, Northern Virginia suburban setting"
```

### Social (flat editorial illustration)

`SOCIAL_PROMPTS` — same 14 keys as WEBSITE_PROMPTS.

Style constant:
```
"Flat editorial illustration, warm amber and sage green color palette, rounded friendly shapes,
clean vector art style, families and children, joyful community atmosphere"
```

### Pokémon TCG (`section = 'pokemon'` events only)

`POKEMON_PROMPTS` — 7 keys:
`league`, `prerelease`, `regional`, `product_drop`, `product_drop_social`,
`league_social`, `default`

Events with `section = 'pokemon'` automatically route to `POKEMON_PROMPTS`.

### Prompt selection

```python
from prompts import get_website_prompt, get_social_prompt, get_pokemon_prompt

# Standard events
website_prompt = get_website_prompt(event)   # tag-based matching
social_prompt  = get_social_prompt(event)

# Pokémon events
website_prompt = get_pokemon_prompt(event, style="website")
social_prompt  = get_pokemon_prompt(event, style="social")
```
