import json
from app import config
from app.loaders import load_corpus, split_whole_act, windows

def test_every_supplied_file_loaded_and_numbered():
    chunks, report = load_corpus()
    assert len(report['documents']) == 11
    assert all(x['chunks'] > 0 for x in report['documents'])
    for act, number in [('Bharatiya Nyaya Sanhita, 2023', '358'), ('Prevention of Corruption Act, 1988', '7'), ('Constitution of India', '21')]:
        assert any(r['metadata']['act_name'] == act and r['metadata']['section_number'] == number for r in chunks)
    assert all(len(r['text']) <= config.CHUNK_CHARS for r in chunks)
    assert len({r['id'] for r in chunks}) == len(chunks)

def test_toc_not_used_as_section_text():
    text = 'ARRANGEMENT OF SECTIONS 1. First. 2. Second. BE it enacted 1. First.—Body of first. 2. Second. —Body of second.'
    sections, _ = split_whole_act(text)
    assert sections[0][0] == ''
    assert sections[1][0] == '1' and 'Body of first' in sections[1][2]
    assert sections[2][0] == '2' and 'Body of second' in sections[2][2]

def test_abbreviations_and_spaced_dash():
    sections, _ = split_whole_act('BE it enacted 1. First. —Body. 2. Property, etc., offences.—Body two.')
    assert [s[0] for s in sections] == ['', '1', '2']

def test_duplicate_records_deduplicated(tmp_path):
    row = {'act': 'Example Act', 'section': '7', 'text': 'A public servant accepts an undue advantage.'}
    (tmp_path / 'a.json').write_text(json.dumps([row, row]))
    (tmp_path / 'b.json').write_text(json.dumps([row]))
    rows, _ = load_corpus(tmp_path)
    assert len(rows) == 1

def test_unsupported_or_empty_records_fail_loudly(tmp_path):
    import pytest
    p = tmp_path / 'broken.json'
    p.write_text('[{"section": "1"}]')
    with pytest.raises(ValueError, match='missing text'):
        load_corpus(tmp_path)
    p.unlink()
    (tmp_path / 'unsupported.pdf').write_bytes(b'pdf')
    with pytest.raises(ValueError, match='Unsupported'):
        load_corpus(tmp_path)

def test_windows_keep_tail():
    chunks = list(windows(' '.join('word'+str(i) for i in range(900))))
    assert chunks[-1].endswith('word899') and len(chunks) > 1
