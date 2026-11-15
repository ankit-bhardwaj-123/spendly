---
description: Commit the current Spendly changes with a commit message the user provides
argument-hint: [commit message]
allowed-tools: Read, AskUserQuestion, Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git add:*), Bash(git commit:*)
---

Commit the changes in this project (`Desktop/expense_tracker`) to git.

IMPORTANT: the git repository root is the user's home folder (`C:\Users\Vivek Rajotia`), not
this project, so `git status` lists hundreds of unrelated files. Only ever stage paths inside
this project. Never run `git add -A`, `git add .` from the home folder, or `git commit -a`.

## 1. See what changed

Run these and read the output:

- `git status --short -- .` (from the project folder; shows only this project)
- `git diff -- .` and `git diff --cached -- .`
- `git log --oneline -5` (may be empty: the repo can have no commits yet)

If nothing in this project has changed, say so and stop.

Check the list for files that must not be committed: `.venv/`, `expense_tracker.db`,
`__pycache__/`, `.env`, `.claude/plans/` (all in `.gitignore`), or anything that looks like a
secret. Leave them out and tell the user.

## 2. Get the commit message from the user

- If the user passed a message with the command, use it as is: `$ARGUMENTS`
- If that is empty, ask with the AskUserQuestion tool. Write a question that lists the files
  about to be committed and asks "What commit message should I use?". Give 2 short
  suggested messages drafted from the diff (imperative, under 72 characters, e.g.
  "Add SQLite data layer and startup seeding") as options; the user can pick one or type
  their own through "Other".
- Never commit with a message the user did not pick or write.

In the same AskUserQuestion call, if `C:\Users\Vivek Rajotia\CHANGELOG.md` changed, ask whether
to include it (it is shared by every project in the home folder, so it may hold other projects'
entries).

## 3. Commit

- Stage only the project's changed files by explicit path, for example
  `git add -- "Desktop/expense_tracker/main.py" "Desktop/expense_tracker/database/db.py"`
  (quote paths, the folders contain spaces). Add `CHANGELOG.md` only if the user said yes.
- Commit with the user's message, and end it with the attribution trailer on its own line after a
  blank line:

  ```
  <user's message>

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

- If a pre-commit hook fails, show the error and fix the cause; never use `--no-verify`.
- Do not push, amend, or create a branch unless the user asks.

## 4. Report

Print the short commit hash, the message, and the list of committed files
(`git show --stat --oneline HEAD`).
