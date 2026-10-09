# Naaya AI — setup, integration, hosting and APK guide

Prepared for the attached ZIP on 9 October 2026: Windows, Intel i3 10th generation, no GPU; English, Hindi and Marathi.

## 1. Findings from your actual project

The app uses Expo SDK 57, Expo Router, React Native 0.86.3 and React 19.2.3. It targets Android/iOS, not web. The previous backend used keyword search without Ollama or a vector store.

| Feature | Existing implementation | Integration |
|---|---|---|
| Chat | `mobile/src/app/(tabs)/index.tsx` | Existing bubbles, source modal and composer consume the new backend |
| Language | `src/components/Header.tsx`, `src/context/AppContext.tsx` | EN/हि/म header buttons are the actual language selector; there is no separate settings screen. Choice persists and is sent with each request |
| Recording | `src/hooks/useVoiceInput.ts`, `expo-audio` | M4A upload, Groq transcription, review/edit before sending, 60-second limit, cache cleanup |
| Read aloud | `expo-speech` | Selects an installed voice for each answer's language, chunks long answers and supports stop |
| Portals | `src/app/(tabs)/complaints.tsx` | Filtering and official link opening retained |
| Emergency | `src/app/(tabs)/emergency.tsx` | Existing phone-dialler actions retained; no automatic call |
| Google auth | `src/services/google.ts`, context, backend auth | Deleted routes, implementation, dependency and configuration |
| Native config | Originally only `app.config.ts` | Added `app.json` for static values/EAS ID; dynamic file controls local HTTP builds |
| Legal corpus | `backend/data/raw` | All 11 JSON files retained unchanged |

**Necessary authentication exception:** the former Google login button now says “Clear this chat,” with a chat icon, inside the same styled account card. Login text/error controls are removed. This is required to remove authentication. No theme, colours, spacing or screen layout was redesigned. Exact changes are in `FRONTEND_EDITS.md`.

## 2. How the pipeline works

1. App sends history and selected `language` (`en`, `hi`, `mr`).
2. Local Ollama `qwen2.5:1.5b` converts the latest question to an English search query, resolving follow-ups from recent user questions.
3. Ollama `nomic-embed-text` embeds that query. The same model embeds documents during ingestion.
4. Persistent Chroma vector results combine with lexical ranking. Explicit article/section references receive a ranking boost.
5. Local Ollama selects relevant excerpts and explains them in the chosen language. The server copies Act/section metadata from the index and validates source IDs and quoted evidence. Unnumbered or marked repealed/omitted provisions cannot be returned as applicable sections.
6. Groq receives the question and selected sections/excerpts and returns practical guidance only. It selects contact IDs; the server supplies curated telephone numbers/URLs.
7. The backend returns both structured fields and the existing `answer`/`sources` fields, preserving your chat presentation.

Chroma is retained because your corpus is small and a single-process persistent database fits this setup. No LangChain/LangGraph dependency is needed. Only one chat pipeline runs at a time. Models unload between query stages to reduce peak RAM; ingestion keeps the embedding model loaded.

Your RAM was not specified. **Planning estimate:** aim for at least 8 GB system RAM; 12–16 GB is more comfortable with Windows and Expo. A 4 GB Windows machine is a poor fit for the full stack. No GPU is required for these small CPU models, but replies can take minutes. No benchmark on your i3 is claimed. Use a real phone instead of an emulator, and EAS cloud builds instead of local Android builds. Allow several GB of free disk for models, Python and npm dependencies.

The 1.5B model is a resource compromise; review multilingual/relevance quality. To use a larger local model, pull it and change `LOCAL_MODEL` in `backend/app/config.py`. Changing `EMBED_MODEL` requires re-ingestion with `--force`; changing only the local chat model does not.

## 3. Where each file goes

1. Extract `Naaya-Mobile-Source.zip` into a new folder, e.g. `C:\Naaya`. The project root inside is `naaya-mobile-source`.
2. Prefer the complete delivered folder to avoid retaining obsolete auth files.
3. To patch an existing project, follow `FRONTEND_EDITS.md`: replace listed files and delete explicitly removed files. Do not copy generated caches or `node_modules`.
4. `COMPLETE_CODE.md` contains complete source/config text with a path above each code block. Binary assets, original datasets and npm lockfile are supplied as files in the ZIP.
5. `FILE_TREE.md` lists the complete distributable tree; `DATA_AUDIT.md` explains ingestion findings.

