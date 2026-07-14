# Headless prompt — decode the GLOBAL half of the World feed

You are writing ONE half of the World news feed: the **GLOBAL** stories only (everything that is NOT
India). This is split from the India half so each generation stays small and reliable — do NOT write
India stories here.

Follow `analyze/world_prompt.md` as the authority for the DECODING SCHEMA and the depth/quality bar
(every field fully decoded, plain language, define jargon, the_lesson + concepts, real sources). But
scope and output are as below.

## Do this
1. Read `dashboard/archive/world-2026-*.json` — the 1–2 most recent — for story continuity (`thread`).
2. Read `output/world-raw-latest.json`. Use the items with `"region": "global"` (categories geopolitics,
   economy, technology, science, health, climate). It's a WIDE net: reputable RSS + Google News +
   **Reddit + Twitter/X (via nitter)**.
3. **VET before publishing:** treat Reddit/X items as LEADS ONLY — corroborate each with a credible
   outlet via WebSearch; DROP anything you can't confirm; never present a rumor/single tweet as fact;
   de-dupe the same event into one story; cite the primary outlet (real URL).
4. Produce **~20 GLOBAL stories** (target 20; quality/verification over volume — return fewer if fewer
   genuinely matter and check out). Order most-important-and-newest first. Spread across geopolitics,
   economy, technology, science, health, climate — not 20 politics stories.
5. For EVERY story include **`published_iso`** = the exact time the news broke (copy from the raw item's
   `published_iso`, or the earliest credible report time you confirm). **Never invent a time**; null only
   if truly unknown. Category must be one of geopolitics|economy|technology|science|health|climate (never
   "india" in this file). Fill all required decode fields per `analyze/world_prompt.md`.

## Write STRICT JSON to `output/world-global.json`
```json
{
  "generated_at": "<now, ISO with +05:30>",
  "headline": "One sentence: the single most important thing in the world today (global).",
  "the_big_picture": "3–4 sentences connecting today's top global stories.",
  "stories": [ { ...full decoded story per analyze/world_prompt.md, with published_iso... } ],
  "also_notable": [ {"title":"...","why":"...","source":{"name":"...","url":"..."}} ],
  "disclaimer": "Decoded from public reporting for general understanding. Verify before relying on any single claim; details evolve."
}
```
Strict JSON only (no prose outside the file). When done, output one line: the #1 global story title.
