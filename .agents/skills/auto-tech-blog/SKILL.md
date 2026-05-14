---
name: auto-tech-blog
description: Analyze recent git activity and Claude conversations to generate tech blog entries in Obsidian. Use for daily/weekly learning capture, reviewing discoveries, and building a personal knowledge base.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Auto Tech Blog

Analyze your recent development work and Claude Code conversations to automatically generate tech blog entries. High recall approach - capture anything potentially interesting, use hashtags for organization.

## Writing Style: Tell Stories, Not Documentation

**This is the most important section.** Blog entries must read like the Anthropic engineering blog, not like README files or documentation.

**Reference example**: https://www.anthropic.com/engineering/AI-resistant-technical-evaluations

Study this post. Notice how it:
- Opens with a concrete problem ("Evaluating technical candidates becomes harder...")
- Follows a chronological journey through multiple failed attempts
- Admits uncertainty ("I had some nagging doubt, so I double-checked")
- Uses self-aware humor ("I had a problem...")
- Ends with an open challenge, not a tidy conclusion

### The Core Principle

Every entry is a **narrative journey**: problem → struggle → discovery → open questions. The reader should feel like they're following along as you figure something out, not reading a spec sheet.

### What Good Writing Looks Like

**Good opening:**
> "I wanted something simple: type a command in Slack, have Claude analyze some business listings. What I got was a crash course in subprocess management."

**Bad opening:**
> "This post covers how to integrate a Slack bot with Claude Code using subprocess spawning."

**Good section:**
> "My first instinct was to add retry logic inline. This worked, technically. But it turned a 10-minute extraction into a 40-minute ordeal. I needed to separate 'do the work' from 'handle the failures.'"

**Bad section:**
> "## Retry Logic\n\nRetry logic can be implemented inline or via a queue. The queue approach has these benefits:\n- Faster initial runs\n- Async processing"

### Required Elements

1. **Narrative arc** - Start with what you wanted, show the struggle, reveal the discovery
2. **First person voice** - "I tried", "I realized", "I broke it"
3. **Honest failures** - Show what didn't work before showing what did
4. **Concrete details** - Actual error messages, specific numbers, real scenarios
5. **Open endings** - What's still unclear? What would you do differently?

### Forbidden Patterns

- Bullet-point lists as the primary content (use prose instead)
- "This document describes..." or "This post covers..."
- Headers like "Overview", "Introduction", "Summary"
- Dry technical explanations without narrative context
- Pretending everything worked perfectly

### Tone

- Conversational but technical
- Self-deprecating humor about mistakes is good
- Admit confusion: "I still don't fully understand why..."
- End with genuine open questions, not fake ones

### Structure

Instead of rigid templates, aim for this flow:

```
# Catchy Title (not "How to X" or "Guide to Y")

Opening hook - one paragraph that draws the reader in with a problem or surprise.

## The Naive Approach / First Attempt / The Problem
What you tried first. Why it seemed reasonable. How it failed.

## The Discovery / What Actually Worked
The insight or solution. Show the journey to get there.

## The Gotchas / Unexpected Complications
Things that broke along the way. Error messages. Debugging stories.

## Where This Leaves Me / What I'm Still Figuring Out
Honest assessment. Open questions. Future exploration.
```

The section names should be specific to the content, not generic. "The NTFS Surprise" is better than "Issue #3".

## When to Use This Skill

- `/auto-tech-blog` - Continue from last run (or 7-day lookback if first run)
- `/auto-tech-blog 3` - Force lookback of last 3 days (ignores state)
- `/auto-tech-blog --full` - Force full 7-day lookback (ignores state)
- "What interesting things did I work on this week?"
- "Generate blog entries from my recent work"

## Configuration

- **Git repos**: `~/git/`
- **Obsidian output**: `~/Documents/online-personal/Tech Blog/`
- **Conversations**: `~/.claude/projects/`
- **State file**: `~/Documents/online-personal/Tech Blog/.state.json`

## Workflow

### Step 1: Parse Arguments and Determine Lookback Mode

Parse user input to determine the lookback strategy:

1. If user provides a number (e.g., `/auto-tech-blog 3`): Use that many days, ignore state
2. If user provides `--full`: Use default 7 days, ignore state
3. Otherwise: Check state file for last run timestamp

```bash
# Read state file if it exists
STATE_FILE="/home/howis/Documents/online-personal/Tech Blog/.state.json"
if [ -f "$STATE_FILE" ]; then
  LAST_RUN=$(cat "$STATE_FILE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('last_run',''))" 2>/dev/null)
  echo "Last run: $LAST_RUN"
else
  echo "No previous run found - will use 7-day lookback"
fi
```

