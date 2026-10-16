# RecallForge

**Turn a learning goal into an original, local-first, audio language course—with your coding agent.**

RecallForge is a recipe, a portable agent skill, a structured lesson format, and working Python tools. Author short bilingual lessons, synthesize them locally, insert real speaking windows, and export MP3 plus chaptered M4A. No paid speech API, hosted application, microphone access, or agent framework required.

> Not a commercial-course copier. Write original scenarios and wording. Active recall, oral production, spaced review, and sentence building are general teaching techniques—not permission to reproduce somebody else's scripts or recordings.

## Give this to your agent

Clone this repository and ask:

> Read `AGENTS.md` and `.agents/skills/recallforge/SKILL.md`. Help me create an original audio-first language course. Ask about my languages, level, goals, preferred situations, session length, and computer. Start with a short voice/lesson pilot, validate the JSON, synthesize locally, audit the result, and give me the audio and timed script. Do not claim human listening review or publish my personal material without permission.

Or start with the [copy/paste prompts](docs/agent-prompts.md). The skill is plain Markdown: agents without skill discovery can read it directly. Keep this whole repository together; the skill references its scripts and documentation. For Pi and other compatible agents, `.agents/skills/recallforge/` is a project skill location. Restart/reload the agent after cloning if necessary.

## First audio

Recommended: Python 3.11 or 3.12; CPU is sufficient. Install FFmpeg (including ffprobe) and eSpeak NG using your OS package manager. Full platform instructions and download/offline caveats: [setup](docs/setup.md).

```sh
git clone https://github.com/jfanals/recallforge.git
cd recallforge
python3 -m venv .venv
# macOS/Linux; on Windows: .venv\Scripts\Activate.ps1
source .venv/bin/activate
python -m pip install -r requirements.txt

# Validation needs only Python's standard library:
python scripts/lesson.py examples/quickstart.json
python -m unittest discover -s tests -v

# First render downloads model/voice assets; inference runs on your computer.
python scripts/render.py examples/quickstart.json --output output/coffee-v1
python scripts/audit.py output/coffee-v1
```

Open `output/coffee-v1/lesson.mp3` or `lesson.m4a` in your usual audio player. The quickstart is about 90 seconds, intentionally too short to demonstrate long-term spacing. For a complete worked lesson, render `examples/studio-pt-en.json` instead (approximately 16 minutes; synthesis-dependent).

## What's included

| File | Purpose |
|---|---|
| [Agent skill](.agents/skills/recallforge/SKILL.md) | Ordered workflow, quality gates, and reference map |
| [Course design](docs/course-design.md) | Intake, curriculum, prompts, speaking windows, transfer, assessment |
| [Audio pipeline](docs/audio-pipeline.md) | Libraries, processing, caching, encoding, pronunciation repairs |
| [Lesson format](docs/lesson-format.md) / [JSON Schema](lesson.schema.json) | Agent-readable authoring contract |
| [Setup](docs/setup.md) | macOS/Linux/Windows, CPU, model provisioning, optional ASR |
| [Quality assurance](docs/quality-assurance.md) | Structural/audio/ASR/listening checks and regression workflow |
| [Provenance](docs/provenance.md) | What came from the original experiment and what changed |
| `examples/quickstart.json` | Small PT-BR → English coffee lesson |
| `examples/studio-pt-en.json` | Full original 156-segment, 10-chapter lesson |
| `examples/author_studio.py` | Editable Python authoring DSL that regenerates the full example |
| `scripts/lesson.py` | Dependency-free validator and timing/cache helpers |
| `scripts/render.py` | Kokoro → cached clips → silence → WAV, MP3, chaptered M4A |
| `scripts/audit.py` | Exact timeline/assembly/silence/edge checks |
| `scripts/check_speech.py` | Optional Parakeet/ONNX local back-transcription |

## Outputs and architecture

```text
learner brief → course map → original lesson.json → validation
  → Kokoro/Misaki/PyTorch → 24 kHz mono utterance cache
  → explicit sample-counted silence → streaming WAV assembly
  → FFmpeg loudness normalization → MP3 + chaptered M4A
  → timeline + timed script + machine-readable reports
  → automated checks + human listening + learner feedback → revision
```

Each render creates a portable bundle with `lesson.json`, `lesson.wav`, `lesson.mp3`, `lesson.m4a`, `clips/*.wav`, `timeline.json`, `script.md`, `chapters.ffmetadata`, and `render-report.json`. Auditing adds `audit.json`; optional ASR adds `speech-check.json`. Clip paths are relative; private machine paths are not embedded. Output folders must be new/empty to avoid mixing revisions. Speech is cached independently of pause lengths.

## Scope and limitations

- The original tested pairing is Brazilian Portuguese guidance + American English (`pf_dora`, `af_bella`, `am_adam`). The renderer also maps other Kokoro languages, but quality/voice availability must be validated per language. Not an arbitrary-language guarantee.
- Local-first does not mean zero setup downloads. Model/voice/language assets must be provisioned before offline use. Hardware speed varies; no GPU is required and none is promised.
- TTS can mispronounce words or add perceptual artifacts. ASR agreement and waveform checks cannot replace listening. Generated lessons are provisional until reviewed.
- This is a toolkit, not a proven curriculum, CEFR diagnosis, learner-scoring engine, or spaced-repetition scheduler. Your agent authors the content; scripts do not generate a sound curriculum automatically.
- The browser-based player is a separate published example: [English, in rhythm](https://jfanals.github.io/learn-english/) / [source](https://github.com/jfanals/learn-english). See the audio pipeline guide before adapting it; this toolkit's timeline is not its manifest.

## License and privacy

Toolkit code, documentation, and original example text: [MIT](LICENSE). Third-party models, voices, phonemizers, Python packages, and codecs retain their own licenses; review their upstream terms before redistributing dependencies or audio. Weights are not included. No commercial recordings, transcripts, source-derived analysis, personal learner recordings, or local application model paths are shipped.

`output/`, `build/`, environments, secrets, and learner workspace files are ignored by Git. Review files before sharing them. Audio is never recorded or uploaded by these scripts; first-run package/model download services can still observe requests.
