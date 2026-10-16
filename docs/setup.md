# Setup and dependencies

## Supported approach

Use a dedicated Python 3.11/3.12 virtual environment. This repository's actual smoke render used Python 3.12 on macOS Apple Silicon and CPU-capable PyTorch. Other platforms have upstream support but have not been exercised here. Keep installation problems separate from lesson authoring: validate the example first, then render a short pilot, then attempt a full lesson.

## System programs

macOS with Homebrew:

```sh
brew install python@3.12 ffmpeg espeak-ng
```

Debian/Ubuntu:

```sh
sudo apt-get update
sudo apt-get install python3 python3-venv ffmpeg espeak-ng libsndfile1
```

Windows:

1. Install a supported Python and ensure it is available in your shell.
2. Install FFmpeg/ffprobe and place their executable directory on `PATH`.
3. Install eSpeak NG using its official Windows MSI; follow its platform-specific shared-library discovery instructions if phonemization cannot find it.
4. Create `.venv` with `py -3.12 -m venv .venv`; activate with `.venv\Scripts\Activate.ps1`, or use `.venv\Scripts\python.exe` directly.
5. If native audio dependencies are difficult, WSL with the Linux instructions is another route. Native Windows/WSL have not been tested by this project.

Official eSpeak guidance: https://github.com/espeak-ng/espeak-ng/blob/master/docs/guide.md

Check binaries:

```sh
python --version
ffmpeg -version
ffprobe -version
espeak-ng --version
```

## Python installation

From repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/lesson.py examples/quickstart.json
python scripts/render.py examples/quickstart.json --output output/first-pilot
python scripts/audit.py output/first-pilot
```

`requirements.txt` pins Kokoro/Misaki to the production versions used, with bounded companion dependencies; it is not a platform lockfile. PyTorch wheels vary by OS and accelerator. If the PyTorch install fails, use the official selector at https://pytorch.org/get-started/locally/ and then retry the remaining requirements. For reproducibility, save `python -m pip freeze > environment-lock.txt` alongside your private project records. The render report records core library versions, not every system/model asset revision.

## What each library does

| Component | Role | Required? |
|---|---|---|
| Kokoro 0.9.4 / Kokoro-82M | Local text-to-speech and voice selection | Render |
| Misaki 0.9.4 | Language-aware grapheme-to-phoneme conversion | Render |
| eSpeak NG | Phonemization/fallback for applicable languages | Recommended system prerequisite |
| PyTorch | Neural inference (CPU works) | Render |
| NumPy | PCM arrays, silence, waveform checks | Render/audit/ASR |
| SoundFile/libsndfile | Read/write WAV and stream assembly | Render/audit |
| FFmpeg / ffprobe | Encode, normalize, chapter, inspect | Render/ASR |
| onnx-asr + ONNX Runtime | Optional local speech recognition | ASR only |
| JSON Schema validator | Optional editor/external schema validation | Not needed by CLI |
| matplotlib | Optional manual waveform/spectrogram investigation | Not bundled/required |
| Node.js | Separate web-player tests/hosting workflow | Not required here |

## Downloads and offline use

Kokoro uses `hexgrad/Kokoro-82M` on Hugging Face; first initialization and each previously unused voice may download weights. Misaki may provision language assets such as English NLP resources. Install Japanese/Chinese extras only when needed (`python -m pip install 'misaki[ja]==0.9.4'` or `'misaki[zh]==0.9.4'`), and validate upstream setup requirements.

Run every desired language/voice once while online. Then test a new render using the provisioned assets with networking disabled before promising offline operation. Hugging Face cache controls such as `HF_HOME` and `HF_HUB_OFFLINE=1` affect HF downloads, not necessarily all third-party language resource downloads. This repository does not bundle or mirror models. No token is normally needed for the public model; never put an access token in a lesson or commit it.

## Optional speech back-check

Use a separate environment if ONNX and synthesis dependency requirements conflict:

```sh
python -m pip install -r requirements-asr.txt
python scripts/check_speech.py output/first-pilot --languages en-US pt-BR
```

Default: `nemo-parakeet-tdt-0.6b-v3`, provisioned through onnx-asr/Hugging Face. To reuse a compatible local ONNX export without hardcoding any application directory:

```sh
python scripts/check_speech.py output/first-pilot \
  --model-dir /path/to/your/parakeet-onnx-directory --quantization int8
```

Do not point at arbitrary PyTorch/MLX weights: the model name, ONNX export files, and quantization must match. Check your ASR model's language coverage. The script skips utterances over 20 seconds and records them; split these or use a VAD-aware workflow rather than treating skipped clips as checked.

## Troubleshooting

- **Missing ffmpeg/ffprobe:** install both and restart the shell if `PATH` changed.
- **eSpeak shared library not found:** confirm architecture matches Python and follow upstream eSpeak/Misaki installation instructions. Do not hide it by changing lesson text.
- **No audio/unsupported voice:** use a real voice from the model's voice list and match its first-letter language prefix. Prefix checks cannot prove a voice exists.
- **Slow rendering:** start with the 14-segment example; subsequent renders reuse matching cached speech. Do not increase speed or shorten response pauses to disguise slow synthesis.
- **Nonempty output folder:** choose `output/lesson-v2`; caches can still be shared.
- **Interrupted run:** choose a fresh output folder; validated completed cache clips are reusable. Invalid cache files should be removed individually and regenerated.
- **GPU/backend problems:** use a known-working CPU PyTorch installation first. This CLI does not expose a device-selection option; backend choice is inherited from Kokoro/PyTorch.
- **Installation is not locked:** the known local smoke-test versions were Kokoro 0.9.4, Misaki 0.9.4, PyTorch 2.11.0, NumPy 2.4.4, SoundFile 0.14.0. Do not assume every combination within dependency ranges has been tested.
