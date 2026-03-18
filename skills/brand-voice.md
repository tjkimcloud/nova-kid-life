# Skill: Brand Voice & Guidelines — NovaKidLife

**Purpose:** Define and maintain consistent tone, voice, and visual identity across all NovaKidLife content — event descriptions, blog roundups, social posts, emails, UI copy, and marketing materials. Apply when writing any user-facing content.

> **Two distinct voices exist in this guide:**
> - **Event descriptions** (Section 5 in `content-generation.md`) → answer-first, concise, factual
> - **Blog posts / roundups** (Section 6 below) → parent-to-parent, warm, personality-forward
>
> Do not mix them. An event card should be crisp. A blog post should feel human.

---

## Brand Identity

**What NovaKidLife is:**
The most trusted, complete, and up-to-date guide to family events and kids activities in Northern Virginia. We save parents time by aggregating and curating events from 50+ local sources so they don't have to.

**Who we serve:**
Parents and caregivers in Northern Virginia (Fairfax, Loudoun, Arlington, Prince William) with children ages 0–18. They're busy, want value for their family's time, and care about their local community.

**Our promise:**
You'll never miss a great event in your backyard again.

---

## Voice Attributes

| Attribute | What it means | Example ✅ | Example ❌ |
|-----------|--------------|-----------|-----------|
| **Warm** | Friendly, approachable — like a neighbor who knows everything happening locally | "Don't miss this one — it fills up fast!" | "This event has limited capacity." |
| **Helpful** | Lead with value. Give parents what they need to decide quickly | "Free, no registration required — just show up." | "Please see event details." |
| **Local** | Know the place. Use real neighborhood names, not just county names | "At the Chantilly branch on Stringfellow Rd" | "At a Fairfax County Library location" |
| **Concise** | Parents are busy. No fluff. Get to the point fast | "Storytime for ages 2–6. Free. Saturday 10am." | "We are excited to present an amazing opportunity for young readers..." |
| **Excited but not breathless** | Enthusiasm without exclamation points on every sentence | "This is one of the best fall events in NoVa." | "Amazing!!! Don't miss this incredible opportunity!!!" |

---

## Tone by Context

### Event descriptions (website)
- Answer-first: what, when, where, who, cost, how to register — in that order
- Present tense, active voice
- No marketing fluff in the first paragraph
- Descriptive details that help parents visualize: "kids can touch real farm animals, ride the hayride, and pick their own pumpkin"
- Specifics over vague claims: "ages 3–8" not "young children"

### Social media copy
- More casual than website — contractions, shorter sentences
- Platform-appropriate energy (Twitter: snappy; Instagram: visual-first; Facebook: community tone)
- Always include the critical logistics (date, time, location, cost) — never make parents click just to find out when it is
- Use emojis sparingly — 1–2 per post max, functional not decorative

### Error states / empty states (UI)
- Empathetic, not robotic
- Suggest a next step
- "No events matched your filters — try clearing the date range or browsing all events."
- Never: "No results found."

### Email / newsletter
- Subject lines: specific and benefit-led ("5 Free Events This Weekend in Fairfax")
- Preview text adds context, never repeats subject
- Short paragraphs, bullet points for event lists
- Single CTA per section

---

## Language Rules

