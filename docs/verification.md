# Initial verification record

These are observed results from the initial RecallForge implementation on macOS Apple Silicon, not performance or quality guarantees for other installations.

## Automated tests

- 21 local tests passed, including a synthetic-waveform FFmpeg MP3/AAC integration test and an intentional nonzero-pause corruption that the auditor correctly rejected.
- Both checked-in examples passed operational validation and JSON Schema Draft 2020-12 validation.
- `examples/author_studio.py` regenerated the complete studio example with 156 segments, 43 prompt turns, and 497s explicit gaps.
- Python files compiled successfully. Skill reference paths were checked by a unit test.
- CI is configured for Python 3.11/3.12 unit/schema tests and a separate synthetic-audio integration job. See GitHub Actions for actual remote run outcomes; local tests alone do not prove remote CI succeeded.

## Real local synthesis

| Metric | Quickstart | Full studio lesson |
|---|---:|---:|
| Duration | 89.287s | 939.744917s |
| Speech including preserved tails | 40.687s | 442.744917s |
| Explicit learner/transition silence | 48.6s | 497s |
| Segments | 14 | 156 |
| Unique clips | 11 | 99 |
| Chapters | 3 | 10 |
| Integrity audit | passed | passed |
| MP3 codec/duration probe | passed | passed |
| M4A codec/duration/chapter probe | passed | passed |
| Human listening review | not performed | not performed |

Reference stack: Python 3.12.12, Kokoro 0.9.4, Misaki 0.9.4, PyTorch 2.11.0, NumPy 2.4.4, SoundFile 0.14.0; model `hexgrad/Kokoro-82M`; 24 kHz mono clips; `safe-edges-v2`. Full studio duration differs slightly from the historical 939.716s pilot, as expected from fresh synthesis.

## Optional ASR smoke test

The quickstart's 11 unique clips were checked locally with onnx-asr 0.10.2 and a pre-provisioned Parakeet v3 int8 ONNX model. No eligible clips were skipped. All target-language English examples matched their normalized intended text. Two Portuguese narrator clips fell below the script's 0.9 token-sequence-agreement heuristic:

- “Troque café por chá. Ouça e repita.” → recognized as “Troque café por chá ou sem repita.” (approximately 0.71).
- “Sem ler, peça um café com educação.” → recognized as “Sem ler, peçam café com educação.” (approximately 0.77).

One further Portuguese result normalized spoken “quinze” to digits, reducing agreement slightly without triggering the heuristic. The text normalizer does not normalize number words across languages.

These are **unresolved listening-review candidates**, not established TTS errors or proof that the other clips are phonetically perfect. No full-studio ASR run or human audition is claimed for this new toolkit revision. Inspect before distributing lessons as reviewed teaching material. Generated bundles and their detailed reports remain local/ignored; this record contains only non-private results.
