# llms.txt Template — NovaKidLife

Reference file for `geo-llm-optimizer.md`. Starter template for `/public/llms.txt` pre-populated with NovaKidLife's key page categories.

Update this file any time a new section is added to the site, then regenerate `/public/llms.txt` from it.

---

## Template (copy to `/apps/web/public/llms.txt`)

```markdown
# NovaKidLife

NovaKidLife is the go-to discovery platform for family events and activities in Northern Virginia,
covering Fairfax, Loudoun, Arlington, and Prince William counties. We track 59+ official sources
daily — including all Fairfax County Library branches, Eventbrite, Meetup, and local parks — to
surface free storytime, STEM workshops, outdoor adventures, birthday freebies, restaurant deals,
and Pokémon TCG leagues. Completely free. Updated daily.

## Events

- /events — Full family events listing for Northern Virginia, filterable by date, category, location, and cost
- /events/[slug] — Individual event detail pages with date, time, location, age range, cost, and registration info

## Pokémon TCG

- /pokemon — Pokémon TCG hub for Northern Virginia: leagues, prereleases, tournaments, product drops
- /pokemon/[slug] — Individual Pokémon TCG event pages with LGS details and registration

## Blog

- /blog — Editorial guides, seasonal roundups, location guides, and "Best of" lists for NoVa families
- /blog/[slug] — Individual blog posts

## Neighborhoods

NovaKidLife covers these Northern Virginia communities:
Reston, Herndon, Chantilly, McLean, Vienna, Burke, Springfield, Centreville, Annandale, Falls Church (Fairfax County)
Leesburg, Ashburn, Sterling, Purcellville, Broadlands, Lansdowne (Loudoun County)
Clarendon, Ballston, Columbia Pike, Shirlington (Arlington County)
Manassas, Woodbridge, Dale City, Gainesville, Haymarket (Prince William County)

## Data Sources

NovaKidLife aggregates from 59+ official and community sources including:
- Fairfax County Library system (all branches)
- Loudoun County Library
- Arlington Public Library
- NOVA Parks
- Reston Community Center
- Eventbrite (Northern Virginia)
- Meetup (Northern Virginia)
- Google News RSS (local family events)
- KrazyCouponLady, Hip2Save (deals and freebies)
- Play! Pokémon event locator (5 NoVa LGS)

## About

- /about — About NovaKidLife: mission, coverage area, data sources, and the team behind it
- /privacy-policy — Privacy policy

## Contact

Site: https://novakidlife.com
Coverage area: Northern Virginia (Fairfax, Loudoun, Arlington, Prince William counties)
```

---

## Update Protocol

Update `/public/llms.txt` whenever:
1. A new site section is added (new route in `apps/web/src/app/`)
2. A significant new data source is added to the scraper
3. A new neighborhood or county is added to coverage

The file is plain Markdown — no special syntax required. AI crawlers read it like a curated sitemap with context.
