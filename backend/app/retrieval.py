"""Persistent Chroma vectors + lexical ranking; no default embedding downloads."""
import json
import math
import re
from collections import Counter, defaultdict
import chromadb
from chromadb.config import Settings
from fastapi import HTTPException
from . import config, ollama
from .loaders import fingerprint

STOP = set('the a an is of to and in on for with my me what how can i it this that be are as or do should'.split())
def tokens(text):
    return [t for t in re.findall(r'[a-z0-9]+', text.lower()) if t not in STOP and len(t) > 1]

def client(path):
    return chromadb.PersistentClient(path=str(path), settings=Settings(anonymized_telemetry=False))

def embedding_text(row):
    m = row['metadata']
    return f"{m['act_name']} {m['provision_type']} {m['section_number']} {m['section_title']}\n{row['text']}"

class Retriever:
    def __init__(self, index_dir=config.INDEX_DIR):
        self.index_dir = index_dir
        self.collection = None
        self.rows = []
        self.error = 'Run python ingest.py before asking questions.'
        active = index_dir / 'active.json'
        if not active.exists():
            return
        try:
            pointer = json.loads(active.read_text(encoding='utf-8'))
            directory = index_dir / pointer['build']
            manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
            expected = {'model': config.EMBED_MODEL, 'chunk_chars': config.CHUNK_CHARS,
                        'chunk_overlap': config.CHUNK_OVERLAP, 'version': config.PIPELINE_VERSION}
            if manifest['settings'] != expected or manifest['files'] != fingerprint():
                raise ValueError('Datasets or embedding settings changed. Run python ingest.py, then restart the backend.')
            self.rows = json.loads((directory / 'chunks.json').read_text(encoding='utf-8'))
            self.db = client(directory / 'chroma')
            self.collection = self.db.get_collection('legal', embedding_function=None)
            if self.collection.count() != len(self.rows):
                raise ValueError('Incomplete vector index. Re-run ingestion.')
            self.by_id = {r['id']: r for r in self.rows}
            self.counts = [Counter(tokens(embedding_text(r))) for r in self.rows]
            self.lengths = [sum(c.values()) for c in self.counts]
            self.average = sum(self.lengths) / max(1, len(self.rows))
            self.df = Counter(t for c in self.counts for t in c)
            self.error = ''
        except Exception as exc:
            self.collection = None
            self.rows = []
            self.error = str(exc) if isinstance(exc, ValueError) else 'Index cannot be opened. Re-run ingestion and restart.'

    def lexical(self, query):
        terms = set(tokens(query))
        scored = []
        for i, counts in enumerate(self.counts):
            score = 0.0
            for term in terms:
                tf = counts[term]
                if tf:
                    idf = math.log(1 + (len(self.rows)-self.df[term]+.5)/(self.df[term]+.5))
                    score += idf * tf * 2.2 / (tf + 1.2 * (.25 + .75*self.lengths[i]/self.average))
            if score:
                scored.append((score, self.rows[i]['id']))
        return sorted(scored, reverse=True)[:24]

    def rank(self, query, vector, limit=config.CANDIDATES):
        result = self.collection.query(query_embeddings=[vector], n_results=min(24, len(self.rows)), include=['distances'])
        dense = result['ids'][0]
        lexical = [key for _, key in self.lexical(query)]
        scores = defaultdict(float)
        for sequence in (dense, lexical):
            for rank, key in enumerate(sequence):
                scores[key] += 1 / (60 + rank)
        # Respect explicit article/section requests without conflating Act numbers.
        explicit = re.search(r'\b(article|section)\s+(\d+[A-Za-z]*)\b', query, re.I)
        if explicit:
            for key in scores:
                m = self.by_id[key]['metadata']
                if m['provision_type'] == explicit[1].lower() and m['section_number'].lower() == explicit[2].lower():
                    scores[key] += .08
        selected, counts = [], Counter()
        for key in sorted(scores, key=scores.get, reverse=True):
            row = self.by_id[key]
            m = row['metadata']
            group = (m['act_name'], m['provision_type'], m['section_number'])
            if counts[group] >= 2:
                continue
            counts[group] += 1
            selected.append(row)
            if len(selected) == limit:
                break
        return [dict(id=f'S{i+1}', title=f"{r['metadata']['act_name']} · {r['metadata']['provision_type'].title()} {r['metadata']['section_number']} · {r['metadata']['section_title']}",
                     text=r['text'], chunk_id=r['id'], **r['metadata']) for i, r in enumerate(selected)]

    async def search(self, query):
        from starlette.concurrency import run_in_threadpool
        if self.collection is None:
            raise HTTPException(503, self.error)
        vector = (await ollama.embeddings([query], query=True))[0]
        return await run_in_threadpool(self.rank, query, vector)
