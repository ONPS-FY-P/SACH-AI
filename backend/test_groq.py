import httpx
from app import config

r = httpx.post('https://api.groq.com/openai/v1/chat/completions',
    headers={'Authorization': 'Bearer ' + config.GROQ_API_KEY}, timeout=90, json={
    'model': config.CHAT_MODEL,
    'messages': [
        {'role': 'system', 'content': 'Return a JSON object only.'},
        {'role': 'user', 'content': 'Give {"ok": true} as JSON.'}],
    'response_format': {'type': 'json_object'},
    'temperature': 0.1,
    'max_completion_tokens': 4000,
})
print(r.status_code)
print(r.text[:800])