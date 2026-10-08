#!/usr/bin/env python3
"""DAA Stress-Testing Lab.
  python lab.py list
  python lab.py run --all                 # every suite -> results/
  python lab.py run --suite search
  python lab.py run --algorithm fibonacci_heap
  python lab.py classify                  # print decision/optimization + NP table"""
import argparse, csv, json, os
from collections import defaultdict
from daalab.suites import SUITES, ALGO_TO_SUITE
from daalab.risk import classify_series
from daalab.complexity import CLASSIFICATION, THEORY
from daalab import plots

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def risk_table(rows):
    groups = defaultdict(list)
    for r in rows: groups[(r["suite"], r["algorithm"], r["family"])].append(r)
    table = []
    for (suite, alg, fam), rs in sorted(groups.items()):
        rs.sort(key=lambda r: r["n"])
        spikes = [r["extra"].get("spike_ratio") for r in rs if r["extra"].get("spike_ratio") is not None]
        res = classify_series([r["n"] for r in rs], [r["ops"] for r in rs], any(r["budget_hit"] for r in rs),
                              pseudo_poly=(alg == "knapsack_01_dp" and fam.startswith("capacity")),
                              spike_ratio=max(spikes) if spikes else None)
        table.append({"suite": suite, "algorithm": alg, "family": fam, "theory": THEORY.get(alg, ""),
                      "sizes": f"{rs[0]['n']}..{rs[-1]['n']}", "max_ops": rs[-1]["ops"], "max_time_s": max(r["time_s"] for r in rs), **res})
    return table


def run(suites, algo=None):
    rows, aux = [], {}
    for s in suites:
        print(f"[lab] running suite: {s}", flush=True)
        r, a = SUITES[s](); rows += r; aux.update(a)
    if algo: rows = [r for r in rows if r["algorithm"].startswith(algo)]
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "measurements.json"), "w") as f: json.dump(rows, f)
    with open(os.path.join(OUT, "aux_tables.json"), "w") as f: json.dump(aux, f, indent=1)
    with open(os.path.join(OUT, "measurements.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["suite", "algorithm", "family", "n", "ops", "time_s", "status", "extra"])
        for r in rows: w.writerow([r["suite"], r["algorithm"], r["family"], r["n"], r["ops"], r["time_s"], r["status"], json.dumps(r["extra"])])
    rt = risk_table(rows)
    with open(os.path.join(OUT, "risk_report.json"), "w") as f: json.dump(rt, f, indent=1)
    with open(os.path.join(OUT, "risk_report.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rt[0].keys())); w.writeheader(); w.writerows(rt)
    print(f"{'ALGORITHM':26}{'FAMILY':28}{'SIZES':10}{'RISK':10}REASON")
    for t in rt: print(f"{t['algorithm']:26}{t['family'][:27]:28}{t['sizes']:10}{t['risk']:10}{t['reason']}")
    if len(suites) == len(SUITES):
        plots.make_all(rows, aux, os.path.join(OUT, "plots")); plots.architecture(os.path.join(OUT, "plots", "architecture.png"))
        print("[lab] plots written to results/plots")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("list"); sub.add_parser("classify")
    r = sub.add_parser("run"); r.add_argument("--all", action="store_true"); r.add_argument("--suite", choices=SUITES); r.add_argument("--algorithm")
    a = ap.parse_args()
    if a.cmd == "list":
        print("suites:", ", ".join(SUITES)); print("algorithms:", ", ".join(sorted(ALGO_TO_SUITE)))
    elif a.cmd == "classify":
        for t in CLASSIFICATION: print(" | ".join(t))
    elif a.cmd == "run":
        if a.all: run(list(SUITES))
        elif a.suite: run([a.suite])
        elif a.algorithm: run([ALGO_TO_SUITE[a.algorithm]], a.algorithm)
        else: ap.error("give --all, --suite or --algorithm")
    else: ap.print_help()
