"""Deterministic fixture evaluation. No network, credentials, or dependencies."""
import argparse
import csv
import hashlib
import json
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'samples' / 'description-normalizer'))
from normalizer import normalize_summary, strip_tags_baseline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=HERE / 'results')
    args = parser.parse_args()
    data = (HERE / 'fixtures.json').read_bytes()
    fixtures = json.loads(data)
    assert len({f['id'] for f in fixtures}) == len(fixtures)
    implementations = {'tag_stripping': strip_tags_baseline, 'adapted_normalizer': normalize_summary}
    rows = []
    for fixture in fixtures:
        for name, function in implementations.items():
            actual = function(fixture['input'])
            rows.append({'case': fixture['id'], 'method': name, 'expected': fixture['expected'], 'actual': actual, 'passed': actual == fixture['expected']})
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / 'cases.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    summary = {'fixture_count': len(fixtures), 'fixture_sha256': hashlib.sha256(data).hexdigest(),
               'python': platform.python_version(), 'implementation': platform.python_implementation(),
               'metric': 'Exact summary-string equality against authored synthetic expectations',
               'methods': {name: {'passed': sum(row['passed'] for row in rows if row['method'] == name),
                                  'failed': [row['case'] for row in rows if row['method'] == name and not row['passed']]}
                           for name in implementations}}
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
