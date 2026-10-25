# Diagnostic benchmark

Run `python benchmarks/run_benchmark.py` from the repository root.

The runner reports exact-set match rate and per-label precision/recall against labelled synthetic logs. Labels indicate expected categories, not proven root causes.

## Limitations

- The initial cases are synthetic and small.
- They do not cover all ROS distributions, middleware, launch setups, hardware or Gazebo versions.
- Scores are regression signals and are not real-world accuracy estimates.
- Add reviewed, permissioned, privacy-scrubbed cases before making broader performance claims.
- Keep a held-out set when tuning rules.

## Adding cases

Append one JSON object per line with a stable `id`, raw `input`, expected diagnostic ID array, and provenance note. Review false positives and misses. Use `unknown` only when no current known category applies.
