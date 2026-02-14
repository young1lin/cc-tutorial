---
description: Stage changed files, create a commit, and push to remote
---

# Commit & Push

Automatically stage files, create a commit message, and push to remote repository.

## What This Command Does

1. **Analyze changes**: Shows what files have been modified/added/deleted
2. **Filter files**: Excludes files that shouldn't be committed:
   - `debug*.json` - Debug output files
   - `*.exe`, `*.dll` - Compiled binaries (unless explicitly added)
   - `*.log` - Log files
   - `.DS_Store` - macOS system files
   - `*.tmp`, `*.swp` - Temporary files
3. **Stage files**: Runs `git add` on remaining files
4. **Create commit**: Generates a conventional commit message
5. **Push**: Pushes to the current branch's remote

## Usage

```
/commit-push
```

## Commit Message Format

Follows conventional commits format:

```
<type>(<scope>): <description>

[optional body]

Co-Authored-By: {Current Model} <noreply@anthropic.com>
```

**重要**: Co-Authored-By 中的模型名称必须使用当前会话的实际模型。从系统消息 "You are powered by the model XXX" 中获取。例如：
- 如果是 glm-5，则写 `Co-Authored-By: GLM-5 <noreply@anthropic.com>`
- 如果是 claude-opus-4-6，则写 `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `docs` - Documentation changes
- `chore` - Maintenance tasks
- `perf` - Performance improvements

## Examples

**Example 1: Feature addition**
```
Changes:
+ cmd/statusline/main.go (new feature)
+ internal/parser/transcript.go (updated)

→ Commit: "feat(statusline): add token progress display"
```

**Example 2: Bug fix**
```
Changes:
M internal/config/paths.go (fix path handling)

→ Commit: "fix(config): correct Windows path resolution"
```

**Example 3: Test updates**
```
Changes:
M cmd/statusline/main_test.go
M internal/parser/parser_test.go

→ Commit: "test: add comprehensive test coverage for parser"
```

## Files to Exclude from Commit

The following patterns are automatically excluded:

| Pattern | Description |
|---------|-------------|
| `debug*.json` | Debug output files |
| `*.exe`, `*.dll`, `*.so` | Compiled binaries |
| `*.log` | Log files |
| `.DS_Store` | macOS system files |
| `Thumbs.db` | Windows thumbnail cache |
| `*.tmp`, `*.swp`, `*.swo` | Editor temporary files |
| `node_modules/` | Node.js dependencies |
| `__pycache__/` | Python cache |
| `*.pyc` | Python bytecode |

## Steps to Execute

1. **Identify current model** - Extract model name from system context (e.g., "You are powered by the model glm-5")
2. Run `git status --porcelain` to get list of changes
3. Run `git diff --stat` to see change summary
4. Filter out files matching exclusion patterns
5. Run `git add` on remaining files
6. Generate commit message based on changes, using the correct model name in Co-Authored-By
7. Run `git commit` with the message
8. Run `git push` to remote

## Error Handling

If any step fails:
- Show the error message
- Don't proceed to next step
- Allow user to manually fix and retry
