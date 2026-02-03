---
name: auto-tech-blog
description: Analyze recent git activity and Claude conversations to generate tech blog entries in Obsidian. Use for daily/weekly learning capture, reviewing discoveries, and building a personal knowledge base.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Auto Tech Blog

Analyze your recent development work and Claude Code conversations to automatically generate tech blog entries. High recall approach - capture anything potentially interesting, use hashtags for organization.

## When to Use This Skill

- `/auto-tech-blog` - Run with default 7-day lookback
- `/auto-tech-blog 3` - Analyze last 3 days
- `/auto-tech-blog 14` - Analyze last 2 weeks
- "What interesting things did I work on this week?"
- "Generate blog entries from my recent work"

## Configuration

- **Git repos**: `~/git/`
- **Obsidian output**: `~/Documents/online-personal/Tech Blog/`
- **Conversations**: `~/.claude/projects/`

## Workflow

### Step 1: Parse Arguments

Extract the days parameter from user input. Default to 7 days if not specified.

### Step 2: Gather Git Activity

Run this to collect recent commits across all repos:

```bash
DAYS=${DAYS:-7}
SINCE_DATE=$(date -d "$DAYS days ago" +%Y-%m-%d)

for dir in /home/howis/git/*/; do
  if [ -d "$dir/.git" ]; then
    name=$(basename "$dir")
    echo "=== REPO: $name ==="

    # Get commits in date range
    git -C "$dir" log --since="$SINCE_DATE" --oneline --no-merges 2>/dev/null | head -20

    # Get diff stats for the period
    echo "--- DIFF SUMMARY ---"
    git -C "$dir" diff --stat $(git -C "$dir" rev-list -n1 --before="$SINCE_DATE" HEAD 2>/dev/null || echo HEAD~50)..HEAD 2>/dev/null | tail -10

    echo ""
  fi
done
```

### Step 3: Gather Claude Conversations

Use the script to extract recent conversations:

```bash
python3 /home/howis/git/auto-tech-blog/.claude/skills/auto-tech-blog/scripts/gather_conversations.py --days $DAYS
```

This outputs user prompts from recent sessions, grouped by project.

### Step 4: Read Existing Blog State

Check the current state of blog topics:

```bash
# List open topics
ls -la "/home/howis/Documents/online-personal/Tech Blog/Open/" 2>/dev/null || echo "No open topics yet"

# Read the index
cat "/home/howis/Documents/online-personal/Tech Blog/_index.md" 2>/dev/null || echo "No index yet"
```

### Step 5: Analyze and Identify Topics

Review the gathered data and identify:

**What makes something "interesting" (high recall):**
- New library or tool usage
- Bug fixes (especially tricky ones)
- Architectural decisions or refactors
- Performance optimizations
- Testing patterns
- Configuration/DevOps discoveries
- Problem-solving approaches
- Anything you'd want to remember in 6 months

**Topic identification:**
- Group related commits/conversations into coherent topics
- Check if topic relates to an existing open blog entry
- If related to open topic → append new insights
- If new topic → create new entry

### Step 6: Generate/Update Blog Entries

For each identified topic:

#### New Topic Template

Create in `~/Documents/online-personal/Tech Blog/Open/{slug}.md`:

```markdown
---
status: open
created: {TODAY}
updated: {TODAY}
repos: [{repo-list}]
tags: [{auto-generated-hashtags}]
---

# {Catchy Title}

> Brief one-liner summary of the discovery/topic

## The Context

What were you trying to do? What problem arose?

## The Discovery

What did you learn? What technique/pattern/solution emerged?

## Code Highlights

```{language}
// Key code snippets that illustrate the point
```

## Key Takeaways

- Bullet points of main lessons
- Things to remember for next time

## Open Questions

- Any unresolved aspects?
- Future exploration ideas?
```

#### Updating Existing Topics

When appending to an open topic:
1. Update the `updated:` date in frontmatter
2. Add new repos to the list if relevant
3. Add new tags if applicable
4. Append a new section with date header:

```markdown
---

## Update: {DATE}

New insights discovered...
```

### Step 7: Consider Closing Topics

A topic might be ready to close when:
- The problem is fully solved
- You've moved on and unlikely to add more
- It's been open for a while with no updates

To close a topic:
1. Move from `Open/` to `Closed/`
2. Rename with date prefix: `2026-02-03-{slug}.md`
3. Change `status: open` to `status: closed`
4. Add a "Final Thoughts" section if appropriate

Ask the user: "These topics look complete - should I close them?"

### Step 8: Update Index

Update `~/Documents/online-personal/Tech Blog/_index.md`:

```markdown
# Tech Blog Index

Personal learning journal auto-generated from development work.

## Open Topics

| Topic | Started | Last Updated | Repos |
|-------|---------|--------------|-------|
| [[Open/topic-slug]] | 2026-02-01 | 2026-02-03 | repo1, repo2 |

## Recently Closed

| Topic | Period | Tags |
|-------|--------|------|
| [[Closed/2026-02-03-topic]] | Jan 15 - Feb 3 | #python #testing |

## Stats

- **Open topics**: X
- **Closed this month**: Y
- **Last updated**: {NOW}
```

### Step 9: Summary

Provide a summary to the user:
- Topics created/updated
- Suggested topics to close
- Any interesting patterns noticed across the work

## Hashtag Generation

Auto-generate tags based on:

**Languages** (from file extensions in diffs):
- `.py` → `#python`
- `.rs` → `#rust`
- `.ts/.tsx` → `#typescript`
- `.go` → `#go`
- `.sh` → `#bash`

**Frameworks/Tools** (from imports, configs, commit messages):
- `ortools` → `#or-tools`
- `pytest` → `#testing`
- `docker` → `#docker`
- `supabase` → `#supabase`
- `marimo` → `#notebooks`

**Concepts** (from content analysis):
- optimization problems → `#optimization`
- API work → `#api`
- database changes → `#database`
- CI/CD → `#devops`
- error handling → `#error-handling`

## Directory Setup

If the blog directory doesn't exist, create it:

```bash
mkdir -p "/home/howis/Documents/online-personal/Tech Blog/Open"
mkdir -p "/home/howis/Documents/online-personal/Tech Blog/Closed"
```

## Tips

- **Be generous with what's "interesting"** - you can always close topics later
- **Link between topics** - use `[[other-topic]]` syntax for related entries
- **Don't overthink titles** - catchy but descriptive is the goal
- **Code snippets matter** - include actual code, not just descriptions
- **Capture the "why"** - future you wants to know the reasoning
