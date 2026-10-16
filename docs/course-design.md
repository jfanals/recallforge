# Designing an original audio-first course

This is the reasoning workflow for an author or coding agent. It is not an automatic curriculum generator or a claim of experimentally proven learning outcomes. Keep curriculum choices inspectable in Markdown/JSON; avoid inventing an opaque agent orchestration system.

## 1. Intake before synthesis

Ask for:

- Instruction language and target language/dialect; verify TTS coverage.
- Learner's self-described ability and examples of what they can already say.
- Concrete communicative goals: ordering a drink, describing a studio project, asking for clarification—not “all English grammar.”
- Relevant interests, situations, accessibility constraints, and preferred voices.
- Session length, comfort with pauses, available device/OS, willingness to download models.
- Desired outputs: standard audio files, optional interactive player, or both.
- Sharing/privacy expectations. Use fictional scenarios instead of private details by default.

Do not infer a formal CEFR level from a short exchange. A learner can recognize vocabulary yet struggle to retrieve it orally; distinguish recognition, imitation, and unassisted production.

Write `workspace/brief.md`, `workspace/course-map.md`, and then a lesson JSON under `workspace/`. These paths are ignored by Git so personal briefs are not published accidentally.

## 2. Course map

Plan a sequence around small communicative outcomes. A practical starting point is 10–16 minutes per lesson, adjusted after feedback; not a mandatory formula. Introduce only a few new sentence frames and deliberately retrieve previous ones. A course map can list:

| Lesson | Communicative outcome | New frames | Review | Transfer | Next-day check |
|---|---|---|---|---|---|
| 1 | Make a polite request | Can I have…?, please | — | coffee → tea | request without replay |
| 2 | Ask for an item again | Can you…again? | requests | café → studio | two independent turns |
| 3 | Describe an ongoing project | I'm working on… | clarification | hobby → work | short personal response |

Avoid writing 30 scripts before testing one. Keep a `review-ledger.md` with frame IDs, first exposure, subsequent retrieval opportunities, and learner feedback. This toolkit does not schedule reviews for you. Revisit across later lessons and days; in-lesson repetition alone is not evidence of durable retention.

## 3. A full lesson arc

The studio worked example demonstrates ten contiguous chapters:

1. Explain how to respond, then preview a short natural dialogue.
2. Build a useful sentence in meaningful chunks and reconstruct it whole.
3. Introduce a practical clarification/request and retrieve the earlier frame.
4. Add a small contrast: now versus completed action yesterday.
5. Practice a question and negative, with concise native-language guidance.
6. Add a future plan without attempting a complete tense system.
7. Transfer the familiar frame to an everyday non-studio situation.
8. Run a guided target-language conversation with a clearly stated fictional scenario.
9. Ask an unassisted mixed recall round (nine items in the worked lesson).
10. Invite a personal response and explain tomorrow's retrieval check.

This is an example, not a template to copy mechanically for every level. A travel beginner may need fewer contrasts; an advanced learner may need pragmatic choices and longer open-ended turns instead of translation cues.

## 4. The fundamental turn

```text
spoken cue → genuine silence for learner production → model answer → short separation
```

A recall prompt must not reveal the answer before the attempt. A repeat-model turn is different: the example comes first and the learner imitates it during the following gap. Mark these distinctions with `kind` rather than guessing from punctuation.

Example:

```json
{"id":"s010","chapter":"02 · Recall","kind":"recall_prompt","language":"pt-BR","voice":"pf_dora","text":"Peça um café com educação.","gap_after_seconds":6,"expected_answer":"Can I have a coffee, please?"}
```

Follow with a separate `confirmation` segment containing the target-language model. `expected_answer` is authoring metadata, not narration, and is not synthesized unless explicitly used as another segment's `text`. Acceptable variants are for review context, not implemented automatic learner scoring.

## 5. Response windows

Starting defaults from the original lesson:

| Turn | Starting gap |
|---|---|
| Narration transition | 0.6s |
| Model/dialogue/confirmation separation | 0.8s |
| Short chunk or short reply | 4–5s |
| Full sentence retrieval | 6–8s |
| Personal response | 15–30s |

Time the response yourself; add planning time, not just articulation time. Longer or more complex utterances need more room. Let learners pause standard audio when needed. Do not compress “silence” out of the final file. Quiet waveform endings belong to speech; explicit gap time is additional and separately counted.

## 6. Useful repetition versus mechanical drilling

- Mix earlier frames into later chapters instead of keeping each block isolated.
- Use small contextual changes, tense contrasts, question/negative contrasts, and person changes as appropriate to the language.
- Start with scaffolding, then reduce translation and hints.
- Prompt a real communicative intention, not only “repeat the last sentence.”
- Keep grammar explanations short, accurate, and immediately usable.
- Transfer a frame into a new scenario so familiarity with the example is not mistaken for general ability.
- Do not force an English grammar model onto other languages; adapt chunks and teaching order to their actual structure.

## 7. Evaluation and next iteration

Ask after the pilot:

1. Too easy / useful challenge / too hard?
2. Which responses came before the model, without reading?
3. Which timestamps had too little or too much response time?
4. Which words/voices sounded unnatural? Ask for exact phrase/timestamp.
5. Can the learner retrieve two or three sentences tomorrow **before replaying**?

A nine-item recall score is a useful local signal, not a proficiency certification. Personal turns have no single correct answer. Recordings are optional and manual; never enable microphone collection implicitly. Change one variable at a time when possible: fewer new frames, more review, longer pauses, a different scenario, or a better voice.

## 8. Originality boundaries

Teach using general techniques: retrieval practice, increasing intervals, sentence construction, bilingual scaffolding, conversation and transfer. Author your own dialogue, progression, examples, explanations, and exercises. Do not ingest a purchased course and ask an agent to translate, paraphrase, or replicate its unit sequence. If a learner provides material, establish their rights before processing or sharing it. No commercial source assets are needed to run this project.
