"""Load ALL supplied JSON files; section-aware, deterministic and auditable.
No LLM is allowed to invent section metadata during ingestion.
"""
import hashlib
import json
import re
from pathlib import Path
from . import config

NAMES = {
    'a202345.json': 'Bharatiya Nyaya Sanhita, 2023',
    'constitution_full_dataset.json': 'Constitution of India',
    'the prevention of coruption act 1988.json': 'Prevention of Corruption Act, 1988',
    'the_bharatiya_sakshya_adhiyanayam_2023.json': 'Bharatiya Sakshya Adhiniyam, 2023',
    'THE_CONSUMER_PROTECTION_ACT_2019.json': 'Consumer Protection Act, 2019',
    'THE_ENVIRONMENT.json': 'Environment (Protection) Act, 1986',
    'THE_INFORMATION_TECHNOLOGY_ACT_2000.json': 'Information Technology Act, 2000',
    'THE_JUVENILE_JUSTICE_(CARE_AND_PROTECTION_OF_CHILDREN)_ACT_2015.json': 'Juvenile Justice (Care and Protection of Children) Act, 2015',
    'The_Motor_Vehicles_Act_1988.json': 'Motor Vehicles Act, 1988',
    'THE_PROTECTION_OF_CHILDREN_FROM_SEXUAL_OFFENCES_ACT_2012.json': 'Protection of Children from Sexual Offences Act, 2012',
    'THE_PROTECTION_OF_WOMEN_FROM_DOMESTIC_VIOLENCE_ACT_2005.json': 'Protection of Women from Domestic Violence Act, 2005',
}
# Allow OCR spaces, etc. inside headings, and footnote markers around amended headings.
HEADING = re.compile(r'(?<![\w.])(\d{1,3}[A-Z]{0,2})\s*\.\s*(?:[—–]\s*)?([A-Z][^—–\n]{1,250}?)\s*(?:\.\s*)?[—–]{1,2}\s*|(?<![\w.])(\d{1,3}[A-Z]{0,2})\s*\.\s*([A-Z][^\n]{1,250}?)\.\s*-\s*')
OMITTED = re.compile(r'(?<![\w.])(\d{1,3}[A-Z]{0,2})\s*\.\s*\[(?:Omitted|Repealed)[^\]]*\]', re.I)


def clean(value):
    return re.sub(r'\s+', ' ', str(value or '')).strip()


def number_key(value):
    m = re.fullmatch(r'(\d+)([A-Z]*)', value)
    return (int(m[1]), m[2]) if m else (0, '')


def split_whole_act(text):
    """Ignore arrangement-of-sections for numbering; preserve it as unlabelled data."""
    enactment = re.search(r'BE\s+it\s+enacted', text, re.I)
    start = enactment.start() if enactment else 0
    matches = []
    for m in re.compile('(?=' + HEADING.pattern + ')').finditer(text, start):
        number, title = (m[1], m[2]) if m[1] else (m[3], m[4])
        # Do not mistake an internal numbered list or amending footnote for a heading.
        if re.search(r'\b(?:Subs\.|Ins\.|Notifn\.|w\.e\.f\.)', title):
            continue
        if re.search(r'(?<!\w)\d{1,3}\s*\.\s+[A-Z]', title):
            continue
        matches.append((m.start(), number, clean(title).rstrip('. '), m.end()))
    matches += [(m.start(), m[1], 'Omitted or repealed in supplied text', m.end()) for m in OMITTED.finditer(text, start)]
    kept = []
    last = (0, '')
    for item in sorted(matches):
        key = number_key(item[1])
        if key > last:
            kept.append(item)
            last = key
    if len(kept) < 2:
        return [('', '', text)], ['Could not reliably identify section boundaries; stored as unnumbered reference.']
    segments = [('', 'Preamble / arrangement of sections', text[:kept[0][0]])]
    warnings = []
    for i, (pos, number, title, _) in enumerate(kept):
        end = kept[i + 1][0] if i + 1 < len(kept) else len(text)
        segment = text[pos:end]
        schedule = None
        if i == len(kept) - 1:
            schedule = re.search(r'\b(?:THE\s+)?(?:(?:FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH)\s+)?SCHEDULE(?:\s*\[|\s*\(|\s+[IVX]+\b)', segment)
        tail = segment[schedule.start():] if schedule else ''
        if schedule:
            segment = segment[:schedule.start()]
        # If an unrecognised numbered heading occurs, stop attributing its text
        # to the previous section. Preserve the remaining bytes as unnumbered data.
        current_n = number_key(number)[0]
        next_n = number_key(kept[i + 1][1])[0] if i + 1 < len(kept) else current_n + 1
        gap = None
        for n in range(current_n + 1, next_n):
            found = re.search(r'(?<![\w.])' + str(n) + r'\s*\.\s*(?:\[)?[A-Z]', segment)
            if found and (gap is None or found.start() < gap):
                gap = found.start()
        if gap is not None:
            segments.append((number, title, segment[:gap]))
            segments.append(('', 'Unparsed provision — verify original', segment[gap:]))
            warnings.append(f'Unparsed material after section {number}; no inferred section labels assigned.')
        else:
            segments.append((number, title, segment))
        if tail:
            segments.append(('', 'Schedule / supplementary material', tail))
    return segments, warnings


