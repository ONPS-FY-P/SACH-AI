import pytest
import ingest
from app import config, retrieval

ROWS = [
    {'id': 'corruption-7', 'text': 'A public servant who demands a bribe or undue advantage.', 'metadata': {'act_name': 'Prevention of Corruption Act, 1988', 'section_number': '7', 'section_title': 'Public servant being bribed', 'provision_type': 'section', 'file': 'test.json', 'record_index': 0, 'part': 0}},
    {'id': 'constitution-21', 'text': 'No person shall be deprived of life or personal liberty except according to procedure established by law.', 'metadata': {'act_name': 'Constitution of India', 'section_number': '21', 'section_title': 'Life and personal liberty', 'provision_type': 'article', 'file': 'test.json', 'record_index': 1, 'part': 0}},
]

async def test_real_chroma_persistence_resume_and_stale_detection(tmp_path, monkeypatch):
    calls = []
    report = {'files': {'test.json': 'hash'}, 'documents': [], 'chunks': 2}
    monkeypatch.setattr(config, 'INDEX_DIR', tmp_path)
    monkeypatch.setattr(ingest, 'load_corpus', lambda: (ROWS, report.copy()))
    monkeypatch.setattr(retrieval, 'fingerprint', lambda: report['files'])
    async def vectors(path, payload):
        calls.append(payload)
        return {'embeddings': [[1., 0., 0.], [0., 1., 0.]][:len(payload['input'])]}
    monkeypatch.setattr(ingest.ollama, 'post', vectors)
    await ingest.ingest()
    assert len(calls) == 1 and (tmp_path / 'active.json').exists()
    retriever = retrieval.Retriever(tmp_path)
    assert retriever.collection.count() == 2
    results = retriever.rank('public servant bribe undue advantage', [1., 0., 0.])
    assert results[0]['section_number'] == '7'
    await ingest.ingest()
    assert len(calls) == 1
    assert retrieval.Retriever(tmp_path).collection.count() == 2
    monkeypatch.setattr(retrieval, 'fingerprint', lambda: {'test.json': 'changed'})
    assert retrieval.Retriever(tmp_path).collection is None

async def test_failed_build_does_not_activate(tmp_path, monkeypatch):
    monkeypatch.setattr(config, 'INDEX_DIR', tmp_path)
    monkeypatch.setattr(ingest, 'load_corpus', lambda: (ROWS, {'files': {}, 'documents': [], 'chunks': 2}))
    async def fail(*args):
        raise RuntimeError('Ollama offline')
    monkeypatch.setattr(ingest.ollama, 'post', fail)
    with pytest.raises(RuntimeError):
        await ingest.ingest()
    assert not (tmp_path / 'active.json').exists()
