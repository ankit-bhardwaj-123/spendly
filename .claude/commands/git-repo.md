---
description: Make Spendly its own git repository and connect it to the remote origin URL the user provides
argument-hint: <origin url>
allowed-tools: Read, AskUserQuestion, Bash(git init:*), Bash(git status:*), Bash(git rev-parse:*), Bash(git remote:*), Bash(git ls-remote:*), Bash(git add:*), Bash(git commit:*), Bash(git branch:*), Bash(git log:*), Bash(git push:*)
---

Turn this project folder (`C:\Users\Vivek Rajotia\Desktop\expense_tracker`) into its own git
repository and connect it to the user's remote.

Background: until now the only repository was the user's home folder (`C:\Users\Vivek Rajotia`).
That repo has its own `origin`, and it would expose private files (`.ssh/`, `.aws/`, `AppData/`)
if anything were pushed from it. Never run git commands that change the home-folder repo (add,
commit, remote, push). Run every command from the project folder.

## 1. Get the origin URL

- Use the URL the user passed with the command: `$ARGUMENTS`
- If that is empty, ask with AskUserQuestion: "What is the origin URL for the Spendly repo?"
  Offer the two URL formats as example options (`https://github.com/<user>/<repo>.git` and
  `git@github.com:<user>/<repo>.git`) so the user types the real one through "Other".
- Check that it looks like a git URL (`https://…`, `git@…:…` or `ssh://…`, normally ending in
  `.git`). If it doesn't, tell the user and ask again. Don't guess or fix it silently.

## 2. Check the current state

Run `git rev-parse --show-toplevel` from the project folder.

- **Output is the home folder** (`C:/Users/Vivek Rajotia`): the project has no repo of its own yet.
  Go to step 3.
- **Output is the project folder**: the project is already its own repo. Skip `git init`, show
  `git remote -v` and `git log --oneline -3`, and go to step 4.
  - If `origin` already exists with a different URL, ask before replacing it
    (`git remote set-url origin <url>`).

## 3. Initialise the repository

- `git init -b main` in the project folder.
- Read `.gitignore` and confirm it ignores at least `.venv/`, `expense_tracker.db`,
  `__pycache__/`, `*.pyc`, `.env` and `.claude/plans/`. If any are missing, tell the user and
  add them only after they agree.
- `git status --short` and review the file list. If you see anything that looks like a secret
  (`.env`, keys, tokens, `*.db`), stop and ask the user.
- `git add .` is safe here, because the repo root is the project folder, not the home folder.
- Ask for the first commit message with AskUserQuestion. Suggest
  "Initial commit: Spendly FastAPI app" and one alternative, and let the user type their own.
  Commit with that message, ending with this trailer on its own line after a blank line:

  ```
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

## 4. Connect the remote

- `git remote add origin <url>` (or `set-url` if the user approved replacing it in step 2).
- `git ls-remote origin` to check that the remote exists and the user has access.
  - Auth fails or the repo isn't found: show the error and stop. Suggest the user creates the repo
    on GitHub or signs in (`! gh auth login`).
  - The remote already has a `main` branch with commits: **don't force-push.** Tell the user and
    ask whether to stop, or to merge it in with `git pull origin main --allow-unrelated-histories`.

## 5. Push (only with confirmation)

Pushing publishes the code, so ask first with AskUserQuestion: "Push `main` to <url> now?"
Options: push now / don't push yet. On yes, run `git push -u origin main`. Never use `--force`.

## 6. Report

Print:

```
Repo:   C:\Users\Vivek Rajotia\Desktop\expense_tracker
Branch: main (<short hash> <message>)
Origin: <url>
Pushed: yes / no
```

Then remind the user:
- `CLAUDE.md` still says the repo root is the home folder. Update that Gotcha, and the `/commit-code`
  instructions that assume the home-folder root, now that the project has its own repo.
- Add a dated entry to `CHANGELOG.md` in the project (create it from the global CLAUDE.md format
  if it doesn't exist; the old one in the home folder belonged to the home-folder repo).
