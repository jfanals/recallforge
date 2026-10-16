# Provenance and boundaries

## The original experiment

RecallForge extracts the reusable production knowledge behind [English, in rhythm](https://github.com/jfanals/learn-english), an original Portuguese-guided American English practice lesson about everyday situations and music production. The public player remains in that separate repository; RecallForge focuses on making new courses.

The original revised lesson had:

- 156 segments and 99 distinct synthesized clips.
- 10 chapters, 43 response prompts (including a personal turn), and nine final recall items.
- Approximately 939.716s total: 442.716s speech including preserved tails, plus 497s explicit silence.
- `pf_dora`, `af_bella`, and `am_adam`; English synthesis speed 0.95.
- MP3, chaptered M4A, raw WAV, a timeline, script, render report, speech back-check and edge/tail investigation.
- Local Parakeet v3 int8 ONNX recognition of 31 unique English clips and six Portuguese samples in the original QA run.
- A reported pronunciation-tail issue investigated with text/phonemes, waveform/spectrum, controlled voice alternatives, and ASR. This was not a human listening certification.

Durations and counts describe that historical render, not guaranteed results on a different environment. Model inference is not promised to be bit-identical.

## What was carried forward

- The complete original authored lesson JSON and its small Python authoring DSL.
- Language-separated Kokoro inference, conservative edge handling, content-addressed clips, explicit learner silence, MP3/M4A chapter export, and ffprobe checks.
- Method documentation for prompt → speaking window → model, scaffolded sentence construction, review, transfer, guided conversation, recall, and learner feedback.
- Practical QA boundaries and the voice-tail debugging lessons.

## What was generalized here

The CLI now accepts arbitrary lesson and output paths rather than a hardcoded pilot filename, validates before synthesis, enforces coherent structural rules, uses integer-sample timing and streaming assembly, copies relative clip assets into a portable bundle, rejects nonempty output folders, escapes chapter metadata, records dependency versions in cache keys/reports, and provides reusable integrity/ASR tools without a private application model directory. The previous pilot-specific 10–16 minute assertion was removed: short voice pilots and longer lessons can use the same tools.

The new quickstart is original example content created for this toolkit. New scripts are adapted from the production approach rather than exact archival copies of every original tool. Historical spectral heuristics dependent on a particular old cache are documented, not shipped as a universal pronunciation detector.

## What is deliberately absent

Commercial lesson recordings, transcripts, source-derived analyses/measurements, local session history, machine-specific paths, downloaded tools or model weights, learner recordings, synthesis caches, generated WAVs, and original private investigation artifacts. No source commercial recording is required or used by the rendering workflow. General learning techniques are discussed without reproducing commercial scripts or claiming affiliation with a branded method.

The earlier browser player/exporter is linked, not duplicated. FluidAudio/other local analysis tooling explored during the earlier project is not a required production dependency. The reproducible path documented here uses Kokoro, NumPy, SoundFile, PyTorch, Misaki/eSpeak NG, FFmpeg/ffprobe, and optional onnx-asr/ONNX Runtime/Parakeet. No paid cloud inference, orchestration framework, voice cloning, or microphone capture is introduced.

## License scope

The MIT license covers this repository's authored scripts, docs, and original example text. It does not replace upstream model/voice/package/codec terms or grant rights to third-party training material. Keep model provenance and review upstream terms for your use case, especially when distributing audio or bundling binaries. People adapting the toolkit are responsible for their course content and publishing decisions.