**Always say:**
- "Northern Virginia" or "NoVa" (not "the DMV" — we're VA-focused)
- Specific city names ("Reston", "Ashburn", "Centreville")
- "free to attend" not just "free" (clarifies it's not just free registration)
- "kids" or "children" (not "little ones" — avoid cutesy)
- "parents and caregivers" when addressing the audience directly

**Never say:**
- "Please note that..." (just say it)
- "We are pleased to announce..."
- "Amazing opportunity"
- "Don't forget!" (condescending)
- "All ages" when we know the actual age range
- "Click here" (use descriptive link text)

**Numbers:**
- Ages: "ages 3–8" not "3 to 8 years old"
- Times: "10:00 AM" not "10am" or "10 AM" (consistency)
- Prices: "$5/person" not "five dollars per person"
- Dates: "Saturday, March 21" (no year unless cross-year context)

---

## Visual Identity

### Colors (CSS + Tailwind tokens)
| Name | Tailwind | Hex (approx) | Use |
|------|---------|-------------|-----|
| Amber 500 | `primary-500` | `#F59E0B` | CTAs, accents, FREE badge bg |
| Amber 600 | `primary-600` | `#D97706` | Hover states, headings |
| Sage 700 | `secondary-700` | `#4B7B5E` | Body text, nav |
| Sage 100 | `secondary-100` | `#DCFCE7` | Card borders, subtle backgrounds |
| Sage 800 | `secondary-800` | `#2D5F45` | Strong emphasis, titles |

### Photography style (for AI-generated + sourced images)
- **Website images:** Warm editorial photography — golden hour light, amber tones, real families (not stock-photo-perfect). No cold blues.
- **Social images:** Flat editorial illustration — amber + sage palette, clean vector art, bold typography overlay
- **Never use:** Dark images, clinical white backgrounds, generic stock photos
- **Image alt text pattern:** "[What's happening] at [location] in [city], Virginia" (already AI-generated per SEO spec)

### Typography
- Headings: **Nunito** (800 weight for H1, 700 for H2, 600 for H3) — friendly, rounded
- Body: **Plus Jakarta Sans** (400 normal, 500 medium) — clean, readable
- Never mix in other fonts

---

## NovaKidLife Personas (use when generating content)

### Primary: "Busy Parent Beth"
- Mom of 2 kids (ages 4 and 7), Fairfax County
- Works full-time, weekend is precious family time
- Wants activities that are worth the drive, age-appropriate, and not going to break the bank
- Discovers events Sunday evening while planning next week
- Follows local Facebook groups but overwhelmed by noise

### Secondary: "Pokémon Dad Dave"
- Dad who plays Pokémon TCG with his 10-year-old
- Wants to find local leagues, prerelease events, and know where to buy new sets
- Highly loyal if we're the reliable source for Pokémon events in NoVa
- Shares content in Pokémon Facebook groups and Discord

---

## Content Quality Checklist

Before publishing any piece of content:
- [ ] Answers the parent's key question (what? when? where? free?)
- [ ] No filler sentences in the first 2 lines
- [ ] Specific city mentioned (not just "Northern Virginia")
- [ ] Age range stated or "all ages welcome" confirmed
- [ ] Cost clearly stated ($0 = "Free to attend")
- [ ] Tone is warm + helpful, not clinical or breathless
- [ ] No exclamation points in consecutive sentences
- [ ] Link to event page or registration included

---

## Blog Voice — Roundup Posts ("Things To Do This Weekend")

> This section governs all blog posts: weekend roundups, date-specific posts,
> location-specific posts, free events roundups, and rainy-day/indoor guides.
> These are the SEO-driving pages that bring new parents to the site.

### The Core Principle

Write like **the most organized parent in the neighborhood Facebook group** — the one who actually looked everything up, knows which parking lot to avoid, and tells you straight whether something is worth the drive. Not a press release. Not a tourism board. A peer.

Parents reading these posts are:
- Already a little stressed about filling the weekend
- Budget-aware and watching for "free" like a hawk
- Worried about whether it's right for their kid's age
- Often checking Thursday night or Friday morning — they need to act on it fast

The voice should quietly address all four without ever saying "as a busy parent."

---

### POV and Person

| When | Use | Avoid |
|------|-----|-------|
| All blog posts | **"you" / "your kids" / "your family"** (second person) — warm, direct, scales to AI generation | First-person singular "I took my kids" — too personal, doesn't scale |
| Community moments | **"we"** sparingly — "we know how fast the weekend goes" | Overusing "we" — starts to sound corporate |
| Never | — | Third-person ("parents should...") — creates distance |

---

### Hook Paragraph Rules

The opening 2–3 sentences are everything. Parents decide in the first line whether to keep reading.

**The hook must do one of these:**
1. Acknowledge the parent's Saturday situation directly
2. Frame what kind of weekend is ahead (big calendar, quiet weekend, rainy, etc.)
3. Lead with the best thing on the list

**Length:** 2–3 sentences max. Then get into the events.

**Examples — approved hooks:**

> The weekend is here and for once, the calendar is actually full. Whether you want something free to burn a Saturday morning or want to make a whole afternoon of it, Northern Virginia is stacked March 21–23. Here's everything worth loading the kids into the car for.

> If your kids have already asked "what are we doing this weekend" before you finished your coffee, this one's for you. Here's what's happening in Northern Virginia March 21–23 — sorted by area so you're not driving across three counties.

> A rainy Saturday doesn't have to mean screen time all day. Northern Virginia has more indoor options than most parents realize — here are the best ones open this weekend.

> Not a huge weekend for events, but the ones happening are genuinely good. Short list, high quality — here's what we'd circle for March 21–23.

**Examples — rejected hooks:**

> ❌ "Here are the top family events happening in Northern Virginia this weekend, March 21–23, 2026." *(directory voice — no personality)*
> ❌ "What an AMAZING weekend ahead for NoVa families!!!" *(breathless — reads like spam)*
> ❌ "As the weather warms up, families across Northern Virginia are looking for ways to enjoy the season together." *(filler — says nothing)*

---

### Event Blurb Format (within a blog post)

Each event entry in a roundup is **not** the same as an event description card. It's shorter, warmer, and ends with a reason to care.

**Structure (3–5 sentences):**
1. **What + who** — one sentence, plain language
2. **Key logistics** — date, time, location, cost (the facts parents need to decide)
3. **One insider detail** — registration deadline, parking tip, crowd timing, age nuance
4. **Optional: one genuine enthusiasm line** — specific, not generic

**Example blurb (good):**
> **Frying Pan Farm Park Spring Farm Days — Herndon**
> Free drop-in farm fun for kids of all ages — animals, wagon rides, and hands-on activities at one of Fairfax County's best free outdoor spots. Saturday and Sunday, 10:00 AM–4:00 PM, free to attend. It gets crowded by midday, especially on nice weekends — aim for early morning or after 2:00 PM. One of the best free Saturday options in Fairfax all spring.

**Example blurb (too dry — don't do this):**
> ❌ **Frying Pan Farm Park Spring Farm Days**
> This event takes place Saturday and Sunday from 10am-4pm at Frying Pan Farm Park in Herndon, Virginia. Admission is free. Activities include farm animals, wagon rides, and hands-on activities.

---

### The NoVa Insider Rule

Every roundup post should include **at least 2–3 details that only a local would know.** This is what separates NovaKidLife from Mommy Poppins templates and what makes parents share the post.

**Examples of insider details:**
- "Loudoun County Library branches fill up 15–20 minutes before storytime starts"
- "The side entrance parking lot off Monument Drive is always less chaotic than the main lot"
- "Cox Farms gets shoulder-to-shoulder by 11am on fall weekends — go at opening or after 3pm"
- "Wolf Trap's Children's Theatre in the Woods is first-come, first-served — bring a blanket and arrive 20 minutes early"
- "One Loudoun's outdoor events usually have free parking in the garage on weekends"
- "Barnes & Noble story times are walk-in, no registration — but the Tysons location fills fast"

If the AI generator doesn't have a specific insider tip for an event, it should skip this rather than fabricate one.

---

### Enthusiasm Calibration

| Approved | Rejected |
|----------|---------|
| "This one is worth the drive from Fairfax" | "This is an AMAZING event!!!" |
| "One of the best free activities in NoVa all year" | "Don't miss this incredible opportunity!" |
| "It fills up — register by Thursday" | "You won't want to miss this!!!" |
| "Genuinely great for the 4–8 age range" | "Kids of ALL ages will LOVE this!" |
| "Not flashy but kids always love it" | "So much fun for the whole family!" |
| A single exclamation point, used once per post | Exclamation points in consecutive sentences |

The rule: **earn the enthusiasm with specificity.** "One of the best free outdoor events in Loudoun this spring" lands because it's specific. "Amazing!!!" lands nowhere.

---

### Tone by Post Type

| Post type | Hook energy | Blurb length | Humor | Insider tips |
|-----------|------------|--------------|-------|-------------|
| Weekend roundup (main) | Warm, slightly wry, acknowledges the Saturday question | 4–5 sentences | Light | 2–3 minimum |
| Free events roundup | Practical, genuinely enthusiastic about the value | 3–4 sentences | Minimal | 2 minimum |
| Date-specific (e.g. "March 22") | Direct, no fluff — parents searching a specific date want facts | 2–3 sentences | None | 1–2 |
| Location-specific (e.g. "Fairfax this weekend") | Hyperlocal, neighborhood feel — like you know the area | 4–5 sentences | Light | 3+ |
| Rainy day / indoor | Problem-solving energy — "we've got you" | 4–5 sentences | Moderate | 2–3 |
| Week-ahead roundup | Looser, planning-mode energy | 3–4 sentences | Light | 1–2 |

---

### What To Never Say in Blog Posts

These phrases make the blog sound like a content farm, not a local parent:

- "There's something for everyone" — vague, meaningless
- "The whole family will love" — same
- "Make memories that last a lifetime" — cringe
- "Fun-filled" — overused to the point of saying nothing
- "Be sure to..." / "Make sure to..." — condescending
- "Exciting opportunity" — corporate
- "We are pleased to share" — press release
- "This beloved [community institution]" — tourism brochure
- Any sentence that could appear unchanged on a site about a different city

---

### Writing Craft — Sounds Human, Not AI

The biggest tell that content is AI-generated is predictable sentence structure, over-qualification, and filler transitions. These rules push the writing toward human.

**Use em dashes (—) for asides and emphasis:**
- "It's free to attend — no registration needed."
- "Great for ages 3–8 — older kids may want something with more action."
- "One of the best outdoor spots in Fairfax — and most parents still haven't been."
Em dashes add rhythm and create the natural "by the way" quality of how people actually talk.

**Sentence variety — mix short and long:**
```
Short, punchy. Then a longer sentence that adds context or paints the picture a little more
vividly. Then short again.
```
Never three long sentences in a row. Never five short ones in a row. Vary it.

**Contractions — always:**
- "It's" not "It is" / "You'll" not "You will" / "Don't" not "Do not"
- AI often writes without contractions. Contractions = human.

**Starting sentences with "And" or "But" — allowed, used sparingly:**
- "And it's free." is punchy and human. Fine once or twice per post.
- "But registration closes Thursday." creates useful urgency.

**Specific numbers over vague descriptors:**
- "About 25 minutes from Ashburn" not "conveniently located"
- "Ages 3–7 get the most out of it" not "great for young children"
- "Usually packed by 11am" not "can get crowded"

**What AI writes that we never write:**
| AI phrase | Human replacement |
|-----------|------------------|
| "Furthermore" / "Additionally" / "Moreover" | Just start a new sentence |
| "It's worth noting that..." | Just say it |
| "This is a great opportunity to..." | Say what it actually is |
| "Families can enjoy..." | "Kids can..." or just describe it |
| "In conclusion" / "To summarize" | End the post, don't announce you're ending |
| "Very" / "quite" / "rather" / "somewhat" | Cut it — or use a stronger word |
| "Needless to say" | Delete entirely |
| "As previously mentioned" | Delete entirely |
| Three adjectives in a row | Pick one |

**Oxford comma — always.** "Hayrides, farm animals, and pumpkin picking" not "hayrides, farm animals and pumpkin picking."

**Numbers:**
- Ages and costs always as digits: "ages 3–8", "$5/person"
- Numbers under 10 spelled out in prose: "two locations", "three reasons"
- Times: "10:00 AM" (already in brand rules)

---

### Blog UX & Readability — Mobile First

Over 70% of parents will read these posts on their phone, probably while standing in the kitchen on a Thursday night. Design the writing for that context.

**Paragraph length — 2–3 sentences max in the body, 1–2 on mobile-sensitive sections.**
A 6-sentence paragraph looks like a wall of text on a phone screen. Break it up. Every time.

**The logistics block — use for every event in a roundup:**
Instead of burying date/time/cost/location in a prose sentence, display it as a scannable block. Parents' eyes go straight to this before reading the blurb.

```
**[Event Name]** — [City, VA]
📅 [Day], [Month Date] · [Time]
📍 [Venue Name], [Address or cross-street]
💰 [Free to attend / $X per person / $X per child]

[3–4 sentence blurb with insider detail and one genuine enthusiasm line]

[→ Details & registration](link)
```

The emoji anchors (📅 📍 💰) act as visual signposts on mobile — parents can scan 10 events in 30 seconds without reading a word of prose. This is intentional. Let them scan first, read second.

**H2 headers every 4–6 events** to break up long lists and give parents a way to jump:
```
## Free Events This Weekend
## Fairfax County
## Loudoun County
## Arlington & Alexandria
## Indoor Options (Rainy Day Backup)
## Pokémon & Gaming
```

**"Jump to" nav at the top of longer posts (8+ events):**
```
Jump to: [Free Events](#free) · [Fairfax](#fairfax) · [Loudoun](#loudoun) · [Indoor](#indoor)
```
Anchor links are also internal SEO signals.

**One CTA every 5–6 events, not just at the end:**
```
→ See all Fairfax events this weekend at novakidlife.com/events
```
Parents who stop reading halfway still get the link.

**Bold the event name** at the start of every blurb — makes scanning faster and helps Google parse the structured content.

**Keep the post skimmable even without reading a single full sentence.** If a parent can get the event name, date, location, and cost just by scanning bold text, emoji anchors, and headers — you've nailed the UX.

---

### GEO & Backlink Optimization for Blog Posts

The answer-first, specific, factual structure of our content is deliberate — it's what makes these posts both GEO-citable and backlink-worthy.

**Why answer-first matters for GEO (LLMs):**
When someone asks Claude, ChatGPT, or Perplexity "what's happening in Fairfax this weekend," LLMs look for:
1. Direct answers to the exact question (not "it depends" preambles)
2. Specific dates, locations, costs — not vague descriptions
3. Content that reads as authoritative, not promotional
4. Structured information they can pull as a citation

Our logistics blocks (date, venue, cost in consistent format) are exactly what LLMs parse and cite. Every event blurb is a potential standalone LLM answer.

**Why specificity drives backlinks:**
Vague content ("great family fun in NoVa!") gets no links. Specific content gets quoted.
- "Free drop-in storytime at Chantilly Library, Saturday 10:00 AM, no registration needed" — citable by local Facebook groups, school newsletters, HOA boards, other blogs
- The more specific and accurate our data, the more we become the source others link to

**Structure every blog post to be quotable in chunks:**
Each event blurb should be able to stand alone as a fact. If a local HOA newsletter wants to share one event, they should be able to copy-paste a single blurb with a link back to us. That's a backlink.

**FAQ section at the bottom of every roundup post — required:**
These directly target LLM citation and "People Also Ask" rich results.

Format:
```
## Frequently Asked Questions

**What free events are happening in Northern Virginia this weekend?**
[List 3–4 free events from the post with one-sentence descriptions and dates]

**What's happening in Fairfax this weekend for kids?**
[Fairfax-specific events from the post]

**What indoor activities are available for kids in Northern Virginia this weekend?**
[Indoor options from the post]

**Do I need to register in advance for weekend family events in Northern Virginia?**
[General answer + note which specific events in this post require registration]
```

The FAQ questions should exactly match how parents phrase searches and how they'd ask an LLM. These also get FAQPage JSON-LD schema applied automatically.

**Internal linking — required on every post:**
- Link every event name to its individual `/events/[slug]` page on NovaKidLife
- Link location H2 headers to `/events?location=[id]` filtered view
- Link the closing CTA to `/events` or the relevant section
- This builds topical authority for "things to do + [NoVa city]" keyword clusters

---

### AI Generation Prompt Reference

When generating blog post content via GPT-4o-mini, include these instructions:

```
You are writing for NovaKidLife, a family events site for Northern Virginia parents.
Voice: warm, local, parent-to-parent. Like the most organized parent in the neighborhood
Facebook group — not a tourism board, not a press release.

VOICE RULES:
- Second person ("you", "your kids") — never first-person singular
- Use contractions: "it's", "you'll", "don't", "there's" — always
- Use em dashes (—) for asides and natural parentheticals
- Vary sentence length: mix short punchy sentences with longer descriptive ones
- Specific numbers over vague descriptors: "25 minutes from Ashburn" not "nearby"
- Never: "Furthermore", "Additionally", "It's worth noting", "Needless to say",
  "In conclusion", "fun-filled", "the whole family will love", "make memories",
  "exciting opportunity", "families can enjoy"
- Oxford comma always
- One exclamation point per post maximum

STRUCTURE:
- Hook: 2–3 sentences acknowledging the parent's weekend situation (see brand guide)
- Each event: logistics block (📅 📍 💰) then 3–5 sentence blurb
- Bold the event name at the start of each entry
- H2 headers to group events by type or geography every 4–6 events
- FAQ section at the bottom (4 questions targeting parent search intent)
- Closing CTA linking to novakidlife.com/events

CONTENT:
- Insider details must be real and specific — skip if uncertain, never fabricate
- One genuine enthusiasm line per blurb max — must be specific, not generic
- Link every event name to its NovaKidLife event page
- Every blurb should be able to stand alone as a quotable fact (backlink target)
```
