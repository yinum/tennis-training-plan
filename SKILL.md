---
name: tennis-training-plan
description: >-
  Generate a targeted, realistic, periodized tennis training plan from a
  tennis-video-analysis skill report (or from a described level when no report exists):
  a macrocycle goal built on the report's top weaknesses, 3–4-week mesocycle phases
  (acquisition → consolidation → integration) with criterion-gated progression, concrete
  weekly session schedules with drills and measurable success metrics, load/safety rules,
  and a re-assessment loop back into video analysis. Use this skill whenever the user
  asks for a tennis training plan, practice plan/schedule, drills to improve, "how do I
  get to 4.0", how to fix weaknesses from their skill report, periodization, or what to
  practice this week/month — even if they don't say "plan".
---

# Tennis Training Plan

Turn a skill report into a plan the player will actually follow: targeted at the 2–3
gates that matter, honest about timelines, scheduled around their real life, and
progressed by criteria rather than by calendar.

**Paths**: `SKILL_DIR` = this skill's directory; `TENNIS_HOME` = `~/.tennis-analysis`
(override `$TENNIS_ANALYSIS_HOME`). Plans land in
`TENNIS_HOME/players/<slug>/plans/<date>/` (slug = lowercase hyphenated player name).

## Workflow

### 1. Find the source report

Look in `TENNIS_HOME/players/<slug>/history.json` for the latest entry; its
`analysis_dir` contains `assessment.json` (dimension scores, weaknesses with fixes,
development_plan with success metrics, specialties) and `report.md`. Pull from there:

- **Gates** — the development_plan priorities and lowest-scoring high-leverage
  dimensions (Rally Consistency, Movement, Serve weigh most).
- **Assets** — specialties and top strengths (the plan must feed these too).
- **Stage** — NTRP/band for calibrating drill levels and expectations.

No report? Offer to run the **tennis-video-analysis** skill first (better input =
better plan). If the user prefers, fall back to interviewing: self-rated NTRP,
biggest frustrations, what breaks down first in matches — and note in the plan that
it is built on self-description, not video evidence.

### 2. Interview for constraints (don't skip — this is what makes it realistic)

Ask, in one batch: sessions per week and minutes per session they can HONESTLY
commit · equipment access (wall / ball machine / hitting partner / coach / league
matches) · injuries or physical limits · goal (league level, tournament date,
"beat my friend") · any fixed events during the cycle. Default plan length is
10 weeks; shift to 8–12 to fit their calendar.

### 3. Design the plan

Read `references/periodization.md` (structure + realism guardrails) and
`references/drill-library.md` (drills by dimension, L1→L3, equipment variants).
Rules that are not negotiable:

- Max 2–3 focus areas per macrocycle, taken from the report's gates.
- Mesocycles gate on the report's **measurable success metrics** — advance when
  met, extend once when not, then simplify the drill level.
- Volume increase ≤ ~10%/week; a lighter week after every 3 build weeks.
- Every week pairs weakness work with one asset drill (motivation).
- Schedule exactly the committed sessions — never more. Every session fits the
  stated minutes including warm-up and play tail.
- The expectation note states, per the progression table, what this block can and
  cannot achieve ("this closes the split-step gate; 4.0 is a next-year outcome").

### 4. Write plan.json and build

Write `plan.json` (anywhere; it gets copied into the plan dir):

```json
{
  "player": "Yi", "date": "2026-07-03",
  "source_report": "/path/to/<video>_analysis/report.md",
  "goal": "markdown prose: the 2-3 gates and why they matter for the next band",
  "current_stage": {"ntrp": 3.5, "band": "3.0-4.0"},
  "constraints": {"sessions_per_week": 3, "session_minutes": 90,
                  "equipment": ["wall", "partner"], "injuries": [], "notes": ""},
  "macrocycle": {"weeks": 10, "theme": "Serve leg drive + split-step automation",
                 "expectation_note": "honest one-liner on what 10 weeks can deliver"},
  "mesocycles": [
    {"name": "Acquisition", "weeks": "1-4", "objective": "markdown prose",
     "emphasis": ["Serve leg drive", "Split step"],
     "exit_criteria": ["8/10 serves show knee bend <150 deg on video", "..."],
     "weekly_template": [
       {"day": "Tue", "minutes": 90, "focus": "Serve mechanics",
        "blocks": [{"name": "Warm-up + shadow serves", "minutes": 15, "detail": "...",
                    "metric": "optional per-block metric"}]}
     ]}
  ],
  "progression_rules": ["advance on criteria, not calendar", "..."],
  "reassessment": {"cadence_weeks": 10,
                   "method": "record 20+ min, same camera angle, re-run tennis-video-analysis"},
  "study_videos": [{"focus": "names the focus area / gate it serves",
                    "title": "video title from the search result — or the exact search phrase when url is null",
                    "url": "https://... or null", "platform": "youtube | bilibili",
                    "why": "one line: what to watch for, tied to this player's gate"}],
  "caveats": ["shoulder history: serve volume halved, band work before serve days", "..."]
}
```

**study_videos (required, 1–2 per focus area, 3–6 total).** Pro slow-motion for the
pattern each gate is chasing, drill tutorials for the phase-1 drills. Sourcing rules:

- A `url` may only come from a web search you ran **this session** (WebSearch or
  equivalent). Never write a video URL from memory — remembered video IDs are
  almost always dead links. No search tool in this harness → set `"url": null`
  and put the exact search phrase in `title`; the plan renders it as a suggested
  search.
- Query patterns that work: YouTube `"<pro> <stroke> slow motion"`,
  `"tennis <drill name> drill"`; Bilibili `site:bilibili.com 网球 <技术> 慢动作/教学`.
  Reliable YouTube channels for slow-motion pro technique: Be Gr8 at Tennis,
  Top Tennis Training, Feel Tennis, Essential Tennis.
- Search Bilibili as well as YouTube; include a Bilibili entry whenever a relevant
  result exists (many players prefer Chinese-language instruction — ask if unsure).
- Match videos to the source report's pro comparisons when it has them (e.g. a
  Sinner-pattern forehand gate → Sinner slow-motion, not a random pro).

Then:
```bash
python3 SKILL_DIR/scripts/build_plan.py plan.json [--publish ~/tennis/<date>]
```
This renders `training_plan.md` + self-contained `training_plan.html` (phase
timeline, weekly tables, exit-criteria callouts) into the player's plans directory.
The plans directory lives under a hidden dot-folder — pass `--publish DIR` to also
copy the deliverables into a user-visible folder when the user wants them findable.

### 5. Deliver

Summarize in chat: the 2–3 gates chosen and why, the phase structure, and the
week-1 schedule. Give both file paths. Close with the re-assessment instruction —
the loop back to tennis-video-analysis is what makes progress visible (radar
overlay + NTRP trend in the next report).

## Honesty requirements

- Never promise an NTRP band jump inside one macrocycle; cite the progression
  table in references/periodization.md when setting expectations.
- Warn that technique changes feel worse before better (acquisition dip).
- Injuries: substitute drills, cap volumes, and say when something needs a
  physio/coach rather than a plan.

## Codex / non-Claude harnesses / Windows

Plain python3 (stdlib only) — no harness-specific tools required. On Windows use
`python` instead of `python3`; paths under `~/.tennis-analysis` resolve to
`%USERPROFILE%\.tennis-analysis` automatically.
