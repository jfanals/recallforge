# Working in RecallForge

Read `.agents/skills/recallforge/SKILL.md` for the course-production workflow. The canonical lesson shape is `lesson.schema.json`; operational semantics live in `scripts/lesson.py`. Detailed references live under `docs/`. Run commands from repository root.

- Author original material only. No commercial recordings, transcripts, or source-derived course reproductions.
- Learner projects belong in ignored `workspace/`; synthesis caches in ignored `build/`; outputs in ignored `output/`.
- Validate before loading models. Start with a short pilot and keep revisions in new output directories.
- Preserve response windows and natural speech endings. Never treat an ASR match or waveform metric as human listening review.
- Test: `python -m unittest discover -s tests -v`. Audio smoke test: render `examples/quickstart.json`, then run `scripts/audit.py` on the bundle.
- Document dependencies and limitations honestly. Never commit secrets, machine-specific model locations, downloaded weights, learner recordings, or unreviewed personal material.
- Do not build an agent framework: ordinary files, inspectable CLI tools, explicit reports, and the user's agent are enough.
