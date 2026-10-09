import json
import math
import httpx
from fastapi import HTTPException
from pydantic import BaseModel, ValidationError
from . import config

async def post(path, payload):
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(240, connect=8)) as client:
            response = await client.post(config.OLLAMA_URL + path, json=payload)
        if response.status_code == 404:
            raise HTTPException(503, 'Ollama model missing. Pull nomic-embed-text and qwen2.5:1.5b, then retry.')
        if not response.is_success:
            raise HTTPException(503, 'Ollama failed. Check its logs, available RAM and model installation.')
        return response.json()
    except httpx.TimeoutException:
        raise HTTPException(504, 'Local Ollama timed out. Close other apps; CPU inference can be slow.') from None
    except (httpx.HTTPError, ValueError):
        raise HTTPException(503, 'Cannot reach Ollama. Start Ollama on the backend computer.') from None

async def embeddings(texts: list[str], *, query=False):
    prefix = 'search_query: ' if query else 'search_document: '
    result = await post('/api/embed', {'model': config.EMBED_MODEL,
        'input': [prefix + t for t in texts], 'truncate': False, 'keep_alive': 0})
    vectors = result.get('embeddings', [])
    if len(vectors) != len(texts) or any(not v or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in v) for v in vectors):
        raise HTTPException(502, 'Ollama returned invalid embeddings.')
    return vectors

async def structured(system: str, content: str, schema: type[BaseModel], *, max_tokens=850):
    result = await post('/api/chat', {'model': config.LOCAL_MODEL, 'stream': False,
        'keep_alive': 0, 'format': schema.model_json_schema(),
        'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': content}],
        'options': {'temperature': 0, 'num_ctx': 4096, 'num_predict': max_tokens, 'num_thread': 4}})
    try:
        return schema.model_validate_json(result['message']['content'])
    except (KeyError, TypeError, ValueError, ValidationError):
        raise HTTPException(502, 'The local model returned invalid structured output. Retry or use a larger local model in app/config.py.') from None

async def readiness():
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(config.OLLAMA_URL + '/api/tags')
            response.raise_for_status()
            names = {m['name'] for m in response.json()['models']}
        return {'reachable': True, 'embedding_model': config.EMBED_MODEL in names, 'local_model': config.LOCAL_MODEL in names}
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        return {'reachable': False, 'embedding_model': False, 'local_model': False}
