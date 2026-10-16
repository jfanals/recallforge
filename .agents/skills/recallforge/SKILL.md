---
name: recallforge
description: Create original local audio language courses using bilingual prompts, active recall, sentence building, speaking windows, Kokoro voices, MP3 and chaptered M4A exports. Use for course design, local speech synthesis, lesson JSON authoring, pronunciation debugging, and course QA.
license: MIT
compatibility: A coding agent with filesystem and terminal access; Python 3.11 or 3.12 recommended, FFmpeg/ffprobe, eSpeak NG, and downloadable Kokoro dependencies for rendering.
---

# RecallForge: local audio course creation

## Locate the toolkit

This skill belongs to the RecallForge repository. Resolve paths relative to this file: repository root is `../../..` from this skill directory. All commands below run from that root. Keep the whole checkout together; copying only this Markdown loses its references and executable tools. No agent orchestration framework or cloud speech API is needed.

Read these references when relevant:

- Before writing lessons: `../../../docs/course-design.md` and `../../../docs/lesson-format.md`.
- Before installing/rendering: `../../../docs/setup.md` and `../../../docs/audio-pipeline.md`.
- Before delivering: `../../../docs/quality-assurance.md`.
- For provenance/rights: `../../../docs/provenance.md`.
- If a word sounds wrong, clipped, or has an extra consonant: read the pronunciation-debugging section in `../../../docs/audio-pipeline.md` before changing trims or repeatedly inspecting waveforms.

## Workflow

1. **Intake.** Ask instruction/target language and dialect, ability, concrete situations, length, OS/hardware, voice preferences, and privacy/sharing constraints. Do not infer a formal proficiency level. Verify TTS language/voice availability before promising a course.
2. **Plan visibly.** Write `workspace/brief.md` and `workspace/course-map.md`. Choose a small set of communicative frames, review opportunities, transfer task, recall check, and delayed retrieval prompt. Start with a short pilot, not 30 generated lessons.
3. **Author original material.** Use `lesson.schema.json` and `examples/quickstart.json`. The full `examples/studio-pt-en.json` and `examples/author_studio.py` show a ten-chapter lesson and lightweight authoring helpers. Do not translate/paraphrase a commercial course or reuse its script progression.
4. **Distinguish turns.** A recall/assessment prompt is followed by real silence then a separate confirmation. `repeat_model` is imitation after hearing the model. Personal turns need no fixed answer. Metadata answers are not spoken automatically.
5. **Validate.** Run `python scripts/lesson.py workspace/lesson-01.json` and `python -m unittest discover -s tests -v`. Check cue/answer truth yourself; structural validation cannot do that.
6. **Provision deliberately.** Explain system/package/model downloads and follow setup instructions. Use a virtual environment. Never embed tokens, private application paths, or downloaded model weights in lessons or commits.
7. **Test voices.** Render representative short native-language utterances first. Use distinct language pipelines, matching voice prefixes, and actual upstream voice names. Worked PT-BR/US-English voices are `pf_dora`, `af_bella`, `am_adam`; speed 1.0 for PT-BR and 0.95 for English. These are starting points, not universal best choices.
8. **Render a revision.** `python scripts/render.py workspace/lesson-01.json --output output/lesson-01-v1`. Keep cache single-writer; never mix output revisions. Do not remove/shorten silence to make the file more compact. New model snapshots require a new cache directory.
9. **Audit.** `python scripts/audit.py output/lesson-01-v1`. Optional local ASR: `python scripts/check_speech.py output/lesson-01-v1 --languages en-US pt-BR` after installing ASR dependencies. Check skipped clips and language coverage. Read actual reports.
10. **Listen and evaluate.** Request human review of the full pilot, especially difficult endings, questions and response windows. Keep timestamped listening evidence. Automated checks/ASR/FFT never establish perfect pronunciation. If no listener reviewed it, explicitly say so.
11. **Deliver and iterate.** Return MP3/M4A paths, timed script, report paths, learner instructions, review limitations and feedback questions. Ask for difficulty, pause comfort, recall before the model, and next-day retrieval. Revise before expanding the course. Publish only with permission after privacy/rights review.

## Golden example

A valid prompt-answer pair (inside a lesson's `segments`):

```json
[
  {"id":"s001","chapter":"01 · Recall","kind":"recall_prompt","language":"pt-BR","voice":"pf_dora","text":"Peça um café com educação.","gap_after_seconds":6,"expected_answer":"Can I have a coffee, please?"},
  {"id":"s002","chapter":"01 · Recall","kind":"confirmation","language":"en-US","voice":"af_bella","text":"Can I have a coffee, please?","gap_after_seconds":0.8}
]
```

Use ~0.6s narration separation, ~0.8s model separation, ~4–8s short production windows, and ~15–30s personal turns as pilot defaults. Adapt to complexity and learner feedback. Do not mistake in-session imitation for retention.

## Output contract and boundaries

- A complete render includes lossless WAV, MP3, chaptered M4A, portable clips, source lesson, sample-accurate timeline, timed script, and render report.
- Preserve full utterances and quiet tails. Do not cut suspected consonants to fix a voice artifact; compare raw/assembled/encoded speech, then controlled re-synthesis.
- Cache keys distinguish voice/text/language/speed/dependency/edge revisions, not pauses. Audit exact silence in WAV, not lossy audio.
- Browser interaction is optional. The linked public player uses a different manifest; write/test an adapter rather than dropping a timeline into it.
- No microphone access, automatic learner scoring, voice cloning, commercial-course copying, or automatic publishing. Local-first still requires first-run model/language provisioning.
