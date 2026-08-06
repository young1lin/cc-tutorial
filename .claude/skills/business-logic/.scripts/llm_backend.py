# /// script
# requires-python = ">=3.10"
# dependencies = ["pydantic-ai-slim[openai,anthropic]>=2.0"]
# ///
"""
Unified LLM backend for the business-logic engine, built on PydanticAI.

One agent loop over two wire protocols:
  - openai    : OpenAI ChatCompletion (and any compatible endpoint: glm,
               deepseek, qwen, one-api/new-api relays, ...) via OpenAIChatModel
  - anthropic : Anthropic Messages via AnthropicModel

PydanticAI provides the agent runtime + tool-calling; we only register the
tools and pick the model from env. Proxy is handled automatically: PydanticAI
uses httpx (trust_env=True), so HTTPS_PROXY / HTTP_PROXY / NO_PROXY in the
environment just work. Writes are sandboxed to the skill data dir so a stray
model call can never touch source code.

Set SYNC_BACKEND=openai|anthropic in .env. Empty / "claude-sdk" returns None,
telling the caller to use the legacy claude-agent-sdk path instead.
"""

import os
import re
import subprocess
import glob as _globmod
from dataclasses import dataclass
from pathlib import Path

from pydantic_ai import Agent, RunContext, Tool

# Cap on any single tool result handed back to the model (keeps context sane).
MAX_TOOL_RESULT = 20_000


# ---------------------------------------------------------------------------
# Dependency injection (each tool reads its sandbox roots from here)
# ---------------------------------------------------------------------------

@dataclass
class SyncDeps:
    work_root: str   # read / glob / grep scoped here
    data_dir: str    # write / edit sandboxed here
    allow_bash: bool


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _within(path, root):
    p = Path(path).resolve()
    r = Path(root).resolve()
    return p == r or r in p.parents


def _truncate(s):
    return s if len(s) <= MAX_TOOL_RESULT else s[:MAX_TOOL_RESULT] + "\n...[truncated]"


# ---------------------------------------------------------------------------
# Tools (executed in-process; schema auto-generated from the type hints +
# docstring by PydanticAI). Errors are returned as text, never raised, so the
# loop continues and the model can self-correct.
# ---------------------------------------------------------------------------

