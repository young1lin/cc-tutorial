# Repository Guidelines

## Project Structure & Module Organization

This repository is a Claude Code tutorial, not a single application. Keep changes scoped to the content area you are editing:

- `video-scripts/`: the main 9-layer course scripts, named with zero-padded prefixes such as `layer-01-theory.md`.
- `docs/`: published articles and images.
- `research/`: source-backed research notes. Add new entries as `NN-descriptive-name.md` and update `research/00-research-summary.md`.
- `examples/http/`: runnable `.http` API examples for REST Client or JetBrains HTTP Client.
- `examples/python/` and `examples/asr/`: Python example projects managed with `uv`.
- `.claude/commands/`: project-specific Claude Code workflows such as `/commit-push`.

## Build, Test, and Development Commands

There is no repo-wide build. Use the command that matches the area you changed:

- `cd examples/python && uv sync`: install the Python example dependencies.
- `cd examples/python && uv run python 00_basic_function_calling.py 1`: run a sample Python demo.
- `cd examples/asr && uv sync`: install the ASR example dependencies.
- `cd examples/asr && uv run python main.py`: start the ASR demo locally.
- Open `examples/http/*.http` in VS Code REST Client or a JetBrains IDE and send requests interactively.

## Coding Style & Naming Conventions

Use concise Markdown, short sections, and concrete examples. For Python, follow PEP 8 with 4-space indentation. Match existing naming patterns:

- ordered tutorial files: `layer-02-setup.md`, `01-main.http`
- documentation and research files: kebab-case
- helper scripts: descriptive snake_case or existing local convention

When adding tutorial analysis or opinionated guidance, clearly label it as author interpretation rather than fact.

## Project Writing Rules

### Evidence Rules

If it is a fact, prove it. If it cannot be proved, do not present it as fact.

- Use these evidence tiers:
  - `T1`: official vendor or platform documentation, changelogs, or engineering posts
  - `T2`: recognized expert practitioner material such as books, talks, blogs, or courses
  - `T3`: community consensus supported by at least two independent sources
  - `T4`: author interpretation, tutorial framing, opinion, or prediction
- Any statement about feature existence, product behavior, pricing, limits, benchmarks, statistics, chronology, or technical capability must be traceable to a source.
- Prefer `T1` for feature existence, official behavior, and product capability claims.
- Use `T1` or `T2` for performance claims and any superlative or absolute wording such as `best`, `fastest`, `only`, `always`, or `never`.
- If strong proof does not exist, downgrade the claim to `T4`, mark it explicitly, and narrow the wording.
- Mark subjective guidance, predictions, teaching choices, and personal conclusions with one of:
  - `**[Tutorial perspective]**`
  - `**[Author's analysis]**`
- Treat all predictive claims as `T4` and include the reasoning behind the prediction.
- For `T3` claims, cite at least two independent sources.
- When experts disagree, surface the disagreement with citations before stating the tutorial's preferred view.

### Research Workflow

When adding or expanding source-backed material:

- Search existing files in `research/` first before creating a new note.
- If a new source is needed, create `research/NN-descriptive-name.md`.
- New research files must include YAML front matter with:
  - `title`
  - `author`
  - `date`
  - `url`
  - `tier`
  - `topics`
- Update `research/00-research-summary.md` whenever a new research note is added.
- Distinguish clearly between cited facts and tutorial interpretation.

### Voice And Tone

Write like a ruthless analyst, not an assistant trying to sound helpful.

- Cut without mercy. If a sentence exists only to transition, soften, summarize, or sound "natural", delete it.
- Ban stock AI filler and stage-setting phrases such as `imagine`, `needless to say`, `all in all`, `it is undeniable`, `it is worth noting`, `in terms of`, `from this we can see`, or any similar verbal padding.
- Do not warm up. Do not ease in. Open with the point, the breakage, the mechanism, or the verdict.
- Favor short sentences. Hard stops. Clean cuts. Use long sentences only when they carry real technical weight.
- Prefer blunt judgments over polite vagueness. If something is weak, say it is weak. If it fails, say where it fails.
- Use sharp, concrete words. Avoid bloodless abstractions and consultant language.
- Use metaphors as weapons, not decorations. They must tighten the logic, raise the image, and land the consequence. Never explain them after the fact.
- Use rhetorical questions to puncture bad assumptions. Do not linger on the question. Answer it with the underlying logic.
- Do not hand out emotional reassurance. No cheerleading. No fake empathy. No empty balance.
- Do not perform neutrality. If one path is better, say so. Then justify it.
- Keep the tone cold, controlled, unsentimental, and precise.
- Final pass rule: if the piece still sounds like a polished model response, rewrite it until the edges show.
- When the content is factual, keep it evidence-backed. When it is interpretation, prediction, or judgment, mark it as `T4`.

## Testing Guidelines

No root test suite exists today. Verify contributions in the smallest relevant way:

- for Python examples, run the touched script with `uv run`
- for `.http` examples, replay the edited request(s)
- for Markdown changes, check links, headings, and code fences manually

If you add automated tests for new Python behavior, prefer `pytest` with `test_*.py` naming and keep tests close to the example they cover.

## Commit & Pull Request Guidelines

Follow the conventional commit style already used in history, for example `feat(examples): add real-time ASR subtitle example` or `docs(setup): simplify permissions config example`.

When generating commit message trailers for AI-assisted commits:

- In `Claude Code`, use `Co-Authored-By: <Model Name> <noreply@anthropic.com>`.
- In `Codex` or other OpenAI terminals, use `Co-Authored-By: <Model Name> (Codex)`.
- Do not use an Anthropic email outside Claude Code.
- Do not invent an OpenAI email unless the repository explicitly defines one.

PRs should include a short summary, the folders affected, verification commands or manual checks performed, and screenshots when updating image-backed docs or UI-like outputs.

## Security & Configuration Tips

Do not commit secrets, local API keys, or `.env` files. Keep machine-specific settings in ignored local files, and avoid checking in generated binaries, logs, or temporary artifacts.
