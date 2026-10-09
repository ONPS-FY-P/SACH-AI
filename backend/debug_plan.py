import asyncio, json
from app import ollama
from app.schemas import SearchPlan

async def main():
    plan = await ollama.structured(
        'You translate questions into English search queries for Indian legal references. '
        'Include useful synonyms (for example bribe, undue advantage, public servant). '
        'Do not answer. Return JSON matching the schema.',
        json.dumps({'previous_questions': [], 'question': 'A police officer is asking me for a bribe. What should I do?'}),
        SearchPlan, max_tokens=250)
    print('PLAN QUERY:', plan.query)

asyncio.run(main())