# Errors & Fixes — NovaKidLife

Running log of bugs encountered and how they were resolved.
Add entries in reverse-chronological order (newest at top).

Format:
```
## YYYY-MM-DD — Short description
**Session:** N
**Error:** What happened
**Root cause:** Why it happened
**Fix:** What resolved it
**Prevention:** How to avoid it next time
```

---

## 2026-03-13 — bash script failed on Windows (WSL not configured)
**Session:** 1
**Error:** `bash apps/web/scritps/download-fonts.sh` → `WSL (10 - Relay) ERROR: CreateProcessCommon:800: execvpe(/bin/bash) failed`
**Root cause:** (1) Typo in path (`scritps` → `scripts`). (2) WSL is installed but misconfigured — `/bin/bash` unavailable inside WSL relay.
**Fix:** Replaced bash script with `apps/web/scripts/download-fonts.mjs` (Node.js, cross-platform). Run with: `node apps/web/scripts/download-fonts.mjs` from repo root.
**Prevention:** Prefer Node.js scripts for cross-platform dev tooling in this project. Save bash scripts for CI/CD only (Linux runners).

---

<!-- Add new entries above this line -->
