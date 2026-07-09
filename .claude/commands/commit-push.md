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

Co-Authored-By: {Model Identity}
```

**重要**:
- 模型名称使用当前会话的实际模型
- 根据当前终端区分署名格式，不要跨厂商混用身份
- 不要猜测或伪造 OpenAI 邮箱

**示例：**
- `claude-opus-4-6` in Claude Code → `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`
- `gpt-5` in Codex → `Co-Authored-By: GPT-5 (Codex)`
- `gpt-4o` in Codex → `Co-Authored-By: GPT-4o (Codex)`

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

1. **Identify current model and terminal** - Determine the actual model name and whether the session is running in Claude Code or Codex/OpenAI
2. Run `git status --porcelain` to get list of changes
3. Run `git diff --stat` to see change summary
4. Filter out files matching exclusion patterns
5. Run `git add` on remaining files
6. Generate commit message based on changes, using the correct trailer format:
   - Claude Code: `Co-Authored-By: <Model Name> <noreply@anthropic.com>`
   - Codex/OpenAI: `Co-Authored-By: <Model Name> (Codex)`
7. Run `git commit` with the message
8. Run `git push` to remote

## Error Handling

If any step fails:
- Show the error message
- Don't proceed to next step
- Allow user to manually fix and retry
