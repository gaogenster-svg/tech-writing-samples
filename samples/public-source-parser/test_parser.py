import json
import unittest
from parser import parse_jobs

SOURCE = 'https://example.test/careers'
JOB = {'@type': 'JobPosting', 'title': 'Deckhand', 'description': 'Maintain deck equipment.', 'url': 'https://example.test/jobs/1'}


def page(value):
    return '<script type="application/ld+json">' + json.dumps(value) + '</script>'


class ParserTests(unittest.TestCase):
    def test_preserves_provenance_and_hash(self):
        item = parse_jobs(page(JOB), SOURCE)['records'][0]
        self.assertEqual(item['source_url'], SOURCE)
        self.assertEqual(item['url'], JOB['url'])
        self.assertEqual(len(item['content_sha256']), 64)
        self.assertIsNone(item['external_id'])

    def test_array_and_graph(self):
        for document in ([JOB], {'@graph': [JOB]}):
            self.assertEqual(len(parse_jobs(page(document), SOURCE)['records']), 1)

    def test_invalid_json_diagnostic(self):
        result = parse_jobs('<script type="application/ld+json">{</script>', SOURCE)
        self.assertEqual(result['records'], [])
        self.assertIn('invalid_json', result['diagnostics'])

    def test_missing_url_is_not_invented(self):
        job = {k: v for k, v in JOB.items() if k != 'url'}
        self.assertEqual(parse_jobs(page(job), SOURCE)['records'], [])

    def test_wrong_type_and_no_script(self):
        self.assertEqual(parse_jobs(page({'@type': 'Organization'}), SOURCE)['records'], [])
        self.assertIn('no_jsonld', parse_jobs('<p>No metadata</p>', SOURCE)['diagnostics'])

    def test_duplicate_identity(self):
        result = parse_jobs(page([JOB, JOB]), SOURCE)
        self.assertEqual(len(result['records']), 1)
        self.assertIn('duplicate_record', result['diagnostics'])

    def test_unsafe_and_relative_urls(self):
        for value in ('javascript:alert(1)', '/jobs/1', 'https://user:password@example.test/jobs/1'):
            self.assertEqual(parse_jobs(page({**JOB, 'url': value}), SOURCE)['records'], [])

    def test_wrong_field_types(self):
        for field in ('title', 'description', 'url'):
            self.assertEqual(parse_jobs(page({**JOB, field: []}), SOURCE)['records'], [])

    def test_multiple_blocks(self):
        result = parse_jobs('<script>ignore()</script>' + page(JOB) + page({**JOB, 'url': 'https://example.test/jobs/2'}), SOURCE)
        self.assertEqual(len(result['records']), 2)


if __name__ == '__main__':
    unittest.main()
