import httpx
from app import config

h = {'Authorization': 'Bearer ' + config.GROQ_API_KEY}

r = httpx.get('https://api.groq.com/openai/v1/models', headers=h, timeout=30)
print('MODELS STATUS:', r.status_code)
if r.is_success:
    for m in sorted(x['id'] for x in r.json()['data']):
        print('  ', m)
else:
    print(r.text)

r = httpx.post('https://api.groq.com/openai/v1/chat/completions', headers=h, timeout=60, json={
    'model': config.CHAT_MODEL,
    'messages': [{'role': 'user', 'content': 'Reply with a JSON object containing ok true'}],
    'response_format': {'type': 'json_object'},
    'max_completion_tokens': 50,
})
print('\nCHAT STATUS:', r.status_code)
print(r.text[:600])