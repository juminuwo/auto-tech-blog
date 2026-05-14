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

~/Documents/online-personal/Tech Blog/
├── .state.json           # Tracks last run timestamp for incremental updates
├── _index.md             # Dashboard/index of all topics
├── Open/                 # Active topics being developed
└── Closed/               # Completed topics with date prefix
```

## Conversation Data Source

Claude Code stores conversations in `~/.claude/projects/` with directory names encoded as:
- `-home-howis-git-repo-name` → conversations for that repo
- `-home-howis-git` → conversations from the parent git directory

JSONL format with `type: "user"` and `type: "assistant"` entries.

## Workflow When Skill Runs

1. Parse arguments and check `.state.json` for last run timestamp
2. Determine lookback mode:
   - If `--days N` or `--full` provided: use days-based lookback
   - If state file exists: continue from last run timestamp
   - Otherwise: use default 7-day lookback
3. Run bash loop to gather git commits/diffs since cutoff
4. Run `gather_conversations.py --since` or `--days` to extract prompts
5. Read existing blog state (open topics, index)
6. Identify interesting content (high recall)
7. Generate/update markdown files in Obsidian
8. Update index dashboard
9. Save current timestamp to `.state.json`
10. Summarize changes to user

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