Set variables based on mode:
- `USE_SINCE=true` and `SINCE_DATE=<timestamp>` if continuing from last run
- `USE_SINCE=false` and `DAYS=<N>` if using days lookback

### Step 2: Gather Git Activity

Run this to collect recent commits across all repos.

**If continuing from last run** (USE_SINCE=true):
```bash
# SINCE_DATE should be the ISO timestamp from state file
for dir in /home/howis/git/*/; do
  if [ -d "$dir/.git" ]; then
    name=$(basename "$dir")
    echo "=== REPO: $name ==="

    # Get commits since last run
    git -C "$dir" log --since="$SINCE_DATE" --oneline --no-merges 2>/dev/null | head -20

    # Get diff stats for the period
    echo "--- DIFF SUMMARY ---"
    git -C "$dir" diff --stat $(git -C "$dir" rev-list -n1 --before="$SINCE_DATE" HEAD 2>/dev/null || echo HEAD~50)..HEAD 2>/dev/null | tail -10

    echo ""
  fi
done
```

**If using days lookback** (USE_SINCE=false):
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

Use the script to extract recent conversations.

**If continuing from last run** (USE_SINCE=true):
```bash
python3 /home/howis/git/auto-tech-blog/.claude/skills/auto-tech-blog/scripts/gather_conversations.py --since "$SINCE_DATE"
```

**If using days lookback** (USE_SINCE=false):
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

For each identified topic, write a narrative blog post. **Do not use templates or fill-in-the-blank structures.**

#### Creating New Entries

Create in `~/Documents/online-personal/Tech Blog/Open/{slug}.md`:

1. Start with YAML frontmatter only:
```yaml
---
status: open
created: {TODAY}
updated: {TODAY}
repos: [{repo-list}]
tags: [{auto-generated-hashtags}]
---
```

2. Then write the actual blog post as prose following the Writing Style guidelines above.

#### Example of a Good Entry

```markdown
---
status: open
created: 2026-02-03
updated: 2026-02-03
repos: [business-scout]
tags: [#python, #error-handling]
---

# When Half Your Requests Fail

The first time I ran Business Scout against a large BizBuySell search, everything looked fine. Chrome opened, listings appeared, the scraper hummed along. Then I checked the results: of 25 listings, 9 had returned "Access Denied."

Not a crash. Not an error. Just... silence.

## The Naive Fix

My first instinct was to add retry logic inline. If a request fails, wait a bit, try again.

[code snippet]

This worked, technically. But it turned a 10-minute extraction into a 40-minute ordeal...

## What I'm Still Figuring Out

The queue pattern works, but it's not smart. It waits a fixed time regardless of error type...
```

Notice: No "Overview" section. No bullet-point lists of features. Just a story.

#### Updating Existing Topics

When appending to an open topic:
1. Update the `updated:` date in frontmatter
2. Add new repos/tags if relevant
3. Append a new dated section that continues the narrative:

```markdown
---

## February 5: The Plot Thickens

Just when I thought the retry queue was working, I discovered...
```

The update should read like the next chapter of the story, not a changelog entry.

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
- Whether this was a continuation or fresh lookback

### Step 10: Save State

After successful completion, save the current timestamp to the state file:

```bash
STATE_FILE="/home/howis/Documents/online-personal/Tech Blog/.state.json"
NOW=$(date -Iseconds)
cat > "$STATE_FILE" << EOF
{
  "last_run": "$NOW",
  "last_run_human": "$(date)"
}
EOF
echo "State saved: $NOW"
```

This ensures the next run will pick up where this one left off.

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

### Content Selection
- **Be generous with what's "interesting"** - you can always close topics later
- **Link between topics** - use `[[other-topic]]` syntax for related entries

### Writing Quality
- **Tell the story of figuring it out** - not just the final solution
- **Include the failures** - what you tried that didn't work
- **Use specific details** - actual error messages, real numbers, concrete examples
- **Code snippets in context** - show them as part of the narrative, not as standalone blocks
- **End with genuine uncertainty** - what you still don't understand

### Titles
- **Catchy and specific**: "When Half Your Requests Fail" not "Retry Queue Implementation"
- **Questions work**: "Why Did My Desktop Break After a Python Update?"
- **Avoid**: "How to X", "Guide to Y", "Understanding Z"

### State Tracking
- Use `/auto-tech-blog` regularly to continue from last run
- Use `/auto-tech-blog --full` or `/auto-tech-blog N` to force a fresh lookback when needed
