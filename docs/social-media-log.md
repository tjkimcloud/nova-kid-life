# Social Media Log — NovaKidLife

Running log of social media setup, strategy, and performance.

Legend: ✅ Done | 🔄 In Progress | ⬜ Not Started

---

## Platform Setup

### Facebook
- ⬜ Page created: "NovaKidLife"
- ⬜ Category: "Local Business" → "Community Organization"
- ⬜ Profile photo: NovaKidLife logo (400×400px)
- ⬜ Cover photo: NoVa family lifestyle image (820×312px)
- ⬜ Bio/About written (include "Northern Virginia", "family events")
- ⬜ Website URL: `https://novakidlife.com`
- ⬜ Call-to-action button: "Learn More"
- ⬜ Page verified (if eligible)
- ⬜ Ayrshare connected to Facebook page
- ⬜ Ayrshare API key saved to SSM: `/novakidlife/ayrshare/api-key`

### Instagram
- ⬜ Account created: `@novakidlife`
- ⬜ Account type: Business (not Creator)
- ⬜ Profile photo: Logo mark (square, recognizable at small size)
- ⬜ Bio written (150 chars max, include link in bio)
- ⬜ Link in bio: `novakidlife.com` (or Linktree if multi-link needed)
- ⬜ Connected to Facebook page
- ⬜ Ayrshare connected to Instagram business account

### Twitter / X
- ⬜ Account created: `@novakidlife`
- ⬜ Profile photo: Logo (400×400px)
- ⬜ Header image: NoVa landscape with family (1500×500px)
- ⬜ Bio written (160 chars max, include NoVa, family events)
- ⬜ Website URL set
- ⬜ Ayrshare connected

---

## Content Strategy

### Posting Schedule (automated via Ayrshare + social-poster Lambda — pending deployment)

| Platform | Frequency | Times (EST) |
|----------|-----------|-------------|
| Facebook | 1×/day | 9am weekdays, 10am weekends |
| Instagram | 1×/day | 12pm weekdays, 11am weekends |
| Twitter/X | 2×/day | 9am + 5pm weekdays |

### Post Types

1. **Event announcement** (primary) — automated via `social-poster` Lambda (pending Ayrshare deployment)
   - Event title, date, location, image, link

2. **Weekend roundup** (manual, weekly) — "Top 5 things to do this weekend in NoVa"

3. **Featured event** (manual, 2×/week) — deeper spotlight on one event

4. **Engagement posts** (manual, 1×/week) — "What's your favorite NoVa family spot?"

### Caption Template
```
🎉 [Event Title]

[Short description — 1 sentence]

📅 [Day, Month Date, Time]
📍 [City, VA]

Full details + tickets → novakidlife.com/events/[slug]

[Hashtags]
```

### Hashtag Strategy

**Always use:**
`#NoVaKids` `#NorthernVirginia` `#FamilyFun` `#NoVaFamilies`

**Rotate by content type:**
- Outdoor: `#OutdoorKids` `#NatureKids` `#NoVaParks`
- Free events: `#FreeKidsActivities` `#FreeNoVaEvents`
- Arts: `#KidsArts` `#NoVaArts`
- Seasonal: `#FairfaxFall` `#SummerFun` `#SpringActivities`

**Location-specific:**
`#FairfaxCounty` `#Arlington` `#Loudoun` `#PrinceWilliam`

---

## Ayrshare Configuration

> **Note:** Buffer was replaced by Ayrshare in Session 11. Buffer deprecated public API access for new users. The `social-poster` Lambda code was updated but the Lambda is NOT deployed yet.

- ⬜ Ayrshare account created at ayrshare.com
- ⬜ API key generated
- ⬜ API key stored in SSM: `/novakidlife/ayrshare/api-key`
- ⬜ All 3 social profiles linked in Ayrshare dashboard
- ⬜ social-poster Lambda updated for Ayrshare API calls
- ⬜ social-poster Lambda added back to Terraform + deployed

Ayrshare post endpoint: `POST https://app.ayrshare.com/api/post`

---

## Performance Tracking

### Metrics to Track (monthly)
| Metric | Target (Month 3) | Target (Month 6) |
|--------|-----------------|-----------------|
| Facebook page followers | 500 | 2,000 |
| Instagram followers | 300 | 1,500 |
| Twitter followers | 200 | 800 |
| Avg post reach (FB) | 200 | 1,000 |
| Link clicks/month | 100 | 500 |
| Website sessions from social | 5% of total | 15% of total |

### Tools
- Ayrshare Analytics (built-in)
- Google Analytics UTM parameters on all social links
- Facebook Insights
- Instagram Insights

### UTM Template
All social links use UTM parameters for attribution:
```
https://novakidlife.com/events/[slug]?utm_source=[fb|ig|twitter]&utm_medium=social&utm_campaign=event-post
```

---

## Launch Announcement Plan

- ⬜ Draft launch post for all 3 platforms
- ⬜ Join NoVa parenting Facebook groups (manual share of launch)
  - Northern Virginia Moms
  - Fairfax County Moms & Families
  - Loudoun County Parents
  - Arlington Families
- ⬜ Personal network share
- ⬜ Reach out to 3-5 NoVa parenting bloggers/influencers for coverage

---

## Notes & Observations

### 2026-03-11 — Buffer deprecated, migrated to Ayrshare
Buffer removed public API access for new users. All social automation code in `services/social-poster/` was updated to reference Ayrshare. The Lambda is not deployed until Ayrshare is set up (account + API key + profiles connected). SSM param `/novakidlife/ayrshare/api-key` needs to be populated before deployment.

<!-- Add session notes here as social strategy evolves -->
