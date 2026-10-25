"""Evaluate deterministic diagnosis rules against labelled synthetic cases."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.diagnostics import diagnose_log  # noqa: E402


def main() -> int:
    cases_path = Path(__file__).with_name("cases.jsonl")
    cases = [
        json.loads(line)
        for line in cases_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    tp, fp, fn = defaultdict(int), defaultdict(int), defaultdict(int)
    exact = 0
    for case in cases:
        actual = {item["id"] for item in diagnose_log(case["input"])["diagnostics"]}
        expected = set(case["expected"])
        exact += actual == expected
        for label in actual & expected:
            tp[label] += 1
        for label in actual - expected:
            fp[label] += 1
        for label in expected - actual:
            fn[label] += 1
        if actual != expected:
            print(f"FAIL {case['id']}: expected={sorted(expected)} actual={sorted(actual)}")

    print(f"Cases: {len(cases)}")
    print(f"Exact set match: {exact}/{len(cases)} ({100 * exact / len(cases) if cases else 0:.1f}%)")
    print("\nPer-label metrics\nlabel                    precision  recall")
    for label in sorted(set(tp) | set(fp) | set(fn)):
        precision = tp[label] / (tp[label] + fp[label]) if tp[label] + fp[label] else 0.0
        recall = tp[label] / (tp[label] + fn[label]) if tp[label] + fn[label] else 0.0
        print(f"{label:24s} {precision:9.3f} {recall:7.3f}")
    print("\nNOTE: synthetic regression metrics are not estimates of real-world performance.")
    return 0 if exact == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