## 4. Install prerequisites

1. Install 64-bit **Python 3.12**, including the launcher:

   ```powershell
   py -3.12 --version
   ```

2. Install a Node.js LTS version compatible with SDK 57. Checks here used Node 24.19.0:

   ```powershell
   node --version
   npm --version
   ```

3. Install Ollama from <https://ollama.com/download/windows> and start the desktop application. Its API is normally `http://127.0.0.1:11434`. Alternatively run `ollama serve` in a terminal. Do not start a second server when the desktop app already owns that port.
4. Pull both models:

   ```powershell
   ollama pull nomic-embed-text
   ollama pull qwen2.5:1.5b
   ollama list
   Invoke-RestMethod http://127.0.0.1:11434/api/tags
   ```

5. `ollama list` shows downloaded models. `ollama ps` shows loaded models and can be empty while idle. This implementation unloads models after inference to conserve RAM.
6. Do not expose port 11434 to the phone/internet. Only FastAPI needs access to Ollama.

## 5. Install/configure FastAPI

1. Open PowerShell in `C:\Naaya\naaya-mobile-source\backend`, adapting the extraction path.
2. Create the environment and install dependencies:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install --upgrade pip
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

   Using the environment's Python directly avoids PowerShell activation-policy problems.

3. Open `backend/.env`. It contains exactly one assignment:

   ```dotenv
   GROQ_API_KEY=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
   ```

   Replace the value with your real Groq key. Keep it on the backend, out of JavaScript, `app.json`, EAS public variables and Git. Restart the API after editing. The code refuses this placeholder before sending it to Groq.
4. Model/chunk settings live in `backend/app/config.py`; no extra backend `.env` variables are required. The optional process environment override `OLLAMA_BASE_URL` is used only when connecting to a private Ollama service during deployment.

## 6. Audit and ingest once

From **backend**:

```powershell
.\.venv\Scripts\python.exe ingest.py --check-only
.\.venv\Scripts\python.exe ingest.py
```

The first command audits parsing without Ollama. The second embeds approximately 3,020 chunks, printing batch progress. Initial CPU ingestion may take significant time. Keep Ollama running. Only run one ingestion process at a time.

`backend/data/index/` contains `audit.json`, generation directories `build-<fingerprint>/`, and `active.json`. Each generation contains Chroma storage, `chunks.json` and `manifest.json`. A generation becomes active only after all vectors are written. Interrupted runs resume already saved vectors; older generations remain as backups.

You do not ingest every launch. After changing/adding/deleting raw data, rerun ingestion and restart the API. Startup fingerprints reject a stale index. Stop the API before changing data. If model weights change under the same tag name, use `python ingest.py --force` because a tag alone cannot detect changed weights.

**Formats:** every supplied dataset is JSON. The loader also supports JSONL, TXT and Markdown. Unsupported added formats raise a clear error instead of being silently ignored. No PDF/DOCX corpus files exist in the attachment; convert future ones into reviewed JSON records first. Minimal record:

```json
[{"act":"Exact Act name and year","section":"7","section_title":"Exact heading","text":"Full verified provision text"}]
```

Use `article_number` for Constitution articles. Several whole-Act files incorrectly labelled their complete text as section 1; the new loader parses actual headings and stores ambiguous spans without guessed section numbers. It retains preambles/schedules as reference material.

A distinct BNSS dataset, a verified recording-rights database, and current amendments to every supplied Act were **not** present. They are not fabricated or silently downloaded. Review OCR, amendments and source completeness before relying on the content. See `DATA_AUDIT.md`.

## 7. Start and check the backend

From **backend**:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

Keep that terminal open. In another terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/ready
```

Expect `index_ready: true`, `groq_configured: true`, `requires_auth: false`. `/ready` checks the index, Ollama reachability and installed model names. It detects a configured non-placeholder key, **not** its validity or remaining Groq quota; a live query checks that. Interactive API documentation: <http://127.0.0.1:8000/docs>. There are no login endpoints.

## 8. Start Expo and connect a real phone

1. Put the laptop and phone on the same private Wi-Fi. Guest networks may block device-to-device traffic.
2. Run `ipconfig` and find the laptop's Wi-Fi IPv4 address, e.g. `192.168.1.5`.
3. On the phone browser open `http://192.168.1.5:8000/health`, using the real IP. This must work first.
4. Allow Python/FastAPI and Metro through Windows Firewall on private networks. Do not disable the firewall globally.
5. Set **mobile/.env** to its one public connection value:

   ```dotenv
   EXPO_PUBLIC_API_URL=http://192.168.1.5:8000
   ```

   Phone `localhost` means the phone. `0.0.0.0` is a server bind address, not a client URL.

