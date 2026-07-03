# tennis-training-plan — Design (2026-07-03)

## Goal
Turn a tennis-video-analysis skill report (or a described level, as fallback) into a
targeted, realistic, periodized training plan: macrocycle goal → mesocycle phases →
weekly microcycle schedules, with gradual progression rules, measurable exit criteria,
and a re-assessment loop back into tennis-video-analysis.

## User requirements (2026-07-02)
- Core function: generate targeted training plan based on the technical report.
- Must be realistic — gradual improvement, no fantasy timelines.
- Must be periodic — phased plan with a schedule.

## Interop with tennis-video-analysis
- Reads `~/.tennis-analysis/players/<slug>/history.json` and the latest
  `assessment.json` / report for: current stage, weaknesses (gates), development
  plan priorities, success metrics, specialties (assets to build around).
- Plans saved to `~/.tennis-analysis/players/<slug>/plans/<date>/` so both skills
  see one player timeline; re-assessment cadence tells the user when to record a
  new video and re-run the analysis skill (closing the loop).

## Shape
- Agent interviews for constraints (sessions/week, session length, equipment access:
  wall / ball machine / hitting partner / coach / league play, injuries, goal, event
  dates), then writes `plan.json`; `scripts/build_plan.py` (stdlib-only) renders
  `training_plan.md` + self-contained `training_plan.html` (same design language as
  the analysis report: palette tokens, light/dark, mesocycle timeline SVG, weekly
  tables).
- `references/periodization.md`: macro/meso/micro structure adapted to recreational
  tennis, realistic band-progression timelines, blocked→variable→random practice
  progression, load management.
- `references/drill-library.md`: drills per rubric dimension with 3 progression
  levels and equipment variants, so plans work for a player with only a wall as
  well as one with a coach.

## Realism guardrails (the point of the skill)
Progression-speed table by NTRP band; never promise a band jump inside one
macrocycle; volume increases capped ~10%/week; rest and deload weeks mandatory;
advance drills only when the exit criterion is met, regress after two failed weeks.
