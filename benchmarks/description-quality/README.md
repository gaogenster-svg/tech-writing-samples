# Description cleanup: a reproducible fixture comparison

**Scope:** exact-output quality on 14 synthetic cases, not a production accuracy or performance benchmark. Executed on 2026-10-28 using CPython 3.12.14. No network requests, external packages, API keys, customer data, or credentials are required.

## Reproduce

From the repository root with Python 3.10+:

```bash
python3 benchmarks/description-quality/run.py
```

The script writes `results/cases.csv` and `results/summary.json` beside this file. To compare a fresh run without overwriting the checked-in evidence:

```bash
python3 benchmarks/description-quality/run.py --output /tmp/description-quality
```

On Windows, use `python` if `python3` is unavailable and choose a local output directory. Timing is not measured. Results are deterministic for the same code, fixtures, and relevant runtime behavior. Runtime metadata can differ on another interpreter.

## Method

`fixtures.json` contains the input, an authored expected summary, and the purpose of each case. Both implementations receive the same input. The baseline removes tag-shaped spans, decodes HTML entities, and collapses whitespace. The adapted normalizer adds the ordered cleanup and summary rules described in the [article](../../investigations/cleaning-job-descriptions.md).

A pass means Python string equality between actual and expected output. There is no fuzzy matching or manual post-processing. The denominator is the number of unique fixture IDs; the numerator is the number of `True` rows for each method in the CSV. The script records a SHA-256 hash of the exact fixture file bytes.

## Observed results

| Method | Matches | Mismatches |
| --- | ---: | ---: |
| `tag_stripping` | 6 / 14 | 8 |
| `adapted_normalizer` | 10 / 14 | 4 |

The adapted method fails `markdown-image`, `meaningful-cookie`, `identifier`, and `literal-comparison`. The baseline preserves two of those inputs that the adaptation damages. See [raw cases](results/cases.csv) and [machine-readable summary](results/summary.json).

## Limits and remeasurement

The cases were authored alongside this sample, informed by the source rules and tests. They are small, selected, synthetic, and not held out. The expectations represent editorial choices. These counts must not be advertised as general accuracy, superiority over production parsers, or performance of the original C# application.

No repeated-run uncertainty interval is relevant to this deterministic count; repeating it cannot make the dataset representative. Expand the fixture set and add independent labels before drawing broader conclusions. When modifying a rule, keep existing fixtures, explain new expectations, rerun the evaluator, and publish both improvements and regressions. There is currently one recorded evaluation, not a longitudinal study.
