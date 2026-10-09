"""Groq handles practical guidance and audio transcription, never retrieval."""
import httpx
from fastapi import HTTPException
from . import config


def configured():
    # Refuse the explicitly supplied fake key without sending it to any provider.
    return bool(config.GROQ_API_KEY) and not config.GROQ_API_KEY.endswith('IvUwH1Dq9GCScUlLm4qaNk9')

async def call_groq(path, *, payload=None, files=None, data=None):
    if not configured():
        raise HTTPException(503, 'Replace the placeholder GROQ_API_KEY in backend/.env and restart the backend.')
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(75, connect=10)) as client:
            response = await client.post('https://api.groq.com/openai/v1/' + path,
                headers={'Authorization': 'Bearer ' + config.GROQ_API_KEY},
                json=payload, files=files, data=data)
        if response.status_code in {401, 403}:
            raise HTTPException(503, 'Groq rejected the server key. Check backend/.env and restart.')
        if response.status_code == 429:
            raise HTTPException(429, 'Groq quota/rate limit reached. Try again later.')
        if not response.is_success:
            raise HTTPException(502, 'Groq request failed. Check the model name and account access.')
        return response.json()
    except httpx.TimeoutException:
        raise HTTPException(504, 'Groq timed out. Please retry.') from None
    except (httpx.HTTPError, ValueError):
        raise HTTPException(502, 'Cannot reach Groq. Check the backend internet connection.') from None

async def guidance(system, context):
    result = await call_groq('chat/completions', payload={
        'model': config.CHAT_MODEL,
        'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': context}],
        'temperature': 0.1, 'max_completion_tokens': 4000,
        'response_format': {'type': 'json_object'},
    })
    try:
        return result['choices'][0]['message']['content']
    except (KeyError, IndexError, TypeError):
        raise HTTPException(502, 'Groq returned an empty guidance response.') from None
