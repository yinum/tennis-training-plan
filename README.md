# tennis-training-plan

An [agent skill](https://skills.sh) that turns a
[tennis-video-analysis](https://github.com/yinum/tennis-video-analysis) skill report
(or a self-described level) into a targeted, realistic, periodized training plan:

- **Macrocycle** (8–12 weeks) built on the report's top 2–3 gates — never more
- **Mesocycles** (acquisition → consolidation → integration) that advance on
  measurable exit criteria, not the calendar
- **Weekly session tables** with drills from a library covering every skill
  dimension at 3 progression levels, with wall / ball-machine / partner / coach
  variants — so the plan works even with no coach and only a wall
- **Realism guardrails**: NTRP progression-speed table (no band-jump promises),
  ≤10%/week load growth, deload weeks, injury pain-gating, an asset drill every
  week so the plan isn't pure weakness-grinding
- **Re-assessment loop**: ends by prescribing a new video for tennis-video-analysis,
  which overlays the new skill radar on the old one

Output: `training_plan.md` + a self-contained `training_plan.html` (phase timeline,
weekly tables, exit-criteria callouts). Works with Claude Code, Codex, and any agent
harness that can run CLI scripts.

## Install

```bash
git clone https://github.com/yinum/tennis-training-plan ~/.agents/skills/tennis-training-plan
ln -s ~/.agents/skills/tennis-training-plan ~/.claude/skills/tennis-training-plan   # Claude Code
ln -s ~/.agents/skills/tennis-training-plan ~/.codex/skills/tennis-training-plan    # Codex
```

No setup script — stdlib Python only. Plans are filed under
`~/.tennis-analysis/players/<name>/plans/` so both skills share one player timeline.

Then ask your agent: *"make me a training plan from my tennis report"*.
