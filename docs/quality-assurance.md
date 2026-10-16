# Quality gates and release checklist

## Gate 1 — Content and rights

Confirm the learner brief and communicative goal. Review cue/answer agreement, grammatical correctness, dialect, culturally appropriate wording, plausible scenario, acceptable variants, limited new material, review opportunities, transfer, and an unassisted check. A valid JSON file can still contain a bad lesson. Ensure authorship/permission for every script and voice; no commercial audio/transcripts or private learner data in public outputs.

## Gate 2 — Structural validation

```sh
python scripts/lesson.py workspace/lesson-01.json
python -m unittest discover -s tests -v
```

Checks cover required fields, unique IDs, finite bounded gaps/speeds, supported language map, voice prefix, contiguous chapters, and immediate confirmation after recall/assessment prompts. The tests also cover cache invalidation, exact sample timing, metadata escaping, and normalization behavior. CI runs dependency-free unit tests plus a separate synthetic-audio integration job (NumPy, SoundFile, FFmpeg), including encoding, auditing and detecting a corrupted pause. No model is downloaded in CI; synthetic tones do not test speech synthesis. Audio tests skip locally when optional dependencies/binaries are absent.

## Gate 3 — Render integrity

```sh
python scripts/render.py workspace/lesson-01.json --output output/lesson-01-v1
python scripts/audit.py output/lesson-01-v1
```

The renderer checks clip shape/rate/finite signal, export codec, duration, and chapter count. The auditor checks source/render correspondence, every timeline boundary, exact zero response windows in the lossless WAV, exact clip/assembled speech agreement, total WAV length, contained relative clip paths, and near-zero edge samples. Machine-readable reports stay alongside the audio.

Audit success does not prove natural pronunciation, pedagogical value, or safety of untrusted model files. Run the scripts on your own generated bundles, not arbitrary hostile artifacts. Optional external schema validation can use `jsonschema` or an editor configured with `lesson.schema.json`.

## Gate 4 — Optional ASR smoke test

```sh
python scripts/check_speech.py output/lesson-01-v1 --languages en-US pt-BR
```

Parakeet v3/ONNX back-transcribes unique eligible clips. FFmpeg converts input to mono float32 at 16 kHz. The report compares normalized token sequences (case/punctuation and a small contraction map) with `difflib.SequenceMatcher`, flagging scores below 0.9. This ratio is not word-error rate or a phonetic metric. The script produces review candidates, not an automatic pass/fail certification; inspect the actual texts, supported languages, and skipped clips. Short samples are preferred; utterances over 20s are recorded as skipped.

ASR may hallucinate over silence, miss a subtle extra consonant, normalize an error, or transcribe correct speech incorrectly. Lack of disagreement is weak evidence, not a reason to skip listening. Do not send learner recordings to a cloud ASR without permission; this workflow uses local model inference.

## Gate 5 — Human listening

Listen to the entire pilot, especially changed clips, grammatical endings, questions, names, longest phrases, bilingual transitions, silence windows, and codec outputs. Where possible, use a proficient/native target-language reviewer. Check the speaking windows by actually answering. Listen on ordinary headphones/speakers and at least one intended playback device.

Keep `listening-review.md` beside the bundle with reviewer, date, file/revision, reviewed scope, timestamped issues, and decisions. If nobody listened, write **not performed**. Do not claim “pronunciation verified” from an FFT, ASR match, or successful export. Correct voice artifacts by controlled re-synthesis rather than surgically deleting consonants.

## Gate 6 — Learner feedback and delayed retrieval

Record subjective difficulty, timestamps needing longer pauses, how many recall answers preceded the model, and which frames failed the next-day check. Keep this private by default. Revise a small amount, regenerate into `output/lesson-01-v2`, and compare. The same cache reuses unchanged speech; changed voice/text/speed/edge revision produces new keys. New model snapshots require a separate cache.

## Publishing

- Validate JSON, run tests, render, audit, and inspect reports.
- Explicitly state whether ASR and listening were performed and on which revision.
- Distribute audio, chapters, a post-attempt script, learning goals, usage instructions, and limitations.
- Review `git status --ignored` and staged diff; no tokens, private paths, model weights, commercial sources, or learner recordings.
- Generated bundles are ignored intentionally. Publish only selected reviewed outputs, for example as a release, with explicit permission and relevant attribution.
- Verify all links/downloads and keep the course's version distinct from toolkit version.

## Evidence in this repository

Both the new quickstart and the full studio lesson were actually synthesized locally with this generalized toolkit; their MP3/M4A exports were probed and their WAV bundles audited. Optional local ASR was also run on the quickstart, flagging two Portuguese clips for listening review. Generated audio is not committed. No human listening review is claimed. Unit tests run independently of the model stack. See [verification](verification.md) for measured results and the distinction from the historical pilot.
