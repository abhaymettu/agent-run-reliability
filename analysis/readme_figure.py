"""Draw the README figure from results/analysis.json.

Left: where the pass/fail variance goes. Right: how often two independent
evaluations of the same two models disagree on the winner, by runs per task.
Standard library only, like the rest of the repo.

    python3 analysis/readme_figure.py --analysis results/analysis.json --out docs/readme-figure.svg
"""
import argparse
import json

W, H = 880, 360
INK, MUTED, GRID, BG = "#1f2328", "#59636e", "#d0d7de", "#ffffff"
BLUE, ORANGE = "#0072B2", "#E69F00"  # Okabe-Ito, distinct in lightness as well as hue


def text(x, y, s, size=13, anchor="start", fill=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
            f'fill="{fill}" font-weight="{weight}">{s}</text>')


def variance_panel(vc, x0, y0, w):
    parts = [("Run to run", vc["residual"], BLUE),
             ("Task", vc["task"], MUTED),
             ("Model x task", vc["task_x_model"], GRID),
             ("Model", vc["model"], ORANGE)]
    total = sum(v for _, v, _ in parts)
    out = [text(x0, y0, "Where the variance in pass/fail goes", 15, weight="600")]
    label_w, bar_w = 120, w - 190
    for i, (name, v, color) in enumerate(parts):
        y = y0 + 34 + i * 52
        share = v / total
        out.append(text(x0, y + 19, name, 13))
        out.append(f'<rect x="{x0 + label_w}" y="{y}" width="{bar_w * share:.1f}" height="26" rx="3" fill="{color}"/>')
        out.append(text(x0 + label_w + bar_w * share + 8, y + 19, f"{share * 100:.1f}%", 13, weight="600"))
    out.append(text(x0, y0 + 262, f"Run-to-run noise is {vc['residual'] / vc['model']:.1f} times the between-model signal.", 12, fill=MUTED))
    return out


def disagreement_panel(per_k, x0, y0, w, h):
    ks = sorted(int(k) for k in per_k)
    ymax = 0.30
    px = lambda k: x0 + 40 + (k - ks[0]) / (ks[-1] - ks[0]) * (w - 60)
    py = lambda p: y0 + 30 + (1 - p / ymax) * (h - 70)
    out = [text(x0, y0, "Two evaluations disagree on the winner", 15, weight="600")]
    for p in (0, 0.1, 0.2, 0.3):
        out.append(f'<line x1="{x0 + 40}" x2="{x0 + w - 20}" y1="{py(p):.1f}" y2="{py(p):.1f}" stroke="{GRID}"/>')
        out.append(text(x0 + 32, py(p) + 4, f"{p * 100:.0f}%", 11, "end", MUTED))
    out.append(f'<line x1="{x0 + 40}" x2="{x0 + w - 20}" y1="{py(0.05):.1f}" y2="{py(0.05):.1f}" stroke="{MUTED}" stroke-dasharray="4 4"/>')
    out.append(text(x0 + w - 20, py(0.05) - 6, "5%", 11, "end", MUTED))
    lo = [(px(k), py(per_k[str(k)]["ci_95_bootstrap"]["lo"])) for k in ks]
    hi = [(px(k), py(per_k[str(k)]["ci_95_bootstrap"]["hi"])) for k in ks]
    band = " ".join(f"{x:.1f},{y:.1f}" for x, y in hi + lo[::-1])
    out.append(f'<polygon points="{band}" fill="{BLUE}" fill-opacity="0.18"/>')
    pts = [(k, px(k), py(per_k[str(k)]["disagreement_rate"])) for k in ks]
    out.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for _, x, y in pts)}" fill="none" stroke="{BLUE}" stroke-width="2.5"/>')
    for k, x, y in pts:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{BLUE}"/>')
        out.append(text(x, y0 + h - 22, str(k), 11, "middle", MUTED))
        if k in (1, 2, 3, 4):
            label = text(x + 8, y - 8, f"{per_k[str(k)]['disagreement_rate'] * 100:.1f}%", 12, weight="600")
            out.append(label.replace("<text ", f'<text stroke="{BG}" stroke-width="4" paint-order="stroke" ', 1))
    out.append(text(x0 + 40 + (w - 60) / 2, y0 + h - 4, "Runs per task per model (band: 95% bootstrap CI)", 12, "middle", MUTED))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", default="results/analysis.json")
    ap.add_argument("--out", default="docs/readme-figure.svg")
    args = ap.parse_args()
    d = json.load(open(args.analysis))
    vc = d["anova"]["variance_components_truncated_at_zero"]
    per_k = d["disagreement_probability"]["pairs"]["haiku_vs_sonnet"]["per_k"]
    body = variance_panel(vc, 28, 40, 400) + disagreement_panel(per_k, 460, 40, 400, 300)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif">'
           f'<rect width="{W}" height="{H}" rx="8" fill="{BG}"/>' + "".join(body) + "</svg>\n")
    open(args.out, "w").write(svg)


if __name__ == "__main__":
    main()
