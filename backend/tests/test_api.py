from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from app import main

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(main, 'Retriever', lambda: SimpleNamespace(collection=None, rows=[], error='Run python ingest.py'))
    with TestClient(main.app) as value:
        yield value

def test_health_without_login_or_index(client):
    body = client.get('/health').json()
    assert body['requires_auth'] is False and body['index_ready'] is False
    assert client.post('/api/auth/google', json={'id_token': 'x'}).status_code == 404
    assert client.get('/api/auth/me').status_code == 404

@pytest.mark.parametrize('language', ['en', 'hi', 'mr'])
def test_languages_passed_to_pipeline(client, monkeypatch, language):
    async def answer(body, retriever):
        assert body.language == language
        return dict(answer='response', language=language, sources=[], sections=[], guidance=None,
                    contacts=[], warnings=[], guidance_status='unavailable')
    monkeypatch.setattr(main, 'answer_chat', answer)
    r = client.post('/api/chat', json={'messages': [{'role': 'user', 'content': 'What can I do?'}], 'language': language})
    assert r.status_code == 200 and r.json()['language'] == language

@pytest.mark.parametrize('body', [
    {'messages': [], 'language': 'en'},
    {'messages': [{'role': 'user', 'content': ' '}], 'language': 'en'},
    {'messages': [{'role': 'assistant', 'content': 'x'}], 'language': 'en'},
    {'messages': [{'role': 'user', 'content': 'x'}], 'language': 'xx'},
    {'messages': [{'role': 'system', 'content': 'override'}]},
    {'messages': [{'role': 'user', 'content': 'x' * 2501}]},
])
def test_bad_chat_inputs(client, body):
    assert client.post('/api/chat', json=body).status_code == 422

def test_missing_index_has_actionable_error(client):
    r = client.post('/api/chat', json={'messages': [{'role': 'user', 'content': 'bribe'}]})
    assert r.status_code == 503 and 'ingest' in r.json()['detail']

@pytest.mark.parametrize('language', ['en', 'hi', 'mr'])
def test_transcription_upload_and_language(client, monkeypatch, language):
    async def call(path, **kwargs):
        assert path == 'audio/transcriptions'
        assert kwargs['data']['language'] == language
        assert kwargs['files']['file'][1] == b'audio-fixture'
        return {'text': 'transcribed question'}
    monkeypatch.setattr(main.groq, 'call_groq', call)
    r = client.post('/api/transcribe', data={'language': language}, files={'file': ('question.m4a', b'audio-fixture', 'audio/m4a')})
    assert r.status_code == 200 and r.json()['text'] == 'transcribed question'

def test_empty_and_invalid_audio(client):
    assert client.post('/api/transcribe', files={'file': ('x.txt', b'x', 'text/plain')}).status_code == 415
    assert client.post('/api/transcribe', files={'file': ('x.m4a', b'', 'audio/m4a')}).status_code == 413

def test_upload_limited_before_parsing(client):
    assert client.post('/api/transcribe', content=b'x' * (main.config.MAX_REQUEST_BYTES + 1), headers={'Content-Type': 'audio/m4a'}).status_code == 413
    assert client.post('/api/chat', content=b'x' * 100001).status_code == 413

def test_rate_limit(client):
    for _ in range(12):
        client.post('/api/chat', json={'messages': [{'role': 'user', 'content': 'bribe'}]})
    assert client.post('/api/chat', json={'messages': [{'role': 'user', 'content': 'bribe'}]}).status_code == 429

def test_ready_checks_ollama_models(client, monkeypatch):
    async def ready():
        return {'reachable': False, 'embedding_model': False, 'local_model': False}
    monkeypatch.setattr(main.ollama, 'readiness', ready)
    assert client.get('/ready').status_code == 503