6. Open another terminal in **mobile**:

   ```powershell
   npm ci
   npx expo install --check
   npm run typecheck
   npm run lint
   npx expo start --go --lan --clear
   ```

7. Scan the QR using a compatible SDK 57 Expo Go installation. If SDK versions differ, use an EAS development APK below. The explicit `--go` is helpful because this project includes `expo-dev-client`.
8. With a development APK instead, run `npx expo start --dev-client --lan --clear`.
9. A standalone `lan` APK requires no Metro, but still needs FastAPI/Ollama on the laptop and the same LAN. A hosted preview APK needs a reachable HTTPS API.
10. Restart Metro after `.env` changes. Rebuild standalone APKs to change embedded URLs. If the laptop IP changes, update the URL or reserve its address in the router.

Expo `--tunnel` tunnels Metro, not FastAPI. Native mobile requests do not need browser CORS configuration. Web was not added as a target.

## 9. Test language and voice features

1. Select EN, ask a question and check English explanation/guidance.
2. Select हि, ask the next question and check Hindi. Select म and check Marathi. Language preference persists across launches.
3. Each request uses the selection at send time. An already running request retains that language; earlier messages are not automatically translated. Speaker playback uses the stored language of each answer, even after switching the app's language.
4. Tap the microphone, grant permission, speak and stop. Recording stops at 60 seconds. Review/edit the inserted transcript, then send; transcription does not auto-submit.
5. Leaving the chat/backgrounding cancels recording. Stale transcripts are ignored. Starting recording stops speech playback. Temporary recording files are removed.
6. Tap an answer's speaker to read; tap again to stop. Install English/Hindi/Marathi voices in the phone's text-to-speech settings if missing. Availability depends on the installed OS speech engine; an app cannot guarantee an absent voice. Check volume and iOS silent mode.
7. Groq transcription and guidance need a valid key and backend internet access. Local retrieval does not make these cloud features offline. Phone TTS may need voice downloads/internet depending on its engine.
8. Test a complaint link and emergency dialler on the phone. These existing actions do not require backend/login; the destination may need connectivity. No automatic complaint submission or phone call is performed.

Questions and selected excerpts go to Groq for guidance; recordings go to Groq for transcription. Chats remain in app memory; no server history database is added. Source excerpts remain in their original language as evidence. Explanations, practical guidance and contact labels are localised; Act names retain their exact names.

## 10. Test query and expected response shape

With the API running:

```powershell
$body = @{
  messages = @(@{ role = "user"; content = "A police officer is asking me for a bribe. What should I do?" })
  language = "en"
} | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/chat -Method Post -ContentType "application/json; charset=utf-8" -Body $body
```

From **backend**, run the included live acceptance checks sequentially:

```powershell
.\.venv\Scripts\python.exe scripts/smoke_test.py --language en
.\.venv\Scripts\python.exe scripts/smoke_test.py --language hi
.\.venv\Scripts\python.exe scripts/smoke_test.py --language mr
```

They consume real model resources/Groq quota and intentionally fail if the expected reference is absent. This is an **illustrative shape, not a live answer captured here**:

