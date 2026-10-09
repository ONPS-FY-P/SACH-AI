import asyncio
from app.retrieval import Retriever

QUERY = "police officer bribe public servant undue advantage gratification corruption"

async def main():
    r = Retriever()
    print("index error:", r.error or "none")
    hits = await r.search(QUERY)
    for h in hits:
        print(h['id'], '|', h['act_name'], '|', h['provision_type'], h['section_number'], '|', h['section_title'])

asyncio.run(main())