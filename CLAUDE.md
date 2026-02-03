# Auto Tech Blog - Claude Context

## Project Overview

A Claude Code skill that generates tech blog entries from development activity. Analyzes git diffs and Claude conversations to capture learnings in Obsidian.

## Key Paths

- **Skill definition**: `.claude/skills/auto-tech-blog/SKILL.md`
- **Conversation script**: `.claude/skills/auto-tech-blog/scripts/gather_conversations.py`
- **Output directory**: `~/Documents/online-personal/Tech Blog/`
- **Symlink**: `~/.claude/skills/auto-tech-blog` -> this repo

## Architecture

```
.claude/skills/auto-tech-blog/
├── SKILL.md              # Main skill instructions (Claude reads this)
├── scripts/
│   └── gather_conversations.py   # Python script to extract conversations
└── templates/
    ├── post.md.template          # Blog post structure
    └── index.md.template         # Index page structure
```

## Conversation Data Source

Claude Code stores conversations in `~/.claude/projects/` with directory names encoded as:
- `-home-howis-git-repo-name` → conversations for that repo
- `-home-howis-git` → conversations from the parent git directory

JSONL format with `type: "user"` and `type: "assistant"` entries.

## Workflow When Skill Runs

1. Parse `--days N` argument (default 7)
2. Run bash loop to gather git commits/diffs from all repos
3. Run `gather_conversations.py` to extract recent prompts
4. Read existing blog state (open topics, index)
5. Identify interesting content (high recall)
6. Generate/update markdown files in Obsidian
7. Update index dashboard
8. Summarize changes to user

## Design Decisions

- **High recall, low precision**: Capture more, filter later via hashtags
- **Additive updates**: New runs append insights, don't regenerate
- **Stepped conversation analysis**: Start with user prompts, fetch assistant responses if needed
- **Topic lifecycle**: Open while developing, closed when complete
- **Manual invocation**: No cron yet, run when desired

## Hashtag Generation

Auto-generated from:
- File extensions in diffs (`.py` → `#python`)
- Imports/configs (`ortools` → `#or-tools`)
- Content analysis (optimization → `#optimization`)