```json
{
  "answer": "Potentially relevant legal provisions\n\n[S1] Prevention of Corruption Act, 1988 — Section 7\nA short explanation, followed by practical steps...",
  "language": "en",
  "sources": [{
    "id": "S1",
    "title": "Prevention of Corruption Act, 1988 · Section 7 · Offence relating to public servant being bribed",
    "text": "Actual retrieved excerpt from the dataset",
    "file": "the prevention of coruption act 1988.json",
    "chunk_id": "stable-content-derived-id",
    "act_name": "Prevention of Corruption Act, 1988",
    "provision_type": "section",
    "section_number": "7",
    "section_title": "Offence relating to public servant being bribed"
  }],
  "sections": [{
    "source_id": "S1",
    "act_name": "Prevention of Corruption Act, 1988",
    "section_number": "7",
    "provision_type": "section",
    "explanation": "This provision may be relevant to the alleged demand for an undue advantage by a public servant.",
    "evidence": "A verbatim supporting quote copied from that source",
    "status": "potentially_relevant"
  }],
  "guidance": {
    "summary": "Consider contacting the relevant authority and preserving available information.",
    "steps": ["Keep the original messages and note when and where the demand occurred."],
    "contact_ids": ["legal_aid"],
    "recording_note": "Check with the relevant authority or lawyer before further recordings; do not assume every recording is lawful or admissible.",
    "follow_up": "Which state did this happen in?"
  },
  "contacts": [{
    "id": "legal_aid",
    "name": "NALSA / District Legal Services Authority",
    "scope": "India — legal aid; eligibility and availability vary",
    "phone": "15100",
    "url": "https://nalsa.gov.in/",
    "checked_on": "2026-10-09"
  }],
  "warnings": ["General legal information, not legal advice. The supplied datasets may be incomplete or outdated. Applicability depends on the facts and current law."],
  "guidance_status": "ok"
}
```

IDs/wording can vary. For this example, check section 7 is backed by a genuine corruption-Act excerpt. Do not expect unrelated Constitution articles merely because they are indexed. Section 8 may be conditional on additional facts about payment; demand alone does not establish those facts. The state should be asked before offering state-specific contacts. Maharashtra ACB is scoped to Maharashtra, and CVC is not treated as the universal route for state police.

If Groq fails, validated local sections are still returned with `guidance: null`, `guidance_status: "unavailable"` and a visible explanation. Ollama/index failure produces an actionable error. Source-quote validation proves provenance, not legal correctness of the entire explanation; human review is still required.

## 11. Hosting options

The APK does **not** contain Python, Chroma or Ollama. A reachable backend must remain running. Start with LAN; use a CPU VPS if you need access away from your laptop network.

| Option | Deployment | Pros | Cons |
|---|---|---|---|
| Laptop | Ollama + FastAPI on Windows | Existing hardware; simple development | Must remain on; CPU latency; LAN-only by default |
| CPU VPS, e.g. DigitalOcean/AWS EC2/Azure VM | Included Compose stack and HTTPS proxy | Control over RAM, persistent disk and request timeouts | Compute cost, maintenance/backups, limited concurrency |
| Render | Paid Docker API + disk; private Ollama service + disk | Managed deployment/HTTPS | Must allocate sufficient RAM; persistent disks unavailable on free web service; runtime ingestion and request limits |
| Railway | API and private Ollama service with volumes | Convenient networking/deployment | Usage costs, memory sizing and request limits |
| GPU VM | Same architecture, GPU-enabled Ollama | Faster or larger local models | Higher cost and driver/runtime setup; unnecessary for first small demo |

Check current plans, RAM, storage and HTTP timeouts before purchase; no fixed prices or performance guarantees are assumed. For these defaults, 8–16 GB total VM RAM is a planning starting point, not a measured minimum. Larger models/traffic need more. GPU VRAM depends on weights, quantisation and context; this implementation runs without a GPU.

### 11A. VPS: concrete commands

1. Create an Ubuntu VM and install Docker/Compose using <https://docs.docker.com/engine/install/ubuntu/>.
2. Transfer the project through SSH/SCP. Put the real key into the server's `backend/.env`; keep it out of a public repo.
3. From the project root:

   ```bash
   docker compose up -d ollama
   docker compose exec ollama ollama pull nomic-embed-text
   docker compose exec ollama ollama pull qwen2.5:1.5b
   docker compose build api
   docker compose run --rm api python ingest.py
   docker compose up -d api
   curl http://127.0.0.1:8000/health
   ```

4. Point a real domain's DNS A record at the VM. Replace `api.example.com` in `deploy/Caddyfile` with that domain.
5. Allow TCP 80/443, keep SSH access limited appropriately, then run:

   ```bash
   docker compose --profile public up -d
   ```

   Caddy serves HTTPS. API binds to loopback on the host; Ollama has no published host port.
6. Test the HTTPS `/health` and a real query. The included proxy permits long CPU responses; other CDNs/hosts may impose a shorter limit. Use faster compute if needed.
7. Back up `naaya_index`/`ollama_models` volumes and your raw datasets/configuration. `docker compose down -v` deletes volumes: do not use it for an ordinary restart.
8. After code/data changes rebuild the API, rerun ingestion if necessary, then recreate API. After editing the key, recreate API so its `env_file` is read again.