def windows(text, size=config.CHUNK_CHARS, overlap=config.CHUNK_OVERLAP):
    text = clean(text)
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = text.rfind(' ', start + size // 2, end)
            if boundary > start:
                end = boundary
        yield text[start:end]
        if end == len(text):
            break
        start = max(start + 1, end - overlap)
        while start < end and not text[start - 1].isspace():
            start += 1


def input_records(path):
    if path.suffix.lower() == '.json':
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        if isinstance(data, dict):
            data = data.get('documents', data.get('records', [data]))
        if not isinstance(data, list) or not all(isinstance(x, dict) for x in data):
            raise ValueError(f'{path.name}: expected a JSON array of text records.')
        return data
    if path.suffix.lower() == '.jsonl':
        return [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    if path.suffix.lower() in {'.txt', '.md'}:
        return [{'text': path.read_text(encoding='utf-8-sig')}]
    raise ValueError(f'Unsupported raw file: {path.name}. This archive contains JSON only. Convert new formats to documented JSON records before ingesting.')


def fingerprint(raw_dir=config.RAW_DIR):
    files = [p for p in sorted(raw_dir.rglob('*')) if p.is_file() and not p.name.startswith('.')]
    if not files:
        raise ValueError(f'No datasets found in {raw_dir}.')
    return {p.relative_to(raw_dir).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def load_corpus(raw_dir=config.RAW_DIR):
    files = fingerprint(raw_dir)
    chunks, report, seen = [], [], set()
    for filename in files:
        path = raw_dir / filename
        records = input_records(path)
        before = len(chunks)
        problems = []
        numbered = set()
        for record_index, record in enumerate(records):
            text = clean(record.get('text') or record.get('content'))
            if not text:
                raise ValueError(f'{filename}, record {record_index}: missing text/content; refusing silent data loss.')
            act = NAMES.get(path.name, clean(record.get('act')) or path.stem.replace('_', ' '))
            # Most of the uploaded whole Acts incorrectly claim section=1.
            whole = bool(re.search(r'ARRANGEMENT OF SECTIONS|BE\s+it\s+enacted', text, re.I)) and len(text) > 8000
            kind = 'article' if record.get('article_number') else 'section'
            if whole:
                parts, notices = split_whole_act(text)
                problems.extend(notices)
            else:
                number = clean(record.get('article_number') or record.get('section') or record.get('section_number'))
                title = clean(record.get('section_title') or record.get('title') or record.get('schedule_name'))
                parts = [(number, title, text)]
            for number, title, segment in parts:
                if not segment.strip():
                    continue
                provision_type = kind if number else 'reference'
                if number:
                    numbered.add(number)
                for part, chunk in enumerate(windows(segment)):
                    digest = hashlib.sha256((act + '\0' + provision_type + '\0' + number + '\0' + chunk).encode()).hexdigest()
                    if digest in seen:
                        continue
                    seen.add(digest)
                    chunks.append({'id': digest[:32], 'text': chunk, 'metadata': {
                        'act_name': act, 'section_number': number, 'section_title': title,
                        'provision_type': provision_type, 'file': filename,
                        'record_index': record_index, 'part': part,
                    }})
        report.append({'file': filename, 'records': len(records), 'chunks': len(chunks)-before,
                       'numbered_provisions': len(numbered), 'warnings': problems})
    return chunks, {'files': files, 'documents': report, 'chunks': len(chunks)}
