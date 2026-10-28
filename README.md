# Technical writing samples

Technical investigations and developer guidance from Mykola Naugolnyi's YachtPass project, with runnable portfolio examples and explicit limits on what the evidence establishes.

## Samples

| Sample | Focus | Supporting material |
| --- | --- | --- |
| [Cleaning job descriptions without hiding data loss](investigations/cleaning-job-descriptions.md) | Ordered transformations, summary design, and regressions | [Python adaptation](samples/description-normalizer/README.md), [14-case evaluation and raw results](benchmarks/description-quality/README.md) |
| [Designing a connector that can say “no usable data”](guides/reliable-public-source-connectors.md) | Source provenance, acceptance rules, failure handling, and honest application links | [Offline parser, synthetic HTML, and tests](samples/public-source-parser/README.md) |
| [Cloudflare R2 upload compatibility](investigations/cloudflare-r2-upload-compatibility.md) | SDK transfer/signing behavior and a compatibility investigation | Investigation note; no standalone reproduction or benchmark |

## Reproduce the quality comparison

With Python 3.10+ installed, clone this repository, open its root directory, and run:

```bash
python3 benchmarks/description-quality/run.py
```

The script evaluates both methods against the same authored expectations and writes every output plus aggregate counts. On the recorded 14-case set, the adapted normalizer matches 10 expectations and simple tag stripping matches 6; four normalizer failures remain published. These are selected synthetic cases, not a production accuracy estimate or an API performance comparison.

## Verification

```bash
python3 -m unittest discover -s samples/description-normalizer -v
python3 -m unittest discover -s samples/public-source-parser -v
python3 samples/public-source-parser/parser.py
```

No third-party packages, credentials, or network calls are required. On Windows, use `python` if `python3` is unavailable.

## Provenance and AI use

The production YachtPass repository remains private. This repository contains selected explanations, a Python adaptation of its C# text-cleanup path, and a newly created offline connector example. The Python sample was executed; the production C# code was not executed during this evaluation.

The new articles, Python examples, fixtures, and tests were prepared with AI assistance for this portfolio. The fixture counts come from executing the included code. This work should not be represented as a historical production benchmark, an independently authored research study, or a longitudinal comparison. These are newly prepared portfolio adaptations, not untouched historical publications.
