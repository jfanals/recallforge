# Local audio production pipeline

## 1. Author before generating

Write a brief and lesson JSON, validate it, then render a handful of representative sentences. Choose examples containing questions, contractions, grammatical endings, unfamiliar names, and quiet final consonants. A 90-second voice pilot is much cheaper to review than a full course. The included `examples/author_studio.py` demonstrates a tiny Python authoring DSL (`section`, `say`, `en`, `ask`, `repeat`); it regenerates only `examples/studio-pt-en.json`. Arbitrary lessons can be authored directly as JSON—do not run that example generator expecting it to write your course.

## 2. Separate language pipelines

The production path is Kokoro 0.9.4 → Misaki → PyTorch → mono PCM at 24 kHz. Use separate `KPipeline` instances for each language; reuse the underlying model object to avoid redundant model allocation. In the original pilot:

- `KPipeline(lang_code='p')` + `pf_dora`: Brazilian Portuguese narration, speed 1.0.
- `KPipeline(lang_code='a')` + `af_bella`: American English examples/questions, speed 0.95.
- The same English pipeline + `am_adam`: second dialogue speaker, speed 0.95.

Synthesize one utterance per segment. Kokoro may yield multiple chunks internally; concatenate them in order. Never interleave two languages into a single pipeline or splice words/phonemes to repair pronunciation. A voice ID must really exist in the upstream model; prefix validation is only a first check.

## 3. Cache speech, not lesson structure

Cache keys include model ID, language, voice, text, synthesis speed, processing revision, and recorded package versions. They deliberately exclude chapter, prompt type, and gap duration: changing a speaking window should not regenerate speech. When changing trim/fade behavior, increment the processing revision in `scripts/lesson.py`. If provisioning a different model snapshot under the same model ID, use a new `--cache` directory: this tool does not hash every downloaded asset.

```sh
python scripts/render.py workspace/lesson-01.json \
  --output output/lesson-01-v1 --cache build/clips
```

Completed cache writes use a temporary WAV then atomic replacement. Treat one cache as single-writer; concurrent renders using it are not supported. An invalid cache fails closed rather than silently entering the final audio. Delete only the bad clip and rerun into a fresh output folder. Each output copies the needed clips, so moving a completed bundle does not depend on the original cache location.

## 4. Preserve speech edges

The revised process detects activity at absolute amplitude 0.001, preserves up to 80ms before and 200ms after activity, and applies 5ms ramps at the preserved boundaries. This is conservative edge processing, not a universal speech endpoint detector. Near-threshold consonants and breaths may still need listening review. If your language/voice clips endings, retain the full generated waveform or increase padding; do not blindly raise the threshold.

A 5ms ramp is not a license to fade out a consonant. Never delete an apparent “extra sound” without confirming it is not part of the language. The validator and audit check finite non-silent waveforms, format, exact assembly, silence, and edges—not phonetic correctness.

## 5. Sample-counted assembly

For each clip:

```text
speech_samples = actual PCM length
pause_samples = round(gap_after_seconds × 24000)
next_start = current_start + speech_samples + pause_samples
```

The assembler streams speech and explicit zero arrays to `lesson.wav` rather than keeping an entire course in RAM. Timeline times derive from these integer counts, preventing accumulated float/rounding drift. Quiet tails inside a clip are part of `speech_samples`; response silence follows them in full.

## 6. Encode without destroying speaking time

FFmpeg exports:

- MP3: libmp3lame, 128 kb/s, 24 kHz.
- M4A: AAC, 128 kb/s, 24 kHz, FFmetadata chapters in millisecond time base.
- Both use `loudnorm=I=-18:TP=-2:LRA=11` as a practical starting target.

This is single-pass normalization, not certified two-pass broadcast loudness compliance. ffprobe verifies output codec, duration within 0.3s, and M4A chapter count. Chapters may not display in every player. No silence-removal, time compression, sentence overlap, or post-hoc speed-up is applied. ffmpeg's license/build and codec distribution obligations are separate from this toolkit's MIT license.

## 7. Pronunciation debugging: what actually happened

A listener reported an apparent extra final consonant in “What are you working on?” in the original pilot. Investigation separated several possible causes:

1. Wrong script? The text was correct.
2. Overlap? The clip had five seconds of separate silence after it; no next sentence overlapped.
3. Hard splice? Boundary samples were already near zero.
4. Phonemizer? Generated phonemes ended in /n/, not an intended /nd/ sequence.
5. Synthesis/voice? The raw synthesized tail had high-frequency release energy; changing the female English voice was more effective than only slowing it down.

The pilot moved from `af_heart` at speed 1.0 to `af_bella` at 0.95, preserved longer quiet edges, added short ramps, and rerendered all affected female English utterances. Both English voices used 0.95 afterward. This is an observed case, not a claim that one voice is universally best.

For a new defect, save the exact phrase, timestamp, model/voice/speed and package versions. Compare raw clip versus assembled WAV versus encoded audio. Generate controlled alternatives changing only one variable at a time: voice, speed, or natural rewording while preserving the teaching goal. Keep correct question punctuation. Compare at matched loudness with a pause and neutral labels. Optional NumPy FFT/matplotlib spectrograms help locate energy, but cannot identify a phoneme with certainty. ASR can recognize the intended sentence while overlooking the perceptual problem. Human comparison listening remains required.

## 8. Optional interactive player

The earlier repository contains a dependency-free HTML/CSS/JavaScript player with repeat, next/previous, chapter navigation, hideable current-line text, independent sentence/response pauses, immediate adjustment of the current gap, and frozen pause countdown when playback is paused. Source: https://github.com/jfanals/learn-english

Its `site/lesson.json` is a dedicated web manifest with relative compressed clip URLs. This toolkit's timeline is **not drop-in compatible**. If adapting it, inspect its `scripts/export_site.py`, `site/player.js`, and tests. Create an explicit adapter: convert unique WAVs to compressed clips, map segment timing/kinds and chapter boundaries to that manifest, copy only public assets, and run the player tests. Keep expected answers/variants private if they are not intended in the UI. Validate asset URLs under a project subpath, mobile layout, autoplay restrictions, and race conditions. A web player is optional; it is not needed to generate or play the MP3/M4A. Background and locked-screen browser playback may be unreliable.

## Upstream references

- Kokoro library/setup: https://github.com/hexgrad/kokoro
- Model and voice terms/inventory: https://huggingface.co/hexgrad/Kokoro-82M
- Phonemization: https://github.com/hexgrad/misaki
- Optional ASR API: https://github.com/istupakov/onnx-asr
- FFmpeg filters: https://ffmpeg.org/ffmpeg-filters.html#loudnorm
- ffprobe: https://ffmpeg.org/ffprobe.html
