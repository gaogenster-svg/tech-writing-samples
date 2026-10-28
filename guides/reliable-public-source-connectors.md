# Designing a connector that can say “no usable data”

A connector is useful only if downstream users can distinguish a real record from a guess. YachtPass aggregates public job opportunities, but a source page can contain navigation text, structured metadata, an incomplete vacancy, and an application control that does not have a reusable link. Treating every page as a valid job creates misleading results.

This guide adapts design decisions documented in YachtPass. The accompanying [offline parser](../samples/public-source-parser/README.md) is a new Python teaching example, not an extraction of the production connector. It processes a synthetic HTML file without contacting any agency.

## Keep retrieval and interpretation separate

A production retrieval layer should decide which sources may be fetched, enforce timeouts and response-size limits, respect access restrictions, and handle redirects under the same outbound policy as the initial request. Public availability alone is not a blanket authorization to collect or redistribute content.

The teaching sample deliberately stops before that layer: it accepts a string and a source URL. This makes parsing reproducible without mixing network availability, authentication, or changing third-party content into the exercise. Its URL check rejects relative URLs, non-HTTP(S) schemes, and embedded credentials; it does not establish that a host is trusted or safe to fetch.

## Extract facts with an explicit acceptance rule

The sample reads `application/ld+json` script blocks and looks for `JobPosting` objects. It supports a top-level object, an array, and objects inside `@graph`. This is limited structural traversal, not a general JSON-LD processor: it does not resolve remote contexts, expand vocabulary prefixes, or follow `@id` references.

Each accepted record must have a nonempty string title, description, and absolute HTTP(S) vacancy URL. These are this sample's requirements, not a claim that every publishing platform must provide them. A missing field produces a diagnostic and no accepted record. It does not become an invented title, synthetic description, or guessed application link.

The synthetic fixture contains one complete vacancy and one without a vacancy URL. Running it accepts the complete item and records `missing_or_invalid_required_field` for the incomplete one.

## Preserve provenance independently of presentation

The output keeps the page supplied as `source_url`, the vacancy's published `url`, the external identifier when supplied, the declared hiring-organization name, and a SHA-256 hash of the description string. The organization name is a source claim, not independently verified ownership. The hash fingerprints that exact string, not the whole record and not a semantically normalized description.

Identity and change detection answer different questions. Within one parse call, the sample deduplicates by source URL and external identifier, falling back to vacancy URL. It keeps the first occurrence and records a duplicate diagnostic. Production reconciliation needs a stronger policy: a changed duplicate should not be silently assumed equivalent, and source-wide identity needs stable source configuration rather than a changing pagination URL.

## A vacancy link is not necessarily an application link

The sample intentionally has no `apply_url` field. A job's canonical URL can identify the vacancy without providing a supported application deep link.

One documented YachtPass source displayed public role briefs while its Apply control opened a JavaScript form fragment. The connector preserved the source board and did not manufacture a direct application action. That distinction belongs in both the data contract and the user-facing explanation. A precise limitation is more useful than a button that promises a workflow the integration cannot complete.

## Make missing data observable

The parser returns records and diagnostics separately. Invalid JSON, absent metadata, rejected required fields, duplicates, and zero accepted jobs are visible outcomes. A fetch failure would belong to the retrieval layer; it should not be relabeled as an empty source.

Likewise, one empty parse should not by itself establish that every previously seen vacancy has closed. Production synchronization needs explicit reconciliation and retry rules; those are outside this offline sample.

## Verify boundaries, not only the happy path

The sample's nine unit tests cover provenance, arrays and graphs, invalid JSON, missing URLs, irrelevant metadata, duplicate identity, unacceptable URL shapes, wrong field types, and multiple script blocks. They establish the behavior of this small example, not coverage of live job boards.

Raw descriptions remain raw source text. Render them as escaped text or pass them through a separately reviewed sanitization path. The parser does not prove content safety, legal permission, freshness, or source authenticity.

## Run the example

From the repository root:

```bash
python3 samples/public-source-parser/parser.py
python3 -m unittest discover -s samples/public-source-parser -v
```

The example uses only Python's standard library. No production hosts, accounts, admin routes, or user documents are required.

## References

- [Schema.org JobPosting](https://schema.org/JobPosting): the source vocabulary; the sample implements only the subset described above.
- [Python HTMLParser](https://docs.python.org/3/library/html.parser.html): the script-block extraction mechanism.
