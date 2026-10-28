"""Python adaptation of YachtPass's plain-text cleanup path; not an HTML sanitizer."""
import html
import re

UNSAFE = re.compile(r'<(?:script|style|iframe|object|embed|form|svg|noscript)\b[^>]*>.*?</(?:script|style|iframe|object|embed|form|svg|noscript)>', re.I | re.S)
BLOCK = re.compile(r'</?(?:p|div|br|li|ul|ol|h[1-6]|section|article|tr|table|blockquote)\b[^>]*>', re.I)
TAG = re.compile(r'<[^>]+>', re.S)
DEBRIS = re.compile(r'''(?:^|\s)(?:document\.|window\.|jQuery\b|\$\s*\(|function\s*\(|(?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=|login\s*\(\s*['"]?#|cookie\s+(?:settings|policy|consent)|sign\s*up\s*(?:for|to)\s+(?:our|the)\s+(?:newsletter|updates))''', re.I)
METADATA = re.compile(r'^(?:position|job id|vessel|location|contract(?: type)?|employment type|publication date|published|agency)\s*:', re.I)


def limit_at_boundary(value, limit):
    if len(value) <= limit:
        return value.strip()
    candidate = value[:limit]
    boundary = max(candidate.rfind(c) for c in '.!?')
    if boundary >= min(160, limit // 2):
        return candidate[:boundary + 1].strip()
    boundary = max(0, candidate.rfind(' '))
    return candidate[:boundary].strip() + '...'


def normalize_content(value, limit=12000):
    if not value or not value.strip():
        return ''
    text = UNSAFE.sub('', value)
    text = BLOCK.sub('\n', text)
    text = TAG.sub('', text)
    text = html.unescape(text)
    text = UNSAFE.sub('', text)
    text = TAG.sub('', text)
    # Preserve the original ordering so its image/link interaction is observable.
    text = re.sub(r'\[([^]]+)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'!\[([^]]*)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'(?:\*\*|__|~~|(?<!\*)\*(?!\*)|(?<!_)_(?!_))', '', text)
    text = text.replace('`', ' ')
    lines = []
    for line in text.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        line = re.sub(r'\s+', ' ', line).strip()
        line = re.sub(r'^(?:[-*+]\s+)', '- ', line)
        line = re.sub(r'^(#{1,6})\s*', '## ', line)
        if line and not DEBRIS.search(line):
            lines.append(line)
    return limit_at_boundary('\n'.join(lines), limit)


def normalize_summary(value):
    lines = normalize_content(value).split('\n')
    while len(lines) > 1 and METADATA.match(lines[0]):
        lines.pop(0)
    text = ' '.join(line.lstrip('- #').strip() for line in lines if line.strip())
    return limit_at_boundary(text, 700)


def strip_tags_baseline(value):
    """Deliberately simple comparator, not a competing production parser."""
    return re.sub(r'\s+', ' ', html.unescape(TAG.sub('', value))).strip()
