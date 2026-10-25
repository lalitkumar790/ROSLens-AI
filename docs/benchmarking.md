# Diagnostic benchmark

Run `python benchmarks/run_benchmark.py` from the repository root.

The runner reports exact-set match rate and per-label precision/recall against labelled synthetic logs. A label is the expected diagnostic category, not proof of the true root cause.

## Limitations

- This initial set is synthetic and small.
- It does not cover all ROS distributions, middleware, launch configurations, hardware or simulator versions.
- Its score is a regression signal only and must not be marketed as real-world accuracy.
- Add reviewed, permissioned and privacy-scrubbed examples before reporting broader performance.
- Keep a held-out set when tuning the rules.

## Adding cases

Append one JSON object per line with a stable `id`, raw `input`, expected diagnostic ID array, and a short provenance note. Review false positives as well as missed matches. Use `unknown` only if the known categories genuinely do not apply.
