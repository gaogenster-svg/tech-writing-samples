"""Offline teaching example. Parses synthetic HTML; never fetches a URL."""
import hashlib
import json
from html.parser import HTMLParser
from urllib.parse import urlsplit


class JsonLdBlocks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.parts = []
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.active = dict(attrs).get('type', '').lower() == 'application/ld+json'
            self.parts = []

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self.active:
            self.blocks.append(''.join(self.parts))
            self.active = False


def nodes(value):
    if isinstance(value, list):
        for item in value:
            yield from nodes(item)
    elif isinstance(value, dict):
        yield value
        yield from nodes(value.get('@graph', []))


def string(value):
    return value.strip() if isinstance(value, str) else ''


def web_url(value):
    value = string(value)
    try:
        parsed = urlsplit(value)
        if parsed.scheme in ('http', 'https') and parsed.hostname and not parsed.username and not parsed.password:
            return value
    except ValueError:
        pass
    return ''


def parse_jobs(page, source_url):
    """Return accepted records plus explicit diagnostics, not silent fallback jobs."""
    if not web_url(source_url):
        raise ValueError('source_url must be an absolute HTTP(S) URL without embedded credentials')
    parser = JsonLdBlocks()
    parser.feed(page)
    parser.close()
    records, diagnostics, seen = [], [], set()
    if not parser.blocks:
        diagnostics.append('no_jsonld')
    for block in parser.blocks:
        try:
            document = json.loads(block)
        except json.JSONDecodeError:
            diagnostics.append('invalid_json')
            continue
        for job in nodes(document):
            types = job.get('@type', [])
            types = [types] if isinstance(types, str) else types
            if not isinstance(types, list) or 'JobPosting' not in types:
                continue
            title, description, url = string(job.get('title')), string(job.get('description')), web_url(job.get('url'))
            if not title or not description or not url:
                diagnostics.append('missing_or_invalid_required_field')
                continue
            identifier = job.get('identifier')
            external_id = string(identifier.get('value')) if isinstance(identifier, dict) else string(identifier)
            identity = (source_url, external_id or url)
            if identity in seen:
                diagnostics.append('duplicate_record')
                continue
            seen.add(identity)
            organization = job.get('hiringOrganization')
            records.append({'title': title, 'description': description, 'url': url,
                            'source_url': source_url, 'external_id': external_id or None,
                            'source_owner': string(organization.get('name')) if isinstance(organization, dict) else None,
                            'content_sha256': hashlib.sha256(description.encode('utf-8')).hexdigest()})
    if not records:
        diagnostics.append('no_accepted_jobs')
    return {'records': records, 'diagnostics': diagnostics}


if __name__ == '__main__':
    from pathlib import Path
    page = (Path(__file__).parent / 'fixtures' / 'jobs.html').read_text(encoding='utf-8')
    print(json.dumps(parse_jobs(page, 'https://example.test/careers'), indent=2))
