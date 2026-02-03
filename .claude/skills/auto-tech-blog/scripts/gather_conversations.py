#!/usr/bin/env python3
"""
Gather recent Claude Code conversations from ~/.claude/projects/

Extracts user prompts (and optionally assistant responses) from recent sessions,
grouped by project directory.
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import argparse


CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
GIT_DIR = Path.home() / "git"


def parse_project_path(encoded_name: str) -> Optional[str]:
    """Convert encoded project directory name back to path."""
    # Format: -home-howis-git-repo-name -> /home/howis/git/repo-name
    if not encoded_name.startswith("-"):
        return None
    path = encoded_name.replace("-", "/")
    return path


def get_repo_name(encoded_name: str) -> Optional[str]:
    """Extract repo name from encoded project directory name."""
    # Format: -home-howis-git-repo-name or -home-howis-git
    git_marker = "-git-"
    git_exact = "-git"

    if git_marker in encoded_name:
        # Extract everything after -git-
        idx = encoded_name.find(git_marker)
        remainder = encoded_name[idx + len(git_marker):]
        # The repo name might have dashes, take everything up to next path separator
        # (which would be another - followed by a known path component, but usually it's the whole thing)
        return remainder if remainder else "git-root"
    elif encoded_name.endswith(git_exact):
        return "git-root"
    return None


def is_within_days(file_path: Path, days: int) -> bool:
    """Check if file was modified within the last N days."""
    cutoff = datetime.now() - timedelta(days=days)
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    return mtime >= cutoff


def is_after_timestamp(file_path: Path, since_timestamp: str) -> bool:
    """Check if file was modified after the given ISO timestamp."""
    cutoff = datetime.fromisoformat(since_timestamp.replace('Z', '+00:00').replace('+00:00', ''))
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    return mtime >= cutoff


def is_meaningful_message(content: str) -> bool:
    """Filter out noise like /clear, empty messages, command outputs."""
    if not content or len(content.strip()) < 10:
        return False

    content_stripped = content.strip()

    # Skip command invocations and system messages
    skip_patterns = [
        r'^/clear\s*$',
        r'^/compact\s',
        r'^clear\s*$',
        r'^<command-name>',
        r'^<command-message>',
        r'^<local-command',
        r'^<system-reminder>',
        r'^resume\s*$',
        r'^yes\s*$',
        r'^no\s*$',
        r'^ok\s*$',
        r'^done\s*$',
    ]
    for pattern in skip_patterns:
        if re.match(pattern, content_stripped, re.IGNORECASE):
            return False

    # Also skip if it contains command tags anywhere
    if '<command-name>' in content or '<command-message>' in content:
        return False

    return True


def extract_user_messages(jsonl_path: Path, include_assistant: bool = False) -> list[dict]:
    """Extract messages from a conversation JSONL file."""
    messages = []

    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)

                    # Skip meta messages
                    if entry.get("isMeta"):
                        continue

                    entry_type = entry.get("type", "")
                    message_data = entry.get("message", {})

                    # User messages
                    if entry_type == "user":
                        content = message_data.get("content", "")
                        if isinstance(content, str) and is_meaningful_message(content):
                            messages.append({
                                "role": "user",
                                "content": content,
                                "timestamp": entry.get("timestamp"),
                                "cwd": entry.get("cwd", "")
                            })

                    # Assistant messages (if requested)
                    elif include_assistant and entry_type == "assistant":
                        content_blocks = message_data.get("content", [])
                        if isinstance(content_blocks, list):
                            text_parts = []
                            for block in content_blocks:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    text_parts.append(block.get("text", ""))
                            if text_parts:
                                full_text = "\n".join(text_parts)
                                # Truncate long responses
                                if len(full_text) > 500:
                                    full_text = full_text[:500] + "..."
                                messages.append({
                                    "role": "assistant",
                                    "content": full_text,
                                    "timestamp": entry.get("timestamp")
                                })

                except json.JSONDecodeError:
                    continue

    except Exception as e:
        print(f"  Error reading {jsonl_path}: {e}", file=sys.stderr)

    return messages


def gather_conversations(days: int = 7, since: str = None, include_assistant: bool = False) -> dict:
    """
    Gather recent conversations grouped by project/repo.

    Args:
        days: Look back N days (used if since is not provided)
        since: ISO timestamp to look back from (overrides days if provided)
        include_assistant: Include assistant responses

    Returns:
        dict: {repo_name: [list of conversation summaries]}
    """
    results = {}

    if not CLAUDE_PROJECTS_DIR.exists():
        print(f"Claude projects directory not found: {CLAUDE_PROJECTS_DIR}", file=sys.stderr)
        return results

    # Iterate through project directories
    for project_dir in CLAUDE_PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue

        repo_name = get_repo_name(project_dir.name)
        if not repo_name:
            continue  # Skip non-git projects

        # Find recent conversation files
        for jsonl_file in project_dir.glob("*.jsonl"):
            if jsonl_file.name == "sessions-index.json":
                continue

            # Use timestamp if provided, otherwise use days
            if since:
                if not is_after_timestamp(jsonl_file, since):
                    continue
            elif not is_within_days(jsonl_file, days):
                continue

            messages = extract_user_messages(jsonl_file, include_assistant)

            if messages:
                if repo_name not in results:
                    results[repo_name] = []

                # Get file modification time for sorting
                mtime = datetime.fromtimestamp(jsonl_file.stat().st_mtime)

                results[repo_name].append({
                    "session_id": jsonl_file.stem,
                    "date": mtime.strftime("%Y-%m-%d %H:%M"),
                    "messages": messages
                })

    # Sort conversations by date within each repo
    for repo in results:
        results[repo].sort(key=lambda x: x["date"], reverse=True)

    return results


def print_conversations(conversations: dict, verbose: bool = False):
    """Print gathered conversations in a readable format."""

    if not conversations:
        print("No recent conversations found in git projects.")
        return

    for repo, sessions in sorted(conversations.items()):
        print(f"\n{'='*60}")
        print(f"REPO: {repo}")
        print(f"{'='*60}")

        for session in sessions:
            print(f"\n--- Session: {session['date']} ---")

            for msg in session["messages"]:
                role_prefix = "USER:" if msg["role"] == "user" else "ASSISTANT:"
                content = msg["content"]

                # Truncate long messages for overview
                if not verbose and len(content) > 300:
                    content = content[:300] + "..."

                # Skip /clear and other short commands
                if content.strip() in ["/clear", "clear", "/compact"]:
                    continue

                print(f"\n{role_prefix}")
                print(content)


def main():
    parser = argparse.ArgumentParser(description="Gather recent Claude Code conversations")
    parser.add_argument("--days", type=int, default=7, help="Look back N days (default: 7)")
    parser.add_argument("--since", type=str, help="ISO timestamp to look back from (overrides --days)")
    parser.add_argument("--include-assistant", action="store_true", help="Include assistant responses")
    parser.add_argument("--verbose", action="store_true", help="Show full message content")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    conversations = gather_conversations(args.days, args.since, args.include_assistant)

    if args.json:
        print(json.dumps(conversations, indent=2, default=str))
    else:
        print_conversations(conversations, args.verbose)


if __name__ == "__main__":
    main()
