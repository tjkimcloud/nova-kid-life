# Content Structure Templates — NovaKidLife

Reference file for `seo-content-writer.md`. Templates for long-form content types.

---

## Template 1: Event Roundup Post

**Use for:** "Best X Events This Weekend", "Top Family Events in [City] This Month"

```
URL:    /blog/{season-or-date}-family-events-{city}-va
Title:  Best Family Events in {City}, VA — {Month} {Year}
H1:     {Number} Best Family Events in {City}, VA This {Month}

[Quick Answer block — first 200 words, no images]
## Quick Answer: Top {N} Family Events in {City} This {Month}
1. {Event Name} — {Date}, {Location}. {One-line description.}
2. ...
(numbered list, concise, no links in Quick Answer block)

[Body]
## {Event Name 1}
{Full details: date, time, location, age range, cost, parking, tips}
[Event Card component or link]

## {Event Name 2}
...

## Frequently Asked Questions
### What are the best free family events in {City} this month?
{Direct answer, 40–50 words}

### Are there family events in {City} this weekend for toddlers?
{Direct answer}

### Do I need to register for events at {Library}?
{Direct answer}

[Schema: Article + FAQPage + ItemList]
[Internal links: 3–5 event pages + events listing + related blog posts]
```

---

## Template 2: Neighborhood Activity Guide

**Use for:** "Best Things to Do with Kids in [City], VA", location guides

```
URL:    /blog/{activity}-kids-{city}-va
Title:  {Number} Best {Activity} for Kids in {City}, VA ({Year})
H1:     {Number} Best {Activity} for Kids in {City}, Virginia

[Quick Answer block]
## Quick Answer: Top {N} {Activity} Spots in {City}
1. {Venue Name} — {One-line description with address}
...

[Intro — 150 words, mention neighborhood landmarks]

## {Venue Name 1} — {City}
- **Address:** {full address}
- **Hours:** {hours}
- **Ages:** {age range}
- **Cost:** {free/cost}
- **Tip:** {parent tip from local POV}
[Link to events at this venue]

## {Venue Name 2}...

## Tips for Visiting {City} with Kids
{Short practical section — parking, best times, what to bring}

## Frequently Asked Questions
[3–5 FAQs matching parent voice search queries]

[Schema: ItemList + LocalBusiness per venue + FAQPage]
[Update: "Last Updated: {Month Year} — verified {date range}"]
```

---

## Template 3: Seasonal Family Content

**Use for:** "Best Fall/Spring/Summer/Winter Activities", holiday guides

```
URL:    /blog/{season}-family-events-northern-virginia-{year}
Title:  Best {Season} Family Events in Northern Virginia {Year}
H1:     {Number} Best {Season} Activities for Kids in Northern Virginia

[Quick Answer block — top 5 picks with one-liners]

[Intro — mention why this season is special in NoVa, 100 words]

## Free {Season} Events
{3–5 events, brief descriptions}

## {Season} Outdoor Activities
...

## Holiday Events in NoVa This {Season}
...

## By County
### Fairfax County
### Loudoun County
### Arlington
### Prince William

## Frequently Asked Questions
[4 FAQs — seasonal queries parents type]

[Schema: Article + FAQPage + ItemList]
[Note: Update the same URL each year — do NOT create new URLs per year]
[Add "Last Updated: [date]" prominently — freshness signal for LLMs and Google]
```

---

## Template 4: "Best of" List Post

**Use for:** evergreen lists — birthday freebies, kids eat free, Pokémon leagues, etc.

```
URL:    /blog/{topic}-northern-virginia (or {topic}-{city}-va)
Title:  {Complete Guide title} — NovaKidLife
H1:     The Complete Guide to {Topic} in Northern Virginia

[Quick Answer block — top 5 with one-liners]
## Quick Answer: Best {Topic} in Northern Virginia
1. ...

[Intro — why this guide exists, what makes it comprehensive, 100 words]
[Mention: "Updated {Month Year} — verified from {N} sources"]

## {Category 1}
{Items with name, details, tips}

## {Category 2}
...

## How to Use This Guide
{Short practical section}

## Frequently Asked Questions
[5 FAQs — exact queries parents type into AI tools and search]

[Schema: ItemList + FAQPage]
[Strategy: most comprehensive version on the internet — include EVERY entry]
[Target: NoVa Facebook group shareability — write for the shareable headline]
```

---

## Universal Content Rules (apply to all templates)

1. **Answer first** — Quick Answer block in first 200 words, no images or links that break AI extraction
2. **Keyword in first 100 words** — primary keyword appears naturally within the opening paragraph
3. **H2 per item** for list posts — Google and LLMs use H2s as entity anchors
4. **3–5 internal links** to event pages; **2–3 external links** to authoritative sources (county sites, library, official venue)
5. **FAQ section required** — phrase questions in parent voice, answers 40–50 words each
6. **"Last Updated" date** visible on page — LLMs deprioritize stale content
7. **Length targets:** pillar content 1,500–3,000 words; supporting posts 800–1,200 words
8. **Schema required:** Article minimum; add FAQPage if FAQs included; ItemList if it's a list
