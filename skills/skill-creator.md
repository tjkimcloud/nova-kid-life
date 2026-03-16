# Skill: Skill Creator — NovaKidLife

**Purpose:** Guide for creating new operational skills for this project. Use whenever a repeatable workflow, standard, or process needs to be codified so future Claude sessions can follow it consistently.

---

## When to Create a Skill

Create a skill when:
- A task will be repeated across multiple sessions (e.g. "add a new event type")
- A standard needs to be enforced consistently (e.g. SEO+GEO rules)
- A workflow has multiple steps that are easy to forget
- An integration has gotchas that need documenting (e.g. Supabase CLI quirks)

Do NOT create a skill for:
- One-time tasks
- Things already covered in CLAUDE.md
- Simple operations with no decision points

---

## Skill File Format

All skill files live in `/skills/` and follow this structure:

```markdown
# Skill: {Descriptive Name} — NovaKidLife

**Purpose:** One sentence: what this skill does and when to apply it.

---

## {Section 1: Prerequisites / Context}
What needs to be true before using this skill.

## {Section 2: The Process / Rules / Templates}
The actual content — steps, code, decisions.

## {Section 3: Verification / Checklist}
How to confirm the task was done correctly.
```

**Rules:**
- Imperative/verb-first instructions ("Run X", "Set Y to Z") — not "you should"
- Concrete over abstract — include actual code, actual commands, actual examples
- NovaKidLife-specific — tailor everything to this project's stack and conventions
- Include gotchas — things that will go wrong without the warning

---

## Skill Categories in This Project

| Category | Skills | Purpose |
|----------|--------|---------|
| **Deployment** | `deploy-frontend`, `deploy-api` | Ship code safely |
| **Database** | `db-migrate`, `seed-db` | Schema changes + test data |
| **Content** | `generate-event`, `generate-image`, `content-generation` | AI content pipeline |
| **SEO/GEO** | `seo-geo` | All standards for discoverable pages |
| **Social** | `post-social`, `social-strategy`, `brand-voice` | Social media operations |
| **Infrastructure** | `terraform-plan`, `terraform-apply`, `add-lambda` | AWS infra |
| **Quality** | `test-api`, `check-lighthouse`, `monitor` | Verification |
| **Development** | `add-component`, `scrape-events` | Building new features |
| **Autonomy** | `autonomous-agents`, `mcp-builder` | Self-running systems |
| **Meta** | `skill-creator` | Creating skills |

---

## Creating a New Skill — Step by Step

### 1. Identify the need
Ask: "Would a future session (or fresh conversation) know how to do this without instructions?"
If no → create a skill.

### 2. Draft the skill content
Write the skill file covering:
- What triggers using this skill
- All decisions that need to be made
- Exact commands, code, or API calls
- Expected outputs / verification steps
- Common errors and how to fix them

### 3. Create the file
```
skills/{kebab-case-name}.md
```

### 4. Register in CLAUDE.md
Add to the Skills Reference section:
```markdown
- `skill-name.md` — One-line description of what it does
```

### 5. Test it
Read the skill as if you've never seen it. Can you execute the workflow from only the skill content? If not, add more detail.

---

## Skill Quality Checklist

- [ ] Purpose line answers: "what does this do and when do I use it?"
- [ ] All code examples are copy-pasteable and tested
- [ ] Commands use correct paths for this project
- [ ] NovaKidLife-specific details (not generic advice)
- [ ] Gotchas are documented (e.g. "PowerShell uses `;` not `&&`")
- [ ] Verification step included
- [ ] Added to CLAUDE.md Skills Reference section

---

## Example: Creating a "Add Event Type" Skill

```markdown
# Skill: Add New Event Type — NovaKidLife

**Purpose:** Add a new event_type value to the system. Apply when a new content category
is identified that doesn't fit existing types.

## Steps

1. Add value to DB constraint:
   Create migration `supabase/migrations/{timestamp}_add_{type}_event_type.sql`:
   ALTER TABLE events DROP CONSTRAINT events_event_type_check;
   ALTER TABLE events ADD CONSTRAINT events_event_type_check
     CHECK (event_type IN (...existing..., '{new_type}'));

2. Add to TypeScript EventType union in `src/types/events.ts`

3. Add to Python EventType enum in `services/events-scraper/scrapers/models.py`

4. Add prompt in `services/image-gen/prompts.py` under WEBSITE_PROMPTS + SOCIAL_PROMPTS

5. Run: supabase migration up

6. Run: npm run type-check (from apps/web/)

## Verify
- Supabase Studio shows new constraint value
- TypeScript compiles without errors
- Image gen service loads without import errors
```
