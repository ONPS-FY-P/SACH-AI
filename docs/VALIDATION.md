# Validation record

Validation performed in the provided Linux workspace using Python 3.12.14 and Node 24.19.0. The target user's Windows laptop/phone was not connected.

## Completed

- **38 backend tests passed.** Covers all 11 actual datasets, source IDs/quote rejection, inferred-section safeguards, input validation, three-language request routing, fake-key refusal, voice upload forwarding, empty/invalid/oversized audio, rate limiting, missing/stale index handling, persistence and ingestion resume/failed-build behavior.
- Real Chroma persistence/readback is exercised on temporary fixture collections. External Ollama/Groq responses in tests are mocked. No fake test vectors are packaged as a real corpus index.
- Corpus parsing audit: **3,020 chunks** from 11 supplied JSON files, with ambiguity warnings preserved in `DATA_AUDIT.md`.
- Python dependency check: no broken requirements.
- TypeScript typecheck passed.
- ESLint passed.
- Expo dependency compatibility check passed.
- Expo SDK 57 public config resolved with no Google sign-in plugin.
- Android JavaScript/Hermes bundle export succeeded (1,349 modules on the initial export). This is not a signed APK/native build.
- Byte comparisons: all raw datasets and image assets unchanged; shared theme, portal/emergency screens, tab/root layouts, directory/translations and link helpers unchanged. Chat/header StyleSheet definitions identical.
- Runtime auth implementation and Google sign-in dependency/config removed. Auth route probes return 404; unauthenticated chat routing is tested.
- Archive integrity checked before delivery.

Expo Doctor initially identified missing direct peer dependencies `expo-font` and `expo-asset` in the original project. SDK-compatible versions and their config plugins were added. **Final Expo Doctor: 21/21 checks passed**, followed by successful final public-config resolution. TypeScript and lint were rerun after the dependency fixes and passed.

## Requires your hardware/account

- Actual installation on Windows/i3, available RAM and performance measurement.
- Pulling Ollama models and generating all real corpus embeddings.
- Real Groq key validation, guidance generation and audio transcription.
- LLM retrieval accuracy and quality in English/Hindi/Marathi.
- Microphone permissions, recording, TTS voice installation, playback/stop, OS dialler/link behavior on an actual phone.
- EAS native compilation/signing/installation and hosting/HTTPS validation.

Use `scripts/smoke_test.py` and the numbered device checks in the setup guide. A source quote can be genuine while an explanation is still wrong; test legal meaning as well as response shape. No end-to-end success or legal correctness is claimed without those checks.
