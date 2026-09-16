#!/usr/bin/env python3
"""dashboard.py: visual eval results dashboard.

    python3 dashboard.py          # reads .workshop/evals.json, opens browser
    python3 dashboard.py --out x  # write to a specific HTML file
"""
import argparse
import json
import os
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
EVALS_PATH = os.path.join(HERE, ".workshop", "evals.json")


def load() -> dict:
    if not os.path.exists(EVALS_PATH):
        raise SystemExit("No .workshop/evals.json found. Run python3 eval_harness.py first.")
    return json.load(open(EVALS_PATH))


def build_html(data: dict) -> str:
    report = data["report"]
    cases = data["cases"]

    # Status colours (status palette — never reused for series identity)
    COLOR = {"PASS": "#22c55e", "FAIL": "#ef4444", "UNKNOWN": "#f59e0b"}
    BG    = {"PASS": "#f0fdf4", "FAIL": "#fef2f2", "UNKNOWN": "#fffbeb"}
    DARK  = {"PASS": "#15803d", "FAIL": "#b91c1c", "UNKNOWN": "#b45309"}

    passed  = report["passed"]
    scored  = report["scored"]
    total   = report["cases"]
    release = report["release"]
    judge   = report["judge_model"]
    rubric  = report["rubric_version"]

    release_color = COLOR["PASS"] if release == "CLEAR" else COLOR["FAIL"]
    release_bg    = BG["PASS"]    if release == "CLEAR" else BG["FAIL"]

    # --- suite rows ---
    suite_rows = ""
    for suite, s in sorted(report["suites"].items()):
        total_s = s["passed"] + s["failed"] + s["unknown"]
        pct     = round(100 * s["passed"] / total_s) if total_s else 0
        gate    = "HARD GATE" if s["hard_gate"] else "soft"
        gate_color = "#ef4444" if s["hard_gate"] else "#94a3b8"
        bar_w   = pct
        suite_rows += f"""
        <tr>
          <td class="suite-name">{suite}</td>
          <td><span class="gate-badge" style="background:{gate_color}20;color:{gate_color};border:1px solid {gate_color}40">{gate}</span></td>
          <td>
            <div class="bar-track">
              <div class="bar-fill" style="width:{bar_w}%;background:{COLOR['PASS']}"></div>
            </div>
          </td>
          <td class="suite-stat">{s['passed']}/{total_s} passed</td>
        </tr>"""

    # --- case cards ---
    cards = ""
    for entry in cases:
        c   = entry["case"]
        res = entry["result"]
        st  = res.get("status", "FAIL")
        color = COLOR[st]
        bg    = BG[st]
        dark  = DARK[st]

        gate_html = '<span class="hard-badge">HARD GATE</span>' if c.get("hard_gate") else ""
        author_html = f'<span class="author">by {c.get("author","?")}</span>' if c.get("author") else ""

        # grader details
        grader_lines = ""
        for g in res.get("graders", []):
            v = g.get("verdict", "?")
            gc = COLOR.get(v, "#94a3b8")
            why = g.get("why", "")
            ev  = " · ".join((g.get("evidence") or [])[:1])
            ev  = ev[:120] + "…" if len(ev) > 120 else ev
            grader_lines += f"""
            <div class="grader-row">
              <span class="grader-dot" style="background:{gc}"></span>
              <span class="grader-type">{g.get('grader','?')}</span>
              <span class="grader-why">{why}</span>
            </div>"""
            if ev:
                grader_lines += f'<div class="grader-ev">"{ev}"</div>'

        cards += f"""
        <div class="card" style="border-left:4px solid {color};background:{bg}">
          <div class="card-header">
            <div class="card-left">
              <span class="status-pill" style="background:{color};color:#fff">{st}</span>
              <span class="case-id">{c['id']}</span>
              <span class="suite-tag">{c.get('suite','-')}</span>
              {gate_html}
            </div>
            <div class="card-right">{author_html}</div>
          </div>
          <div class="shape">{c.get('shape','')}</div>
          <div class="message">"{c.get('message','')}"</div>
          <div class="expect">{c.get('expect','')}</div>
          <div class="graders">{grader_lines}</div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Larkspur Evals Dashboard</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
       background:#f8fafc;color:#0f172a;padding:32px 24px;max-width:900px;margin:0 auto}}
  h1{{font-size:1.4rem;font-weight:700;margin-bottom:4px}}
  .meta{{font-size:.8rem;color:#64748b;margin-bottom:28px}}

  /* hero row */
  .hero{{display:flex;gap:16px;margin-bottom:28px;flex-wrap:wrap}}
  .tile{{background:#fff;border:1px solid #e2e8f0;border-radius:10px;
         padding:18px 22px;flex:1;min-width:140px}}
  .tile-val{{font-size:2rem;font-weight:800;line-height:1}}
  .tile-label{{font-size:.75rem;color:#64748b;margin-top:4px;text-transform:uppercase;letter-spacing:.05em}}

  /* release banner */
  .banner{{padding:12px 18px;border-radius:8px;font-weight:600;font-size:.95rem;
           margin-bottom:28px;background:{release_bg};color:{DARK['PASS'] if release=='CLEAR' else DARK['FAIL']};
           border:1px solid {COLOR['PASS'] if release=='CLEAR' else COLOR['FAIL']}40}}

  /* suite table */
  .section-title{{font-size:.8rem;font-weight:700;text-transform:uppercase;
                  letter-spacing:.07em;color:#64748b;margin-bottom:10px}}
  .suite-table{{width:100%;border-collapse:collapse;background:#fff;
                border:1px solid #e2e8f0;border-radius:10px;overflow:hidden;margin-bottom:28px}}
  .suite-table td{{padding:10px 14px;font-size:.875rem;border-bottom:1px solid #f1f5f9}}
  .suite-table tr:last-child td{{border-bottom:none}}
  .suite-name{{font-weight:600;color:#1e293b}}
  .suite-stat{{color:#64748b;white-space:nowrap;text-align:right}}
  .gate-badge{{font-size:.7rem;font-weight:700;padding:2px 7px;border-radius:4px;
               text-transform:uppercase;letter-spacing:.05em;white-space:nowrap}}
  .bar-track{{height:8px;background:#f1f5f9;border-radius:4px;overflow:hidden;min-width:80px}}
  .bar-fill{{height:100%;border-radius:4px;transition:width .4s ease}}

  /* cards */
  .card{{background:#fff;border-left:4px solid #22c55e;border-radius:8px;
         padding:16px 18px;margin-bottom:14px;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
  .card-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:6px}}
  .card-left{{display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
  .status-pill{{font-size:.7rem;font-weight:800;padding:3px 9px;border-radius:20px;letter-spacing:.06em}}
  .case-id{{font-weight:700;font-size:.9rem}}
  .suite-tag{{font-size:.75rem;color:#64748b;background:#f1f5f9;padding:2px 8px;border-radius:4px}}
  .hard-badge{{font-size:.68rem;font-weight:700;background:#fef2f2;color:#b91c1c;
               border:1px solid #fecaca;padding:2px 7px;border-radius:4px;text-transform:uppercase}}
  .author{{font-size:.75rem;color:#94a3b8}}
  .shape{{font-size:.9rem;font-weight:600;color:#1e293b;margin-bottom:5px}}
  .message{{font-size:.82rem;color:#475569;font-style:italic;margin-bottom:5px;
            padding:6px 10px;background:#f8fafc;border-radius:4px;border-left:2px solid #cbd5e1}}
  .expect{{font-size:.78rem;color:#64748b;margin-bottom:10px}}
  .graders{{display:flex;flex-direction:column;gap:4px}}
  .grader-row{{display:flex;align-items:center;gap:7px;font-size:.78rem}}
  .grader-dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0}}
  .grader-type{{font-weight:600;color:#475569;width:42px;flex-shrink:0}}
  .grader-why{{color:#64748b}}
  .grader-ev{{font-size:.74rem;color:#94a3b8;margin-left:57px;font-style:italic;
              overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
</style>
</head>
<body>
<h1>Larkspur Evals Dashboard</h1>
<div class="meta">rubric {rubric} &nbsp;·&nbsp; judge {judge}</div>

<div class="banner">{'✓ RELEASE CLEAR — no hard gate failed' if release=='CLEAR' else '✗ RELEASE BLOCKED — hard gate failure'}</div>

<div class="hero">
  <div class="tile">
    <div class="tile-val">{passed}/{scored}</div>
    <div class="tile-label">Cases passed</div>
  </div>
  <div class="tile">
    <div class="tile-val">{round(100*passed/scored) if scored else 0}%</div>
    <div class="tile-label">Pass rate</div>
  </div>
  <div class="tile">
    <div class="tile-val">{total - scored}</div>
    <div class="tile-label">Unscored (UNKNOWN)</div>
  </div>
  <div class="tile">
    <div class="tile-val">{len(report['blocking_suites']) or '—'}</div>
    <div class="tile-label">Blocking suites</div>
  </div>
</div>

<div class="section-title">Suites</div>
<table class="suite-table">
  <tbody>{suite_rows}</tbody>
</table>

<div class="section-title">Cases ({total} ran)</div>
{cards}

</body>
</html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, ".workshop", "dashboard.html"))
    args = ap.parse_args()

    data = load()
    html = build_html(data)
    with open(args.out, "w") as f:
        f.write(html)
    print("Dashboard written to", os.path.relpath(args.out, HERE))
    webbrowser.open("file://" + os.path.abspath(args.out))


if __name__ == "__main__":
    main()
