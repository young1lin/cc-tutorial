# Evidence-Based Content Rule

This rule enforces rigorous evidence standards for all content created in this tutorial project.

## Core Principle

**Every factual claim must be traceable to a verifiable source.** Opinions must be clearly distinguished from facts.

## Evidence Tiers

| Tier | Name | Definition |
|------|------|------------|
| **T1** | Official Doctrine | Primary source from the tool/platform vendor (official docs, changelogs, engineering team blog posts) |
| **T2** | Expert Practitioner | Published content from recognized practitioners (blogs, conference talks, courses, books) |
| **T3** | Community Consensus | Widely repeated claim across multiple independent sources (requires 2+ citations) |
| **T4** | Author Interpretation | Your own analysis, opinion, pedagogical framing, or prediction |

## Citation Requirements

### T1 Citations (Official)
```markdown
According to [Anthropic's official documentation](URL) (Author/Team, YYYY-MM), ...
```

### T2 Citations (Expert)
```markdown
Boris Cherny recommends ... ([Best Practices Guide](research/01-xxx.md), 2025-01)
```

### T3 Citations (Community)
Must reference at least two independent sources:
```markdown
Multiple sources report that ... ([Source A](URL), [Source B](URL))
```

### T4 Markers (Opinion)
Must be explicitly prefixed:
```markdown
**[Author's analysis]** Based on our testing across 5 projects, we found that ...
**[Tutorial perspective]** We recommend starting with Module 01 because ...
```

## Critical Thinking Requirements

### Superlative and Absolute Claims
Statements containing "best", "only", "always", "never", "fastest", "most powerful" require **T1 or T2 evidence**. If unavailable:
1. Mark as T4 with explicit prefix
2. Use hedging language ("in our experience", "based on available benchmarks")

**Bad:** "Claude Code is the best AI coding tool available."
**Good:** "**[Tutorial perspective]** In our testing, Claude Code provided the most effective workflow for the use cases covered in this tutorial."

### Conflicting Expert Opinions
When experts disagree, present **both positions with citations**:
```markdown
There are differing views on this approach:
- Boris Cherny argues for X ([source](URL))
- Addy Osmani suggests Y ([source](URL))

**[Tutorial perspective]** For this tutorial, we follow X because ...
```

### Predictive Claims
All predictions are **always T4**. Include:
1. `**[Author's analysis]**` prefix
2. Reasoning chain explaining the basis

## Research Directory Integration

When encountering new claims that require evidence:

1. **Search existing research** in `research/` first
2. **If no evidence exists**, either:
   - Find and cite a credible source, save to `research/NN-descriptive-name.md`
   - Mark as T4 with explicit marker
3. **New research files** must include YAML front matter:
   ```yaml
   ---
   title: "Source Title"
   author: "Author Name"
   date: "YYYY-MM-DD"
   url: "https://original-source-url"
   tier: T1 | T2 | T3
   topics: [topic1, topic2]
   ---
   ```
4. **Update** `research/00-research-summary.md` with a summary entry

## Quick Reference

| Claim Type | Evidence Required |
|------------|-------------------|
| Performance/benchmark claims | T1 or T2 citation |
| Feature existence claims | T1 citation |
| Expert quotes | T2 citation |
| Statistics/numerical data | T1-T3 citation |
| Workflow recommendations | T4 marker sufficient |
| Analogies/metaphors | T4 marker sufficient |
| Predictions | T4 marker + reasoning |

## Verification Checklist

Before publishing any content:
- [ ] All factual claims have citations or T4 markers
- [ ] Superlative claims have T1/T2 support or are hedged
- [ ] Conflicting opinions are presented fairly
- [ ] New research files follow the standard format
- [ ] Research summary is updated
