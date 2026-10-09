"""Run once after adding/changing raw datasets; restart API after ingestion.
Builds a new generation and only activates it once every vector is written.
An interrupted build is resumed; the previous active generation remains intact.
"""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
from app import config, ollama
from app.loaders import load_corpus
from app.retrieval import client, embedding_text

async def ingest(check=False, force=False):
    chunks, report = load_corpus()
    settings = {'model': config.EMBED_MODEL, 'chunk_chars': config.CHUNK_CHARS,
                'chunk_overlap': config.CHUNK_OVERLAP, 'version': config.PIPELINE_VERSION}
    report['settings'] = settings
    config.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    (config.INDEX_DIR / 'audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    for item in report['documents']:
        print(f"{item['file']}: {item['chunks']} chunks, {item['numbered_provisions']} numbered provisions")
        for warning in item['warnings']:
            print('  WARNING:', warning)
    print(f'Total: {len(chunks)} chunks from {len(report["files"])} files.')
    if check:
        return
    if not chunks:
        raise ValueError('Nothing to index.')
    signature = hashlib.sha256(json.dumps([report['files'], settings], sort_keys=True).encode()).hexdigest()[:20]
    if force:
        import time
        signature += '-' + str(time.time_ns())
    directory = config.INDEX_DIR / ('build-' + signature)
    directory.mkdir(parents=True, exist_ok=True)
    db = client(directory / 'chroma')
    collection = db.get_or_create_collection('legal', embedding_function=None, metadata={'hnsw:space': 'cosine'})
    existing = set(collection.get(include=[])['ids'])
    remaining = [r for r in chunks if r['id'] not in existing]
    print(f'{len(existing)} vectors already saved; {len(remaining)} left. Keep this window open.', flush=True)
    for start in range(0, len(remaining), config.EMBED_BATCH):
        batch = remaining[start:start + config.EMBED_BATCH]
        # Keep the embedding model loaded for ingestion, while only one model is used.
        result = await ollama.post('/api/embed', {'model': config.EMBED_MODEL,
            'input': ['search_document: ' + embedding_text(r) for r in batch],
            'truncate': False, 'keep_alive': '5m'})
        vectors = result.get('embeddings', [])
        if len(vectors) != len(batch):
            raise ValueError('Ollama returned the wrong number of vectors; rerun to resume.')
        collection.upsert(ids=[r['id'] for r in batch], documents=[r['text'] for r in batch],
                          metadatas=[r['metadata'] for r in batch], embeddings=vectors)
        print(f'Indexed {len(existing) + min(start + len(batch), len(remaining))}/{len(chunks)}', flush=True)
    if collection.count() != len(chunks):
        raise ValueError('Count mismatch; use --force to build a fresh generation.')
    for name, value in [('chunks.json', chunks), ('manifest.json', report)]:
        (directory / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    pending = config.INDEX_DIR / 'active.tmp'
    pending.write_text(json.dumps({'build': directory.name}), encoding='utf-8')
    pending.replace(config.INDEX_DIR / 'active.json')
    print('Index is ready. Start/restart the API. Older build-* directories are retained as backups.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-only', action='store_true', help='Audit parsing without contacting Ollama')
    parser.add_argument('--force', action='store_true', help='Build fresh vectors even when inputs match')
    args = parser.parse_args()
    try:
        asyncio.run(ingest(args.check_only, args.force))
    except Exception as exc:
        from fastapi import HTTPException
        print('INGESTION FAILED:', exc.detail if isinstance(exc, HTTPException) else str(exc))
        raise SystemExit(1)
