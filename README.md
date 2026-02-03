# Auto Tech Blog

A Claude Code skill that automatically generates tech blog entries from your daily development work. Analyzes git commits and Claude Code conversations to capture learnings, discoveries, and interesting patterns.

## Features

- **Git activity analysis** - Scans commits and diffs across all repos in `~/git/`
- **Conversation mining** - Extracts insights from Claude Code sessions
- **High recall approach** - Captures anything potentially interesting, uses hashtags for organization
- **Topic lifecycle** - Tracks open (developing) vs closed (complete) topics
- **Obsidian integration** - Writes directly to your Obsidian vault

## Installation

The skill is installed via symlink to `~/.claude/skills/`:

```bash
ln -sf /home/howis/git/auto-tech-blog/.claude/skills/auto-tech-blog ~/.claude/skills/auto-tech-blog
```

## Usage

```bash
/auto-tech-blog      # Analyze last 7 days (default)
/auto-tech-blog 3    # Analyze last 3 days
/auto-tech-blog 14   # Analyze last 2 weeks
```

## Output Structure

```
~/Documents/online-personal/Tech Blog/
├── _index.md     # Dashboard of all topics
├── Open/         # Active topics being developed
│   └── topic-slug.md
└── Closed/       # Completed topics
    └── 2026-02-03-topic-slug.md
```

## Blog Entry Format

Each entry includes:
- Frontmatter with status, dates, repos, and auto-generated hashtags
- Context section (what you were trying to do)
- Discovery section (what you learned)
- Code highlights
- Key takeaways
- Open questions

## Configuration

Edit `.claude/skills/auto-tech-blog/SKILL.md` to customize:
- Git repos directory (default: `~/git/`)
- Obsidian output path (default: `~/Documents/online-personal/Tech Blog/`)
- Hashtag generation rules

## Scripts

- `scripts/gather_conversations.py` - Extracts user prompts from Claude Code conversation history

```bash
# Standalone usage
python3 scripts/gather_conversations.py --days 7
python3 scripts/gather_conversations.py --days 3 --include-assistant
python3 scripts/gather_conversations.py --json  # Output as JSON
```

## How It Works

1. Gathers recent git commits and diff summaries
2. Extracts your prompts from Claude Code sessions
3. Analyzes content for interesting patterns and learnings
4. Creates new topic entries or appends to existing open topics
5. Suggests closing topics that appear complete
6. Updates the index dashboard
