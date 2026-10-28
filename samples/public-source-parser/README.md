# Offline public-source parser

A new AI-assisted teaching example based on the connector design discussed in the [guide](../../guides/reliable-public-source-connectors.md). This is not YachtPass's production connector or a general-purpose JSON-LD implementation.

Requires Python 3.10+, standard library only. From the repository root:

```bash
python3 samples/public-source-parser/parser.py
python3 -m unittest discover -s samples/public-source-parser -v
```

`fixtures/jobs.html` is authored synthetic data. Every vacancy URL uses `example.test`. The CLI loads that local file and makes no HTTP requests. The expected output contains one accepted job and a `missing_or_invalid_required_field` diagnostic for the incomplete listing.

The program preserves raw descriptions, so its output must not be inserted as HTML without a separate sanitization decision. URL syntax checks are not SSRF protection or an allow-list. No production configuration, customer information, or proprietary source-board fixtures are included.

The tests and demo were run during portfolio preparation. The guide distinguishes implemented sample behavior from recommendations for production retrieval and reconciliation.
