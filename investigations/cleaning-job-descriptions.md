# Cleaning job descriptions without hiding data loss

A job aggregator receives text that was written for different publishing systems. One source embeds HTML, another mixes Markdown with field labels, and a third includes a fragment of page JavaScript. Removing angle-bracket tags gets rid of some formatting, but it does not decide which text belongs in the job description.

This investigation examines a plain-text cleanup strategy used in YachtPass. The accompanying Python implementation is an AI-assisted adaptation of the production C# logic, created for this portfolio. It is not the production implementation, a complete HTML parser, or an HTML sanitizer. All examples and evaluation inputs are synthetic.

## Decide which output you are producing

The original application distinguishes a full description from its shorter summary. That matters for metadata: a full record can legitimately retain `Position: Deckhand`, while repeating the same label in a card summary adds little value when the card already has a title.

For this sample, the comparison evaluates summary strings. The normalizer first produces cleaned multiline content, then removes leading metadata lines and joins the remaining text. It removes those lines only while there is another line to retain. A single metadata-only line can therefore survive; this is a heuristic, not proof that a record contains a useful description.

Consider this input:

```text
**Position:** Deckhand
**Location:** Spain
Experienced deckhand required.
```

The expected summary is:

```text
Experienced deckhand required.
```

The full cleaned text retains the position and location. A reusable text-cleaning function should not silently equate those two outputs.

## Order changes the result

The sample removes paired script and style-like elements before stripping ordinary tags. Simply stripping the tags from `<script>alert('x')</script>` retains the script body as visible text.

Block elements become line breaks before tag removal, so adjacent paragraphs remain separated. Entity decoding comes next, followed by another removal pass. That second pass handles the synthetic case where script tags arrive encoded as `&lt;script&gt;`.

Markdown cleanup then retains link text and removes formatting markers. Finally, the implementation normalizes whitespace and filters lines that resemble page debris. Separate lines containing a JavaScript variable declaration or `document.querySelector` are examples of this debris.

This ordering solves some practical inputs, but each transformation can destroy information. Decoding entities and removing tags can also mistake literal comparison symbols for markup.

## A small comparison with published failures

The [evaluation package](../benchmarks/description-quality/README.md) includes 14 authored cases, two implementations, and every resulting string. A case passes only when the complete output exactly matches its expected summary.

| Method | Exact matches | Mismatches |
| --- | ---: | ---: |
| Simple tag stripping and entity decoding | 6 / 14 | 8 |
| Adapted normalizer | 10 / 14 | 4 |

These are observed results from the included Python sample on this fixture set, not an estimate of production accuracy. The fixtures were selected to exercise known transformations and counterexamples; they are not a random or held-out sample of real vacancy pages. The baseline is intentionally minimal and is not a substitute for comparing mature HTML or Markdown parsers.

The richer normalizer improves handling of leading metadata, scripts, Markdown links, paragraph boundaries, and separate JavaScript lines. The four mismatches are more useful than an unexplained success percentage:

| Case | What went wrong | Implication |
| --- | --- | --- |
| Markdown image | Link cleanup runs first and leaves `!` before the alt text. | Ordering creates an interaction between otherwise reasonable rules. |
| Meaningful cookie phrase | A sentence about a chef's “cookie policy” is treated as navigation debris. | A phrase match can discard an entire legitimate sentence. |
| Identifier | `engine_room` becomes `engineroom`. | Formatting cleanup changes an identifier's meaning. |
| Literal comparisons | Text between `<` and `>` is removed. | A tag regex cannot distinguish arbitrary text from markup reliably. |

The minimal baseline preserves the cookie phrase and identifier. Adding rules improved the aggregate fixture count while introducing losses that the simpler method did not have. That is why the per-case outputs belong beside the aggregate.

## What should change next?

The immediate candidates are narrower Markdown handling and a debris filter that uses source structure instead of deleting an entire line after a phrase match. Those are proposals, not improvements measured here. Changing rules requires keeping the counterexamples and adding new inputs; silently editing expected outputs to match the implementation would invalidate the comparison.

For a larger evaluation, label examples independently, keep development and evaluation sets separate, and report preservation of critical fields as well as formatting quality. Summaries that look clean but lose a salary, qualification, or identifier can be worse than untidy text.

## Reproduce the result

With Python 3.10 or newer, clone this portfolio and run `python3 benchmarks/description-quality/run.py` from the repository root. Read the method counts in `results/summary.json` and inspect `results/cases.csv` to recover the numerator and every mismatch.

See [sample scope and provenance](../samples/description-normalizer/README.md) for the adaptation boundaries. This evaluation makes no latency, search-ranking, or production-security claim.
