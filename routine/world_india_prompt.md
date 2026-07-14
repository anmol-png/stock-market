# Headless prompt — decode the INDIA half of the World feed

You are writing ONE half of the World news feed: the **INDIA** stories only. This is split from the
global half so each generation stays small and reliable — write only India stories here.

Follow `analyze/world_prompt.md` as the authority for the DECODING SCHEMA and the depth/quality bar
(every field fully decoded, plain language, define jargon, the_lesson + concepts, real sources).

## Do this
1. Read `dashboard/archive/world-2026-*.json` — the 1–2 most recent — for story continuity (`thread`).
2. Read `output/world-raw-latest.json`. Use the items with `"region": "india"` (national news, economy,
   policy, markets, India-in-the-world). WIDE net: RSS + Google News India + **Reddit (r/india, …) +
   Twitter/X via nitter (ANI, PTI, NDTV)**.
3. **VET before publishing:** Reddit/X are LEADS ONLY — corroborate via WebSearch; DROP the unconfirmed;
   never present a rumor/single tweet as fact; de-dupe into one story; cite the primary outlet (real URL).
4. Produce **~20 INDIA stories** (target 20; quality/verification over volume — fewer is fine if fewer
   genuinely matter). Order most-important-and-newest first. Range across national/politics, economy &
   policy, markets, and India's place in the world.
5. For EVERY story include **`published_iso`** = the exact time the news broke (copy from the raw item, or
   the earliest credible report you confirm). **Never invent a time**; null only if truly unknown. Every
   story's `category` must be `"india"`. Fill all required decode fields per `analyze/world_prompt.md`.

## Write STRICT JSON to `output/world-india.json`
```json
{
  "generated_at": "<now, ISO with +05:30>",
  "stories": [ { ...full decoded story per analyze/world_prompt.md, "category":"india", with published_iso... } ]
}
```
Strict JSON only (no prose outside the file). When done, output one line: the #1 India story title.
