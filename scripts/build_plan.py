#!/usr/bin/env python
"""Render an agent-authored plan.json into training_plan.md + a self-contained
training_plan.html, filed under the player's directory so the analysis and training
skills share one timeline.

Run with any python3 (stdlib only):
  python3 build_plan.py PLAN_JSON [--outdir DIR]

Default outdir: $TENNIS_ANALYSIS_HOME/players/<slug>/plans/<date>/
(plan.json is copied there too, so the plan directory is self-describing).
"""
import argparse, html, json, os, re, shutil, sys
from pathlib import Path

TENNIS_HOME = Path(os.environ.get("TENNIS_ANALYSIS_HOME", Path.home() / ".tennis-analysis"))
SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "assets" / "plan_template.html"

REQUIRED = ["player", "date", "goal", "current_stage", "constraints",
            "macrocycle", "mesocycles", "progression_rules", "reassessment", "caveats"]


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "player"


def md_lite(text):
    if not text:
        return ""
    out, in_list = [], False
    for line in str(text).split("\n"):
        s = html.escape(line.rstrip())
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
        if s.strip().startswith("- "):
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{s.strip()[2:]}</li>")
        else:
            if in_list:
                out.append("</ul>"); in_list = False
            if s.strip():
                out.append(f"<p>{s}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def timeline_svg(mesos, total_weeks):
    """Horizontal phase bar — ordinal single-hue ramp, direct labels."""
    W, H, x0, bar_y, bar_h = 640, 92, 8, 34, 26
    ramps = ["var(--ramp-a)", "var(--ramp-b)", "var(--ramp-c)"]
    usable = W - 2 * x0
    parts = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Plan timeline">']
    x = x0
    for i, m in enumerate(mesos):
        w = usable * (m["_weeks"] / total_weeks)
        color = ramps[min(i, len(ramps) - 1)]
        parts.append(f'<rect x="{x:.1f}" y="{bar_y}" width="{max(w - 2, 2):.1f}" height="{bar_h}" '
                     f'rx="4" fill="{color}"><title>{html.escape(m["name"])}: weeks {html.escape(str(m.get("weeks", "")))}'
                     f' — {html.escape(m.get("objective", ""))}</title></rect>')
        parts.append(f'<text x="{x + 4:.1f}" y="{bar_y - 8}" font-size="12" fill="var(--ink-2)">'
                     f'{html.escape(m["name"])}</text>')
        parts.append(f'<text x="{x + 4:.1f}" y="{bar_y + bar_h + 16}" font-size="11" fill="var(--muted)">'
                     f'wk {html.escape(str(m.get("weeks", "")))}</text>')
        x += w
    parts.append("</svg>")
    return "".join(parts)


def meso_weeks(m):
    """'1-4' -> 4, '5-8' -> 4, 3 -> 3."""
    w = m.get("weeks", 0)
    if isinstance(w, (int, float)):
        return max(1, int(w))
    nums = re.findall(r"\d+", str(w))
    if len(nums) >= 2:
        return max(1, int(nums[1]) - int(nums[0]) + 1)
    return max(1, int(nums[0])) if nums else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_json")
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--publish", default=None, metavar="DIR",
                    help="also copy training_plan.html/.md into DIR (a user-visible folder)")
    args = ap.parse_args()

    src = Path(args.plan_json).expanduser().resolve()
    try:
        p = json.loads(src.read_text())
    except Exception as e:
        sys.exit(f"ERROR: cannot parse {src}: {e}")
    missing = [k for k in REQUIRED if k not in p]
    if missing:
        sys.exit(f"ERROR: plan.json missing keys: {missing} (schema in SKILL.md)")

    outdir = Path(args.outdir) if args.outdir else \
        TENNIS_HOME / "players" / slugify(p["player"]) / "plans" / p["date"]
    outdir.mkdir(parents=True, exist_ok=True)
    if src != outdir / "plan.json":
        shutil.copy2(src, outdir / "plan.json")

    mesos = p["mesocycles"]
    for m in mesos:
        m["_weeks"] = meso_weeks(m)
    total_weeks = int(p["macrocycle"].get("weeks") or sum(m["_weeks"] for m in mesos))
    cons = p["constraints"]
    stage = p["current_stage"]

    # ---------- markdown ----------
    md = [f"# {p['player']} — Training Plan", "",
          f"*{p['date']} · built from {p.get('source_report', 'described level')} · "
          f"current NTRP {stage.get('ntrp', '?')} ({stage.get('band', '')})*", "",
          "## Goal & expectations", p["goal"], ""]
    if p["macrocycle"].get("expectation_note"):
        md += ["> " + p["macrocycle"]["expectation_note"], ""]
    md += [f"**Macrocycle:** {total_weeks} weeks — {p['macrocycle'].get('theme', '')} · "
           f"{cons.get('sessions_per_week', '?')} sessions/week × {cons.get('session_minutes', '?')} min", ""]
    for m in mesos:
        md += [f"## {m['name']} (weeks {m.get('weeks', '?')})", "",
               m.get("objective", ""), ""]
        if m.get("emphasis"):
            md += ["Emphasis: " + ", ".join(m["emphasis"]), ""]
        for day in m.get("weekly_template", []):
            md += [f"### {day.get('day', '?')} — {day.get('focus', '')} ({day.get('minutes', '?')} min)"]
            for blk in day.get("blocks", []):
                line = f"- **{blk['name']}** ({blk.get('minutes', '?')} min) — {blk.get('detail', '')}"
                if blk.get("metric"):
                    line += f" *Metric: {blk['metric']}*"
                md.append(line)
            md.append("")
        if m.get("exit_criteria"):
            md += ["**Exit criteria (advance only when met):**"]
            md += [f"- {c}" for c in m["exit_criteria"]]
            md.append("")
    md += ["## Progression rules"] + [f"- {r}" for r in p["progression_rules"]]
    ra = p["reassessment"]
    md += ["", "## Re-assessment",
           f"Week {ra.get('cadence_weeks', total_weeks)}: {ra.get('method', 'record a new video and re-run tennis-video-analysis')}"]
    md += ["", "## Constraints & safety"] + [f"- {c}" for c in p["caveats"]]
    (outdir / "training_plan.md").write_text("\n".join(md))

    # ---------- html ----------
    tpl = TEMPLATE.read_text()
    meso_cards = ""
    for m in mesos:
        rows = ""
        for day in m.get("weekly_template", []):
            blocks = "".join(
                f"<li><strong>{html.escape(blk['name'])}</strong> "
                f"<span class='num'>({blk.get('minutes', '?')} min)</span> — {html.escape(blk.get('detail', ''))}"
                + (f"<div class='metric'>metric: {html.escape(str(blk['metric']))}</div>" if blk.get("metric") else "")
                + "</li>"
                for blk in day.get("blocks", []))
            rows += (f"<tr><td class='num'><strong>{html.escape(str(day.get('day', '?')))}</strong></td>"
                     f"<td>{html.escape(day.get('focus', ''))}<br>"
                     f"<span class='metric'>{day.get('minutes', '?')} min</span></td>"
                     f"<td><ul>{blocks}</ul></td></tr>")
        emphasis = "".join(f"<span class='pill'>{html.escape(e)}</span>" for e in m.get("emphasis", []))
        exits = "".join(f"<li>{html.escape(c)}</li>" for c in m.get("exit_criteria", []))
        meso_cards += (
            f"<div class='card'><h2>{html.escape(m['name'])} "
            f"<span class='metric'>weeks {html.escape(str(m.get('weeks', '?')))}</span></h2>"
            + md_lite(m.get("objective", "")) + (f"<div>{emphasis}</div>" if emphasis else "")
            + (f"<table><thead><tr><th>Day</th><th>Focus</th><th>Session blocks</th></tr></thead>"
               f"<tbody>{rows}</tbody></table>" if rows else "")
            + (f"<div class='exit'><div class='t'>Exit criteria — advance only when met</div>"
               f"<ul>{exits}</ul></div>" if exits else "")
            + "</div>")

    subs = {
        "PLAYER": html.escape(p["player"]), "DATE": p["date"],
        "SOURCE": html.escape(str(p.get("source_report", "described level"))),
        "NTRP": html.escape(str(stage.get("ntrp", "?"))),
        "WEEKS": str(total_weeks), "THEME": html.escape(p["macrocycle"].get("theme", "")),
        "SPW": html.escape(str(cons.get("sessions_per_week", "?"))),
        "MINUTES": html.escape(str(cons.get("session_minutes", "?"))),
        "N_PHASES": str(len(mesos)),
        "REASSESS_WK": html.escape(str(ra.get("cadence_weeks", total_weeks))),
        "GOAL_HTML": md_lite(p["goal"]) +
                     (md_lite("*" + p["macrocycle"]["expectation_note"] + "*")
                      if p["macrocycle"].get("expectation_note") else ""),
        "TIMELINE_SVG": timeline_svg(mesos, total_weeks),
        "MESOCYCLE_CARDS": meso_cards,
        "RULES_HTML": "<ul>" + "".join(f"<li>{html.escape(r)}</li>" for r in p["progression_rules"]) + "</ul>",
        "REASSESS_HTML": md_lite(f"**Week {ra.get('cadence_weeks', total_weeks)}:** "
                                 f"{ra.get('method', 'record a new video and re-run tennis-video-analysis')}"),
        "CAVEATS_HTML": "<ul>" + "".join(f"<li>{html.escape(c)}</li>" for c in p["caveats"]) + "</ul>",
    }
    out_html = tpl
    for k, v in subs.items():
        out_html = out_html.replace("{{%s}}" % k, v or "")
    (outdir / "training_plan.html").write_text(out_html)

    published = None
    if args.publish:
        pub = Path(args.publish).expanduser()
        pub.mkdir(parents=True, exist_ok=True)
        for f in ("training_plan.html", "training_plan.md"):
            (pub / f).write_bytes((outdir / f).read_bytes())
        published = str(pub)

    print(json.dumps({"plan_md": str(outdir / "training_plan.md"),
                      "plan_html": str(outdir / "training_plan.html"),
                      "published_to": published,
                      "weeks": total_weeks, "phases": len(mesos)}, indent=2))


if __name__ == "__main__":
    main()
