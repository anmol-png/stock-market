# Daily routine — how the automation works

**The daily run is AUTOMATED on this Mac.** A LaunchAgent
(`~/Library/LaunchAgents/com.dailyintel.daily.plist`) fires [`run_daily.sh`](run_daily.sh) at login
and every 30 minutes; the script exits instantly once today's brief exists, so the net effect is
**one real run per day, the first time you open your laptop**. The script runs the deterministic
steps (fetch_world.py → fetch.py → analyze_stock.py --all), then invokes headless
`claude -p` (Max subscription) with [`claude_routine.md`](claude_routine.md) to write both briefs,
then publishes + archives (`build_dashboard.py`) and emails only if `.env` exists.

```bash
# manage it
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.dailyintel.daily.plist   # enable
launchctl bootout   gui/$(id -u)/com.dailyintel.daily                                # disable
bash routine/run_daily.sh --force                                                    # run now, manually
tail -f logs/daily.log                                                               # watch a run
```

> Cloud alternative (works with the Mac off): push to GitHub + `/schedule` a cloud routine +
> GitHub Pages. Not set up yet — the local LaunchAgent is the active path.

The block below is the legacy manual prompt (same steps, for pasting into an interactive session):

---

```
You are running the daily Intelligence update for this repo. Follow CLAUDE.md as your persona and
mission. You produce TWO separate briefs: World (decoded global news) and Markets. The reader is new
to markets and world affairs — DECODE and EXPLAIN everything, define jargon inline, never just
summarize. Do all of the following, in order:

1. Run: python fetch_world.py
   (Writes output/world-raw-latest.json — broad global headlines across geopolitics, economy, tech,
   science, health, climate, and India.)

2. Run: python fetch.py
   (Writes output/raw-latest.json — free prices, indicators, fundamentals, market news, calendars.)

3. Run: python analyze_stock.py --all
   (Computes the full industry technical suite -> a processed verdict per stock in
   dashboard/stocks/*.json, and rebuilds dashboard/stocks/index.json.)

=== WORLD PILLAR ===
4. Read output/world-raw-latest.json. Use WebSearch to confirm facts, get the latest, and fill gaps.
   Pick the 6–10 stories that genuinely matter globally today, ranked by importance, spread across
   categories. FULLY DECODE each per analyze/world_prompt.md: what_happened, why_it_matters,
   ripple_effects, why_now, watch_next, market_link (if any). Write the_big_picture connecting them.
   Never invent facts/numbers — cite at least one source per story. Save STRICT JSON to
   output/world-<today>.json AND output/world-latest.json (schema: analyze/world_prompt.md).

=== MARKETS PILLAR ===
5. Read output/raw-latest.json and dashboard/stocks/index.json. Use WebSearch for the most important
   market news (US, India, crypto/commodities). As the analyst in CLAUDE.md, write the Markets brief
   as STRICT JSON per analyze/brief_prompt.md. Rank what_to_watch by materiality. For each favorite,
   focus on what CHANGED since yesterday and EXPLAIN the technical read in plain English. Never invent
   numbers. Save to output/brief-<today>.json AND output/brief-latest.json.

6. Enrich the favorites' deep panels: for each favorite in the brief, open the matching
   dashboard/stocks/<TICKER>.json (^ -> _, / -> _) and set its "whats_new" and "news" fields from the
   brief, then save. This makes the "What changed" + "Recent news" sections show on each stock's page.

=== PUBLISH ===
7. Run: python build_dashboard.py   (publishes world.json + brief.json to the dashboard)

8. Run: python send.py              (emails the short two-pillar digest via Gmail SMTP)

9. Commit and push so GitHub Pages updates:
   git add dashboard && git commit -m "update: $(date +%F)" && git push

Report a one-line summary (the single most important world story + top market thing to watch) when done.
```
