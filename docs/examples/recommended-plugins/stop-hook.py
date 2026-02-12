#!/usr/bin/env python3
"""
Ralph Loop Stop Hook (Python version for Windows compatibility)
Prevents session exit when a ralph-loop is active
Feeds Claude's output back as input to continue the loop
"""

import sys
import os
import json
import re
from pathlib import Path


def main():
    try:
        # Read hook input from stdin
        hook_input = json.loads(sys.stdin.read())

        # Check if ralph-loop is active
        ralph_state_file = Path(".claude/ralph-loop.local.md")

        if not ralph_state_file.exists():
            # No active loop - allow exit
            sys.exit(0)

        # Read state file content
        state_content = ralph_state_file.read_text(encoding="utf-8")

        # Parse frontmatter (YAML between ---)
        frontmatter_match = re.search(r'^---$(.*?)^---$', state_content, re.MULTILINE | re.DOTALL)
        if not frontmatter_match:
            print("⚠️  Ralph loop: State file corrupted - no frontmatter found", file=sys.stderr)
            ralph_state_file.unlink()
            sys.exit(0)

        frontmatter_text = frontmatter_match.group(1)

        # Extract values from frontmatter
        def extract_field(pattern):
            match = re.search(rf'^{pattern}:\s*(.+)$', frontmatter_text, re.MULTILINE)
            if match:
                value = match.group(1).strip()
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                return value
            return None

        iteration_str = extract_field('iteration')
        max_iterations_str = extract_field('max_iterations')
        completion_promise = extract_field('completion_promise')

        # Validate numeric fields
        try:
            iteration = int(iteration_str) if iteration_str else 0
        except ValueError:
            print("⚠️  Ralph loop: State file corrupted", file=sys.stderr)
            print(f"   File: {ralph_state_file}", file=sys.stderr)
            print(f"   Problem: 'iteration' field is not a valid number (got: '{iteration_str}')", file=sys.stderr)
            print("", file=sys.stderr)
            print("   Ralph loop is stopping. Run /ralph-loop again to start fresh.", file=sys.stderr)
            ralph_state_file.unlink()
            sys.exit(0)

        try:
            max_iterations = int(max_iterations_str) if max_iterations_str else 0
        except ValueError:
            print("⚠️  Ralph loop: State file corrupted", file=sys.stderr)
            print(f"   File: {ralph_state_file}", file=sys.stderr)
            print(f"   Problem: 'max_iterations' field is not a valid number (got: '{max_iterations_str}')", file=sys.stderr)
            print("", file=sys.stderr)
            print("   Ralph loop is stopping. Run /ralph-loop again to start fresh.", file=sys.stderr)
            ralph_state_file.unlink()
            sys.exit(0)

        # Check if max iterations reached
        if max_iterations > 0 and iteration >= max_iterations:
            print(f"🛑 Ralph loop: Max iterations ({max_iterations}) reached.")
            ralph_state_file.unlink()
            sys.exit(0)

        # Get transcript path from hook input
        transcript_path = hook_input.get('transcript_path')

        if not transcript_path:
            print("⚠️  Ralph loop: No transcript_path in hook input", file=sys.stderr)
            ralph_state_file.unlink()
            sys.exit(0)

        transcript_file = Path(transcript_path)
        if not transcript_file.exists():
            print("⚠️  Ralph loop: Transcript file not found", file=sys.stderr)
            print(f"   Expected: {transcript_path}", file=sys.stderr)
            ralph_state_file.unlink()
            sys.exit(0)

        # Read transcript and find last assistant message
        transcript_lines = transcript_file.read_text(encoding="utf-8").strip().split('\n')

        last_assistant_line = None
        for line in reversed(transcript_lines):
            if '"role":"assistant"' in line:
                last_assistant_line = line
                break

        if not last_assistant_line:
            print("⚠️  Ralph loop: No assistant messages found in transcript", file=sys.stderr)
            ralph_state_file.unlink()
            sys.exit(0)

        # Parse JSON and extract text content
        try:
            message_data = json.loads(last_assistant_line)
            content_list = message_data.get('message', {}).get('content', [])

            # Extract text from content blocks
            last_output = '\n'.join(
                item.get('text', '')
                for item in content_list
                if item.get('type') == 'text'
            )
        except (json.JSONDecodeError, KeyError) as e:
            print("⚠️  Ralph loop: Failed to parse assistant message JSON", file=sys.stderr)
            print(f"   Error: {e}", file=sys.stderr)
            ralph_state_file.unlink()
            sys.exit(0)

        if not last_output:
            print("⚠️  Ralph loop: Assistant message contained no text content", file=sys.stderr)
            ralph_state_file.unlink()
            sys.exit(0)

        # Check for completion promise (only if set)
        if completion_promise and completion_promise != 'null':
            # Extract text from <promise> tags
            promise_match = re.search(r'<promise>(.*?)</promise>', last_output, re.DOTALL)
            if promise_match:
                promise_text = promise_match.group(1).strip()
                # Normalize whitespace
                promise_text = re.sub(r'\s+', ' ', promise_text).strip()

                if promise_text and promise_text == completion_promise.strip():
                    print(f"✅ Ralph loop: Detected <promise>{completion_promise}</promise>")
                    ralph_state_file.unlink()
                    sys.exit(0)

        # Not complete - continue loop
        next_iteration = iteration + 1

        # Extract prompt text (everything after second ---)
        parts = state_content.split('---', 2)
        if len(parts) < 3:
            print("⚠️  Ralph loop: State file corrupted or incomplete", file=sys.stderr)
            print(f"   File: {ralph_state_file}", file=sys.stderr)
            print("   Problem: No prompt text found", file=sys.stderr)
            ralph_state_file.unlink()
            sys.exit(0)

        prompt_text = parts[2].strip()

        if not prompt_text:
            print("⚠️  Ralph loop: State file corrupted - empty prompt", file=sys.stderr)
            ralph_state_file.unlink()
            sys.exit(0)

        # Update iteration in frontmatter
        new_content = re.sub(
            r'^iteration: .*$',
            f'iteration: {next_iteration}',
            state_content,
            count=1,
            flags=re.MULTILINE
        )
        ralph_state_file.write_text(new_content, encoding="utf-8")

        # Build system message
        if completion_promise and completion_promise != 'null':
            system_msg = f"🔄 Ralph iteration {next_iteration} | To stop: output <promise>{completion_promise}</promise> (ONLY when statement is TRUE - do not lie to exit!)"
        else:
            system_msg = f"🔄 Ralph iteration {next_iteration} | No completion promise set - loop runs infinitely"

        # Output JSON to block the stop and feed prompt back
        result = {
            "decision": "block",
            "reason": prompt_text,
            "systemMessage": system_msg
        }

        print(json.dumps(result, ensure_ascii=False))
        sys.exit(0)

    except Exception as e:
        print(f"⚠️  Ralph loop: Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
