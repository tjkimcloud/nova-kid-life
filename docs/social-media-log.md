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
- ⬜ Buffer connected to Facebook page
- ⬜ Buffer profile ID saved to SSM: `/novakidlife/buffer/profile-ids`

### Instagram
- ⬜ Account created: `@novakidlife`
- ⬜ Account type: Business (not Creator)
- ⬜ Profile photo: Logo mark (square, recognizable at small size)
- ⬜ Bio written (150 chars max, include link in bio)
- ⬜ Link in bio: `novakidlife.com` (or Linktree if multi-link needed)
- ⬜ Connected to Facebook page
- ⬜ Buffer connected to Instagram business account
- ⬜ Buffer profile ID saved to SSM

### Twitter / X
- ⬜ Account created: `@novakidlife`
- ⬜ Profile photo: Logo (400×400px)
- ⬜ Header image: NoVa landscape with family (1500×500px)
- ⬜ Bio written (160 chars max, include NoVa, family events)
- ⬜ Website URL set
- ⬜ Buffer connected
- ⬜ Buffer profile ID saved to SSM

---

## Content Strategy

### Posting Schedule (automated via Buffer + social-poster Lambda)

| Platform | Frequency | Times (EST) |
|----------|-----------|-------------|
| Facebook | 1×/day | 9am weekdays, 10am weekends |
| Instagram | 1×/day | 12pm weekdays, 11am weekends |
| Twitter/X | 2×/day | 9am + 5pm weekdays |

### Post Types

1. **Event announcement** (primary) — automated via `social-poster` Lambda
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

## Buffer Configuration

- ⬜ Buffer account: Free tier initially (10 posts/profile queued)
- ⬜ Upgrade to Essentials ($6/mo) when queue regularly hits limit
- ⬜ Posting schedule configured in Buffer dashboard
- ⬜ All 3 profiles connected
- ⬜ API access token generated and stored in SSM
- ⬜ Profile IDs retrieved from API and stored in SSM

Retrieve profile IDs:
```bash
curl "https://api.bufferapp.com/1/profiles.json?access_token=<TOKEN>" | jq '.[].id'
```

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
- Buffer Analytics (built-in with paid plan)
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
<!-- Add session notes here as social strategy evolves -->
