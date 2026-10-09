# Naaya AI — integrated Expo + Ollama RAG + FastAPI

Start with **docs/SETUP_RUN_HOSTING_APK.md**. The app opens without login.

- `backend/`: FastAPI, persistent Chroma ingestion, Ollama retrieval/section explanations, Groq guidance and transcription.
- `mobile/`: your Expo SDK 57 app with service/auth wiring updated. Theme, layout and styles retained; the former login button clears the current chat within the same styled card.
- `docs/FRONTEND_EDITS.md`: exact before/after diffs and file replacement instructions.
- `docs/COMPLETE_CODE.md`: full source/config text, with destination paths.
- `docs/FILE_TREE.md`: distributable folder structure.
- `docs/VALIDATION.md`: completed checks and checks requiring your computer/phone.
- `docs/DATA_AUDIT.md`: corpus counts and parsing limitations.
- `compose.yaml`, `deploy/Caddyfile`: optional server deployment.

Replace the placeholder `GROQ_API_KEY` in `backend/.env` locally. Never put your real key in mobile code. The vector index is not bundled: install/pull Ollama models and run `python ingest.py`. All 11 original JSON datasets are included byte-for-byte.
