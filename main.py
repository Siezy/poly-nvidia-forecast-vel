# polymarket-nvidia-ceo-forecast-01 — Vel entry
# Quantile forecaster for Polymarket Yes prices: per-market empirical volatility
# (minute-diff RMS over a 120-minute window, floored, scaled) on a random-walk
# sqrt-horizon spread. Offline, stdlib only, deterministic.
import json, math, os

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
HORIZON = 240
TAUS = [0.05, 0.25, 0.5, 0.75, 0.95]
Z = [(-1.644854, 0.05), (-0.67449, 0.25), (0.0, 0.5), (0.67449, 0.75), (1.644854, 0.95)]
SPREAD_SCALE = 0.4
VOL_SCALE = 0.45
VOL_WINDOW = 120
VOL_FLOOR = 0.001

def quantile_rows(prices, horizon):
    diffs = [prices[i + 1] - prices[i] for i in range(max(0, len(prices) - VOL_WINDOW), len(prices) - 1)]
    sd = math.sqrt(sum(d * d for d in diffs) / max(1, len(diffs)))
    vol = max(VOL_FLOOR, 0.0025 + VOL_SCALE * sd) * SPREAD_SCALE
    x = prices[-1]
    rows = []
    for h in range(1, horizon + 1):
        spread = vol * math.sqrt(h)
        rows.append([min(1.0, max(0.0, x + z * spread)) for z, _ in Z])
    return rows

def main():
    for name in sorted(os.listdir(INPUT_DIR)):
        if not name.endswith(".in"):
            continue
        case = json.load(open(os.path.join(INPUT_DIR, name)))
        out = {"forecasts": []}
        for m in case["markets"]:
            out["forecasts"].append({"id": m["id"], "q": quantile_rows(m["prices"], case["horizon_minutes"])})
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(os.path.join(OUTPUT_DIR, name[:-3] + ".out"), "w") as f:
            json.dump(out, f)

main()
