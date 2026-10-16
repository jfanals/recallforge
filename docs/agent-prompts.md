# Prompts you can give your agent

Run your coding agent in the cloned repository. It needs ordinary file/terminal access and permission to install the chosen local dependencies; no special agent SDK or hosted service is required. Review downloads/commands before approving them.

## A new course

> Read `AGENTS.md`, `.agents/skills/recallforge/SKILL.md`, and the referenced course-design guide. I want an original audio-first course for [instruction language] speakers learning [target language/dialect]. My current ability is [description]. I want to handle [real situations]. Ask any missing questions, inspect my OS/Python/audio prerequisites, and write a private brief and course map under `workspace/`. Start with one short pilot, not the entire course. Use supported local voices, explicit speaking windows, and a final recall/transfer task. Validate before synthesis. Give me MP3, chaptered M4A, a timed script, reports, and an honest list of what was actually reviewed. Do not publish personal information.

## Reproduce the example

> Follow the setup guide and render `examples/quickstart.json` into a fresh `output/quickstart-v1` directory. Run unit tests and the bundle audit. Explain where the audio and transcript are and how I should evaluate them. Ask before optional large model downloads. Do not label the audio human-reviewed.

## Grow a pilot into a sequence

> Here is my pilot feedback: [feedback]. Read the course-design guide. Revise the pilot first if necessary, then outline [N] short lessons with explicit outcomes, limited new frames, review from earlier lessons, and next-day retrieval checks. Keep a review ledger. Produce only the next lesson until I approve its content and voices.

## Fix a pronunciation report

> At [timestamp] in [output revision], [phrase] sounds like [description]. Read the audio-pipeline pronunciation-debugging section and quality gates. Identify the original segment and cached clip. Compare raw speech, assembled WAV, and encoded audio before changing anything. Test a few controlled voice/speed alternatives, preserve all consonants and speaking windows, and create an A/B comparison plus a new revision. State what automated evidence can and cannot establish.

## Another language

> I want [instruction language] → [target language/dialect]. Check `docs/lesson-format.md` and upstream Kokoro voice/language support first. If unsupported, say so instead of rendering through an English pipeline. If supported, provision needed Misaki extras and create a short native-text voice pilot with difficult endings, questions and representative sounds. Do not claim pronunciation quality until a qualified listener reviews it.

## Optional player

> I have reviewed audio bundles and want an interactive browser player like the linked `learn-english` example. Inspect that repository's public exporter, manifest, player and tests. Plan an explicit adapter from RecallForge's timeline to the player's manifest rather than copying JSON unchanged. Keep learner answer windows distinct from sentence gaps, use relative asset URLs, exclude private answer metadata if not intended for the UI, and test browser pause/resume/navigation races and project-subpath hosting. Ask before publishing.
