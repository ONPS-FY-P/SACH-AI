"""Live local acceptance test; requires running API, ingested index and real Groq key.
python scripts/smoke_test.py --url http://127.0.0.1:8000 --language en
"""
import argparse
import httpx

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8000')
parser.add_argument('--language', choices=['en', 'hi', 'mr'], default='en')
args = parser.parse_args()
queries = {
    'en': 'A police officer is asking me for a bribe. What should I do?',
    'hi': 'एक पुलिस अधिकारी मुझसे रिश्वत माँग रहा है। मुझे क्या करना चाहिए?',
    'mr': 'एक पोलीस अधिकारी माझ्याकडे लाच मागत आहे. मी काय करावे?',
}
with httpx.Client(base_url=args.url.rstrip('/'), timeout=810) as client:
    health = client.get('/health')
    health.raise_for_status()
    print('HEALTH:', health.json())
    response = client.post('/api/chat', json={'language': args.language, 'messages': [{'role': 'user', 'content': queries[args.language]}]})
    response.raise_for_status()
    result = response.json()
    print(result['answer'])
    assert result['language'] == args.language
    assert result['guidance_status'] == 'ok', 'Guidance unavailable: check Groq key/model/quota.'
    assert any(s['act_name'] == 'Prevention of Corruption Act, 1988' and s['section_number'] == '7' for s in result['sections']), 'Section 7 was not confirmed. Inspect retrieval/model quality; do not fake a pass.'
    ids = {s['id'] for s in result['sources']}
    assert all(s['source_id'] in ids for s in result['sections'])
    print('\nPASS: live response shape and expected source. Manually review legal relevance and language quality.')
