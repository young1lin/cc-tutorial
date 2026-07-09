# Evidence-Based Content Rule

## Core Principle

If it is a fact, prove it.

If you cannot prove it, stop calling it a fact.

Opinion is allowed. Analysis is allowed. Prediction is allowed. Smuggling any of them in dressed as fact is not.

## Evidence Tiers

- `T1`: primary material from the vendor, platform, or tool owner. Official docs. Changelogs. Engineering posts.
- `T2`: recognized expert practitioner material. Books. Talks. Courses. Technical blogs with real standing.
- `T3`: community consensus. Requires at least two independent sources.
- `T4`: tutorial interpretation. Author judgment. Teaching framing. Prediction.

## Hard Rules

### 1. Every factual claim needs a trail

Any statement about product behavior, feature existence, pricing, limits, benchmarks, statistics, chronology, or technical capability must be traceable to a source.

No source, no factual claim.

### 2. Strong claims need strong proof

Words like `best`, `fastest`, `only`, `always`, `never`, `most powerful`, or anything else that tries to close the case require `T1` or `T2`.

If that proof does not exist:

- downgrade the statement to `T4`
- mark it explicitly
- narrow the wording until it stops pretending to be universal

### 3. Community repetition is not evidence unless it converges

If the claim rests on community chatter, forum wisdom, or repeated blog claims, treat it as `T3` and cite at least two independent sources.

One echo chamber is still one source.

### 4. Predictions are never facts

Every forecast, projection, or forward-looking claim is `T4`.

Mark it. Explain the reasoning. Do not write prophecy in the grammar of certainty.

### 5. Disagreement must be shown, not buried

When credible sources disagree, surface the conflict first.

Show both positions with citations. Then state the tutorial's judgment and why it takes that side.

### 6. Interpretation must wear a label

Use explicit markers for non-factual content:

- `**[Tutorial perspective]**`
- `**[Author's analysis]**`

Do not rely on tone alone to imply subjectivity. Mark it.

## Research Workflow

### 1. Search before you add

Check `research/` before creating a new note. Do not duplicate source work that already exists.

### 2. Add new sources the right way

If the source is new, create `research/NN-descriptive-name.md`.

Every new research file must include YAML front matter with:

- `title`
- `author`
- `date`
- `url`
- `tier`
- `topics`

### 3. Update the index

If you add a research note, update `research/00-research-summary.md`.

No orphan notes. No hidden evidence.

## What Requires Evidence

- feature existence or product behavior: `T1`
- benchmarks and performance claims: `T1` or `T2`
- expert recommendations or quoted guidance: `T2`
- statistics, counts, and quantitative claims: `T1`, `T2`, or `T3`
- workflow recommendations, teaching advice, and framing: `T4` is acceptable if clearly marked
- predictions: always `T4`

## Final Check

Before publishing:

- every factual claim has a source or gets cut
- every opinion is marked or obviously framed as `T4`
- every strong claim has evidence strong enough to carry the weight
- every new research file follows the repository format
- every new research file is reflected in `research/00-research-summary.md`