No user login is introduced. The backend has per-process request limits and one chat slot, but anonymous public access can consume your Groq quota. Apply provider quotas and gateway limits for a public demo. A shared secret embedded in an APK is not adequate protection. The Docker command ignores forwarded headers, so behind the included proxy limits are aggregate; configure explicit trusted proxies if you later need per-client limits. Multiple API instances would require shared rate limiting and a different vector-store serving arrangement.

### 11B. Render/Railway

1. Deploy `backend/Dockerfile` as the API; set private `GROQ_API_KEY` in the service settings. Expose container port **8000**.
2. Mount persistent storage at `/app/data/index`.
3. Deploy private `ollama/ollama` with a volume at `/root/.ollama`, adequate RAM, and service settings `OLLAMA_HOST=0.0.0.0:11434`, `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=1`. Do not expose it publicly.
4. Set API `OLLAMA_BASE_URL` to the provider's exact private Ollama hostname, including port 11434. Container localhost cannot reach a separate container.
5. In the Ollama runtime shell, pull both models. In the API runtime shell run `python ingest.py` using its mounted volume. Do not ingest in an image build: for example, Render disks are only available at runtime.
6. Restart API and test via HTTPS. If your plan lacks RAM, a runtime shell, persistence or sufficient request timeout, use the VPS recipe.

### 11C. Point the frontend to hosting

Set `mobile/.env` to:

```dotenv
EXPO_PUBLIC_API_URL=https://api.yourdomain.com
```

Restart Metro. For EAS builds set this value in that profile's EAS environment. Do not append `/api/chat`; the service code appends paths. Hosted preview/production builds require HTTPS.

## 12. Build an installable APK with EAS

Run from **mobile**. Cloud EAS builds need no local Android Studio or GPU.

1. Verify:

   ```powershell
   npm ci
   npx expo-doctor
   npm run typecheck
   npm run lint
   ```

2. Sign into your **Expo developer account**, not an in-app account:

   ```powershell
   npx eas-cli@latest login
   npx eas-cli@latest init
   npx eas-cli@latest build:configure
   ```

3. If dynamic config cannot be updated automatically, insert the actual EAS project ID under `expo` in `app.json`:

   ```json
   "extra": { "eas": { "projectId": "THE-REAL-UUID-FROM-EAS" } }
   ```

   This is an insertion fragment, not the complete file. Do not use that placeholder as an ID. The included `app.config.ts` preserves `config.extra` and therefore your EAS project ID.
4. Build a **standalone hosted APK**:

   ```powershell
   npx eas-cli@latest env:set --name EXPO_PUBLIC_API_URL --value https://api.yourdomain.com --environment preview --visibility plaintext
   npx eas-cli@latest build --platform android --profile preview
   ```

   You may instead set the variable in Expo dashboard's preview environment. Ignored local `.env` files are normally not uploaded. Allow EAS to manage an Android signing key unless you already have one.
5. Build a **standalone LAN APK**:

   ```powershell
   npx eas-cli@latest env:set --name EXPO_PUBLIC_API_URL --value http://192.168.1.5:8000 --environment development --visibility plaintext
   npx eas-cli@latest build --platform android --profile lan
   ```

   Use your real laptop IP. `lan` permits HTTP and embeds JS, so Metro is unnecessary. Keep backend/Ollama running on the same network. Do not use the HTTP profile for public hosting.
6. For an APK development client:

   ```powershell
   npx eas-cli@latest build --platform android --profile development
   npx expo start --dev-client --lan --clear
   ```

7. Download the completed `.apk` from the EAS build page to your Android phone. Permit installation from that source when prompted, install, open and run the acceptance checks.
8. `production` creates an **AAB** for store submission, not an APK for direct installation. Use preview or lan for installable APKs.

The full ready-to-use `app.json`, `app.config.ts` and `eas.json` are in the project and code listing.

| Profile | Output | API transport | Metro? |
|---|---|---|---|
| development | Development-client APK | Local HTTP allowed | Yes |
| lan | Standalone APK | Local HTTP allowed | No |
| preview | Standalone APK | HTTPS | No |
| production | Store AAB | HTTPS | No |

## 13. Troubleshooting

