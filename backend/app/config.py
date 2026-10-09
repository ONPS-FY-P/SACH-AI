"""Non-secret defaults. Only the Groq key belongs in backend/.env."""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '').strip()
# This one optional deployment override connects containers over a private network.
OLLAMA_URL = os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434').rstrip('/')
EMBED_MODEL = 'nomic-embed-text:latest'
LOCAL_MODEL = 'qwen2.5:1.5b'
CHAT_MODEL = 'openai/gpt-oss-120b'
STT_MODEL = 'whisper-large-v3-turbo'
RAW_DIR = ROOT / 'data' / 'raw'
INDEX_DIR = ROOT / 'data' / 'index'
CHUNK_CHARS = 1200
CHUNK_OVERLAP = 180
EMBED_BATCH = 4
CANDIDATES = 6
LANGUAGES = {'en': 'English', 'hi': 'Hindi', 'mr': 'Marathi'}
MAX_AUDIO_BYTES = 10 * 1024 * 1024
MAX_REQUEST_BYTES = MAX_AUDIO_BYTES + 64 * 1024
PIPELINE_VERSION = 1
