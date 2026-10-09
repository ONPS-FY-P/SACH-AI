import asyncio
import json
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from typing import Literal
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from starlette.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from . import config, groq, ollama
from .pipeline import answer_chat
from .retrieval import Retriever
from .schemas import ChatRequest, ChatResponse

class BodyLimit:
    """Bound uploads before multipart parsing/spooling, including chunked bodies."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['method'] != 'POST':
            return await self.app(scope, receive, send)
        limit = config.MAX_REQUEST_BYTES if scope['path'] == '/api/transcribe' else 100_000
        chunks, size = [], 0
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            data = message.get('body', b'')
            size += len(data)
            if size > limit:
                return await JSONResponse({'detail': 'Request body is too large.'}, 413)(scope, receive, send)
            chunks.append(data)
            if not message.get('more_body', False):
                break
        body = b''.join(chunks)
        consumed = False
        async def replay():
            nonlocal consumed
            if not consumed:
                consumed = True
                return {'type': 'http.request', 'body': body, 'more_body': False}
            return await receive()
        return await self.app(scope, replay, send)

@asynccontextmanager
async def lifespan(app):
    app.state.retriever = await run_in_threadpool(Retriever)
    app.state.ai_lock = asyncio.Lock()
    app.state.requests = defaultdict(deque)
    yield

app = FastAPI(title='Naaya RAG API', version='2.0.0', lifespan=lifespan)
app.add_middleware(BodyLimit)


def rate_limit(request, limit=12):
    now = time.monotonic()
    queues = request.app.state.requests
    for key in list(queues):
        q = queues[key]
        while q and now - q[0] >= 60:
            q.popleft()
        if not q:
            del queues[key]
    # Do not trust arbitrary X-Forwarded-For headers; proxy trust is configured in Uvicorn.
    identity = request.client.host if request.client else 'unknown'
    q = queues[identity]
    if len(q) >= limit:
        raise HTTPException(429, 'Too many requests. Wait one minute.')
    q.append(now)

@app.get('/health')
def health(request: Request):
    retriever = request.app.state.retriever
    return {'status': 'ok', 'index_ready': retriever.collection is not None,
            'chunks': len(retriever.rows), 'groq_configured': groq.configured(), 'requires_auth': False,
            'index_message': retriever.error}

@app.get('/ready')
async def ready(request: Request):
    local = await ollama.readiness()
    ok = request.app.state.retriever.collection is not None and all(local.values()) and groq.configured()
    return JSONResponse({'ready': ok, 'ollama': local, 'groq_configured': groq.configured(),
                         'index_ready': request.app.state.retriever.collection is not None}, status_code=200 if ok else 503)

@app.post('/api/chat', response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request):
    rate_limit(request)
    lock = request.app.state.ai_lock
    # One CPU pipeline at a time; do not accumulate long queues on an i3.
    if lock.locked():
        raise HTTPException(429, 'The local AI is answering another question. Please retry shortly.')
    async with lock:
        try:
            return await asyncio.wait_for(answer_chat(body, request.app.state.retriever), timeout=780)
        except asyncio.TimeoutError:
            raise HTTPException(504, 'The local pipeline timed out. Check Ollama and available RAM.') from None

@app.post('/api/transcribe')
async def transcribe(request: Request, file: UploadFile = File(...), language: Literal['en', 'hi', 'mr'] = Form('en')):
    rate_limit(request)
    types = {'audio/m4a': 'm4a', 'audio/mp4': 'm4a', 'audio/x-m4a': 'm4a',
             'audio/wav': 'wav', 'audio/x-wav': 'wav', 'audio/mpeg': 'mp3', 'audio/webm': 'webm'}
    try:
        if file.content_type not in types:
            raise HTTPException(415, 'Send an M4A, MP4, WAV, MP3 or WebM recording.')
        data = await file.read(config.MAX_AUDIO_BYTES + 1)
        if not data or len(data) > config.MAX_AUDIO_BYTES:
            raise HTTPException(413, 'Audio must be nonempty and at most 10 MB.')
        result = await groq.call_groq('audio/transcriptions',
            files={'file': ('question.' + types[file.content_type], data, file.content_type)},
            data={'model': config.STT_MODEL, 'language': language, 'response_format': 'json', 'temperature': '0'})
        text = result.get('text', '')
        if not isinstance(text, str) or not text.strip():
            raise HTTPException(422, 'No speech detected. Try recording again.')
        return {'text': text.strip()[:2500]}
    finally:
        await file.close()

@app.get('/api/portals')
def portals():
    return json.loads((config.ROOT / 'data/portals.json').read_text(encoding='utf-8'))
