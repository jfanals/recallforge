# Lesson and render formats

## Canonical source

`lesson.schema.json` is JSON Schema Draft 2020-12 for editor/tool integration. `scripts/lesson.py` is a dependency-free operational validator: it also checks semantic constraints JSON Schema does not express here (unique IDs, contiguous chapters, voice/language prefix, immediate confirmation after scored prompts). Run the CLI even if your editor accepts the schema. Extra metadata is allowed for extension; it is not automatically narrated or scored.

Required top-level fields: `title`, `source` (rights/provenance statement), `narrator_language`, `target_language`, `segments`. Optional: `version`, `goals`, `level`, and project-specific curriculum metadata. Author genuine text in UTF-8, not phonetic English substitutes for another language.

```json
{
  "title": "A useful request",
  "source": "Original authored lesson",
  "narrator_language": "pt-BR",
  "target_language": "en-US",
  "segments": [
    {"id":"s001","chapter":"01 · Recall","kind":"recall_prompt","language":"pt-BR","voice":"pf_dora","text":"Peça um café com educação.","gap_after_seconds":6,"expected_answer":"Can I have a coffee, please?"},
    {"id":"s002","chapter":"01 · Recall","kind":"confirmation","language":"en-US","voice":"af_bella","text":"Can I have a coffee, please?","gap_after_seconds":0.8}
  ]
}
```

## Segment fields

| Field | Meaning |
|---|---|
| `id` | Unique nonempty stable identifier; not used as a file path |
| `chapter` | Nonempty title; adjacent equal titles form one M4A chapter |
| `kind` | Turn type from the list below |
| `language` | Exact key from the supported map below |
| `voice` | Actual Kokoro voice matching the language prefix |
| `text` | Spoken text only, 1–1000 characters; split long narration |
| `gap_after_seconds` | Explicit silence after the utterance, 0–120 seconds |
| `speed` | Optional synthesis speed 0.5–2; English defaults to 0.95, others 1.0 |
| `expected_answer` | Required nonempty model answer for recall/assessment prompts |
| `acceptable_variants` | Optional list of acceptable answer strings; metadata only |

`kind` values:

- `instruction`: guidance/explanation.
- `dialogue`: preview or conversation example.
- `model`: listening example without a retrieval requirement.
- `repeat_model`: model first, learner repeats in the following gap.
- `recall_prompt`: cue first, learner answers before the next `confirmation`.
- `assessment_prompt`: unassisted check; same immediate confirmation requirement.
- `confirmation`: model answer after the speaking window.
- `free_response_prompt`: personal/open-ended turn; no fixed answer required.

Chapters must be contiguous: A → B → A is rejected. The validator checks language prefixes, not the existence of every voice. It does not enforce pedagogical truth: an agent must still check that cue, answer, variants, language, and context actually agree. Nonempty strings containing only whitespace are rejected by the CLI.

## Kokoro language mapping

| Lesson language | Pipeline code / voice prefix | Notes |
|---|---|---|
| `en-US` | `a` | Worked voices `af_bella`, `am_adam` |
| `en-GB` | `b` | Select an actual British voice |
| `es` | `e` | Check upstream voice/dialect support |
| `fr-FR` | `f` | Validate native pronunciation |
| `hi` | `h` | Validate native pronunciation |
| `it` | `i` | Validate native pronunciation |
| `ja` | `j` | Requires Misaki Japanese extras |
| `pt-BR` | `p` | Worked narrator `pf_dora` |
| `zh-CN` | `z` | Requires Misaki Chinese extras |

Upstream voice inventory: https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md

If a desired language is absent, do not silently route it through English. Replace/add a TTS backend, preserve the segment/timeline contract, and test it. `narrator_language` and `target_language` describe the lesson; synthesis routes using each segment's language.

## Rendered bundle

`timeline.json` adds `sample_rate_hz`, `duration_seconds`, a chapter list, and per-segment fields:

- `start_sample`, `speech_samples`, `gap_samples`, `end_sample` (integer canonical timing).
- `start_seconds`, `speech_end_seconds`, `end_seconds`, `speech_duration_seconds` (derived convenience values).
- `clip`: portable path under `clips/`, relative to the output folder.

All clips and the raw assembled WAV are mono 24 kHz PCM16. Encoded MP3/AAC can introduce small encoder padding; ffprobe tolerance is 0.3s. Never reconstruct exact silence checks from lossy MP3. `script.md` is a post-attempt transcript, not a substitute for audio practice.

`render-report.json` records package versions, model identifier, edge revision, duration breakdown, counts, peak, codec/duration verification, and `human_listening_review: false`. Keep human review evidence in a separate `listening-review.md`; do not turn the flag true merely because automated tests passed. Exact bit-level reproducibility is not promised: model snapshots, NLP assets, hardware, and library versions matter.