def _read(ctx: RunContext[SyncDeps], path: str) -> str:
    """Read a file's text content (UTF-8). Use to inspect source or existing docs."""
    try:
        p = Path(path)
        if not _within(p, ctx.deps.work_root):
            return "ERROR: path outside the project root"
        return _truncate(p.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return "ERROR: read: {}".format(e)


def _write(ctx: RunContext[SyncDeps], path: str, content: str) -> str:
    """Write text to a file. Writes are sandboxed to the skill data dir."""
    try:
        p = Path(path)
        if not _within(p, ctx.deps.data_dir):
            return "ERROR: writes are sandboxed to {}".format(ctx.deps.data_dir)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return "wrote {} bytes to {}".format(len(content), p)
    except Exception as e:
        return "ERROR: write: {}".format(e)


def _edit(ctx: RunContext[SyncDeps], path: str, old_string: str, new_string: str) -> str:
    """Replace exactly one occurrence of old_string with new_string in a file."""
    try:
        p = Path(path)
        if not _within(p, ctx.deps.data_dir):
            return "ERROR: edits are sandboxed to {}".format(ctx.deps.data_dir)
        text = p.read_text(encoding="utf-8")
        count = text.count(old_string)
        if count == 0:
            return "ERROR: old_string not found"
        if count > 1:
            return "ERROR: old_string matches {} times; make it unique".format(count)
        p.write_text(text.replace(old_string, new_string, 1), encoding="utf-8")
        return "edited {}".format(p)
    except Exception as e:
        return "ERROR: edit: {}".format(e)


def _glob(ctx: RunContext[SyncDeps], pattern: str) -> str:
    """List files matching a glob pattern (relative to the project root)."""
    try:
        return _truncate("\n".join(
            _globmod.glob(pattern, recursive=True, root_dir=ctx.deps.work_root)))
    except Exception as e:
        return "ERROR: glob: {}".format(e)


def _grep(ctx: RunContext[SyncDeps], pattern: str, include: str = "*") -> str:
    """Search file contents for a regex; return matching file:line: text rows."""
    try:
        pat = re.compile(pattern)
        hits = []
        for f in _globmod.glob(include, recursive=True, root_dir=ctx.deps.work_root):
            fp = Path(ctx.deps.work_root) / f
            if not fp.is_file():
                continue
            try:
                for i, line in enumerate(fp.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                    if pat.search(line):
                        hits.append("{}:{}: {}".format(f, i, line.strip()[:200]))
            except OSError:
                continue
            if len(hits) > 200:
                hits.append("...[truncated]")
                break
        return _truncate("\n".join(hits))
    except Exception as e:
        return "ERROR: grep: {}".format(e)


def _bash(ctx: RunContext[SyncDeps], command: str) -> str:
    """Run a shell command. Disabled unless ALLOW_SYNC_BASH=1 is set."""
    if not ctx.deps.allow_bash:
        return "ERROR: bash disabled (set ALLOW_SYNC_BASH=1 to enable)"
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True,
                           cwd=ctx.deps.work_root, timeout=120)
        out = (r.stdout or "") + (("\n[stderr]\n" + r.stderr) if r.stderr else "")
        return _truncate(out)
    except Exception as e:
        return "ERROR: bash: {}".format(e)


TOOLS = [
    Tool(_read, takes_ctx=True),
    Tool(_write, takes_ctx=True),
    Tool(_edit, takes_ctx=True),
    Tool(_glob, takes_ctx=True),
    Tool(_grep, takes_ctx=True),
    Tool(_bash, takes_ctx=True),
]


# ---------------------------------------------------------------------------
# Model factory (reads env; returns None for the legacy claude-sdk path)
# ---------------------------------------------------------------------------

def make_model(env):
    """Build a PydanticAI model from env, or None when SYNC_BACKEND=claude-sdk."""
    backend = (env.get("SYNC_BACKEND") or "").strip().lower()
    if backend in ("", "claude-sdk", "claude"):
        return None  # caller falls back to the claude-agent-sdk path

    if backend == "openai":
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.openai import OpenAIProvider
        base = env.get("OPENAI_BASE_URL") or env.get("OPENAI_API_BASE") or None
        key = env.get("OPENAI_API_KEY") or env.get("OPENAI_TOKEN") or None
        return OpenAIChatModel(
            env.get("OPENAI_MODEL") or env.get("SYNC_MODEL") or "",
            provider=OpenAIProvider(base_url=base, api_key=key),
        )

    if backend == "anthropic":
        from anthropic import AsyncAnthropic
        from pydantic_ai.models.anthropic import AnthropicModel
        from pydantic_ai.providers.anthropic import AnthropicProvider
        client = AsyncAnthropic(
            api_key=env.get("ANTHROPIC_API_KEY") or env.get("ANTHROPIC_AUTH_TOKEN") or None,
            base_url=env.get("ANTHROPIC_BASE_URL") or None,
        )
        return AnthropicModel(
            env.get("ANTHROPIC_MODEL") or env.get("SYNC_MODEL") or "",
            provider=AnthropicProvider(anthropic_client=client),
        )

    raise ValueError("unknown SYNC_BACKEND: {!r}".format(backend))


# Back-compat alias: auto_sync asks make_backend() whether to use the PydanticAI
# path. Does NOT construct the model (that needs a valid key); it only inspects
# SYNC_BACKEND so the caller can dispatch before any API key check fires.
def make_backend(env):
    """Return 'pydantic-ai' if SYNC_BACKEND targets openai/anthropic, else None."""
    backend = (env.get("SYNC_BACKEND") or "").strip().lower()
    return "pydantic-ai" if backend in ("openai", "anthropic") else None


# ---------------------------------------------------------------------------
# Worker entry point
# ---------------------------------------------------------------------------

DEFAULT_SYSTEM = (
    "You are the automated business-logic documentation sync worker. "
    "Read the changed code with `read`/`grep`/`glob`, then update the markdown "
    "docs under the skill data dir with `edit`/`write`. Never touch source code. "
    "Never ask for permission -- act directly."
)


async def run_worker(prompt, system, env, work_root, data_dir,
                     allow_bash=False, log=None):
    """Run one PydanticAI agent turn to completion. Returns (last_text, ok).

    ok is False if the loop ran out without a final answer or raised.
    """
    model = make_model(env)
    if model is None:
        return "", False  # caller should use the legacy claude-sdk path
    agent = Agent(
        model,
        deps_type=SyncDeps,
        tools=TOOLS,
        system_prompt=system or DEFAULT_SYSTEM,
    )
    deps = SyncDeps(str(work_root), str(data_dir), allow_bash)
    # reasoning_effort: the OpenAI-format thinking level (low/medium/high/max).
    # Honored by OpenAI-compatible providers that support it (e.g. DeepSeek V4,
    # GLM). Anthropic uses a different thinking budget, so skip it there.
    model_settings = {}
    if (env.get("SYNC_BACKEND") or "").strip().lower() == "openai":
        effort = (env.get("REASONING_EFFORT") or "").strip().lower()
        if effort:
            model_settings["reasoning_effort"] = effort
    try:
        result = await agent.run(prompt, deps=deps, model_settings=model_settings or None)
    except Exception as e:
        if log:
            log("worker raised: %s", e)
        return "", False
    if log:
        usage = getattr(result, "usage", None)
        log("worker done, output=%d chars, usage=%s", len(result.output or ""), usage)
    return result.output, True