| Error | Fix |
|---|---|
| `ModuleNotFoundError: app` | Start Uvicorn from backend using that environment's Python |
| Missing Chroma/package | Install requirements into the same Python environment |
| PowerShell activation blocked | Use `\.venv\Scripts\python.exe` directly |
| Ollama model not found | Pull both exact model names, check `ollama list` |
| Empty `ollama ps` | Normal when idle/unloaded; list checks installed models |
| Port 11434 in use | Desktop Ollama may already be serving; don't launch a second instance |
| Very slow/out of memory | Close heavy apps; use small defaults, real phone, more RAM/hosted compute |
| Missing/stale index | Ingest from backend, then restart API |
| Groq key/quota/model error | Replace server key and restart; check account access/model availability |
| Phone cannot reach backend | Check `/health` in phone browser, private Wi-Fi/IP/firewall, bind `0.0.0.0` |
| Works on laptop only | Do not use localhost/127.0.0.1 in the phone API URL |
| HTTP blocked in APK | Use LAN profile locally or HTTPS for hosted builds; rebuild after native config changes |
| EAS build lacks API URL | Set `EXPO_PUBLIC_API_URL` in the profile's EAS environment |
| Expo Go SDK mismatch | Use compatible SDK 57 Go or development APK, not arbitrary package downgrades |
| Microphone denied | Grant OS microphone permission |
| Missing Hindi/Marathi audio | Install the relevant TTS voice; check volume/silent mode |
| Old Google module error | Apply deletions, run `npm ci`, clear Metro, rebuild old development client |
| EAS ownership/project error | Use the correct Expo account and actual `extra.eas.projectId` |
| APK update will not install | Signing/package mismatch: use the same key, or uninstall old test app (clears its data) |
| Download is AAB | Build preview/lan instead of production |
| Hosting times out | Check proxy/service timeouts; use faster inference or the VPS recipe |

## 14. Validation and limits

See `VALIDATION.md` for exact results. Automated checks use real corpus parsing and real persistent Chroma, but mock model/provider responses where credentials/models are absent. They do not establish an LLM's legal accuracy.

Windows installation, full-corpus Ollama vector generation, real Groq guidance/transcription, an EAS native APK build, and physical phone microphone/speaker/dialler behavior still need your equipment/account. No signed APK or deployed service is claimed.

The legal corpus was not updated or comprehensively legally audited. Some source files are OCR extractions/summaries; outdated law and translation mistakes remain possible. Results are potentially relevant provisions, not definitive legal opinions. Contacts are curated, not freshly searched on every app request.

## 15. Official references checked

- Expo SDK 57: <https://docs.expo.dev/versions/v57.0.0/>
- Audio: <https://docs.expo.dev/versions/v57.0.0/sdk/audio/>
- Speech: <https://docs.expo.dev/versions/v57.0.0/sdk/speech/>
- APK builds: <https://docs.expo.dev/build-reference/apk/>
- EAS variables: <https://docs.expo.dev/eas/environment-variables/>
- Build properties: <https://docs.expo.dev/versions/v57.0.0/sdk/build-properties/>
- Ollama Windows: <https://docs.ollama.com/windows>
- Ollama APIs: <https://docs.ollama.com/api/embed>, <https://docs.ollama.com/api/chat>
- Models: <https://ollama.com/library/nomic-embed-text>, <https://ollama.com/library/qwen2.5:1.5b>
- Ollama Docker: <https://docs.ollama.com/docker>
- Chroma supplied embeddings: <https://docs.trychroma.com/docs/collections/add-data>
- Groq: <https://console.groq.com/docs/speech-to-text>, <https://console.groq.com/docs/models>
- Render disks: <https://render.com/docs/disks>
- Railway volumes: <https://docs.railway.com/volumes>
- Maharashtra ACB: <https://acb.maharashtra.gov.in/>
- NALSA: <https://nalsa.gov.in/>
- Emergency response: <https://www.mha.gov.in/en/commoncontent/emergency-response-support-system-erss>
- Cybercrime: <https://cybercrime.gov.in/>, <https://i4c.mha.gov.in/>
- Consumer helpline: <https://consumerhelpline.gov.in/>
- CVC jurisdiction notice: <https://portal.cvc.gov.in/login?loginType=complainant>

Recheck official docs when upgrading tools/models or choosing a hosting plan.
