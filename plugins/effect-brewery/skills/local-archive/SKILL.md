---
name: local-archive
description: Use in a chat when the owner wants to move the finished ExecPlans of this repository from docs/execplans/ to docs/execplans/archived/, in a pull request that holds only the moves.
---

# Archiving finished ExecPlans in a chat

An ExecPlan is a self-contained, living design-and-implementation document, kept as one Markdown file in `docs/execplans/`. The skills `local-plan` and `local-implement` write one for each pull request, and the file stays in that directory after its work is finished. This skill moves each finished ExecPlan to `docs/execplans/archived/`, with the same content, in one pull request that contains only the moves. The owner is in this chat: ask, never guess.

## Rules that always apply

- Work in the repository of the current checkout. Its remote on GitHub is `origin`. Run every command from the top folder of the checkout, the output of `git rev-parse --show-toplevel`.
- The default branch is the output of `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`. This skill writes `<default branch>` for it.
- Move only the files that "Find the finished plans" lists. Never change the content of a file, never move, change, or delete any other file, and never overwrite a file.
- Never push to the default branch. The moves reach it only through the pull request, which the owner reviews and merges.
- The pull request body never has a line that starts with `Part of #`. The skills `local-plan`, `local-implement`, and `local-wrap-up` link a pull request to an issue with that line, and an archive pull request belongs to no issue.
- Run each command as it is written. Replace only the parts in angle brackets and the names of the files of the last rule. The commands work in bash and in zsh.
- If a command exits with an error, report the error, and stop.
- Post no comment. Tell the owner in the chat what you did, with the URL of the pull request.
- Keep the lists and the pull request body in files outside the repository, such as in the session scratchpad directory. This skill writes `LIST_FILE`, `NAMES_FILE`, `MOVES_FILE`, and `BODY_FILE` for these files. Remove them when you are done.

## Finished ExecPlans

A file is an ExecPlan when it is a Markdown file directly in `docs/execplans/` and it has a line that starts with `This ExecPlan is a living document.` before its first `## ` heading. That line opens the skeleton of `references/PLANS.md` of the skill `execplans` of the plugin `effect-brewery`. An ExecPlan is finished when it has a `## Progress` section and no line of that section is an unchecked box (`- [ ]`, `* [ ]`, or `+ [ ]`, indented or not). This is the rule of `local-plan`.

Every other file stays where it is and does not change: for example `AGENTS.md`, a notes file, a plan in another format, an ExecPlan with an unchecked box, and every file in a subdirectory of `docs/execplans/`.

## Check the start

1. The checkout must have no change to a tracked file, because this skill switches branches and commits in it. This command must print nothing:

   ```bash
   git status --porcelain --untracked-files=no
   ```

   When it prints a line, tell the owner that the checkout has changes, and stop.
2. No archive pull request may be open, because a second one would move the same plans again. This command prints one line for each open pull request with the title of an archive pull request, and nothing when there is none:

   ```bash
   set -o pipefail
   gh pr list --state open --limit 1000 --json number,title,url \
     | jq -r '.[] | select(.title == "Move finished ExecPlans into docs/execplans/archived/") | "#\(.number) \(.url)"'
   ```

   When it prints a line, tell the owner "#<p> is open. The next archive starts after it is merged or closed.", and stop.
3. Fetch the default branch:

   ```bash
   git fetch origin <default branch>
   ```

## Find the finished plans

This command reads `docs/execplans/` on the fetched default branch, and writes the path of each finished ExecPlan to `LIST_FILE`, one per line:

```bash
set -o pipefail
git -c core.quotePath=false ls-tree "origin/<default branch>" -- docs/execplans/ \
  | awk -F '\t' '$(1) ~ / blob / && $(2) ~ /^docs\/execplans\/[^\/]+\.md$/ { print $(2) }' \
  | while IFS= read -r f; do
      if git show "origin/<default branch>:$f" | awk '
           /^## / { head = 1 }
           !head && /^This ExecPlan is a living document\./ { plan = 1 }
           /^## Progress[ \t\r]*$/ { seen = 1; inp = 1; next }
           /^# / || /^## /         { inp = 0; next }
           inp && /^[ \t]*[-*+][ \t]+\[ \]/ { open = 1 }
           END { exit !(plan && seen && !open) }'
      then printf '%s\n' "$f"; fi
    done > LIST_FILE
```

When `LIST_FILE` is empty, there is no finished ExecPlan to move: tell the owner, and stop. Create no branch, and open no pull request. When the owner asked only for the list, show it, and stop.

## Move the plans

1. Ask the owner for the template of the branch name, for example `feature/*`, unless the owner gave it in this chat. Never choose a branch name without it: the repository's CI/CD may run only on branches that match a template. Make a name from it, with `archive-execplans-` and the UTC time of `date -u +%Y%m%d-%H%M%S` in its variable part, for example `feature/archive-execplans-20261018-120000`. This skill writes `<branch>` for it. Create the branch from the fetched default branch:

   ```bash
   git switch --no-track -c "<branch>" "origin/<default branch>"
   ```
2. Move each file of `LIST_FILE` with `git mv`, and write each move to `MOVES_FILE` as a line `<from> -> <to>`. A plan keeps its file name. When `docs/execplans/archived/` already has a file with that name, the plan gets the first free name with a counter before `.md`: `-2`, then `-3`, and so on.

   ```bash
   mkdir -p docs/execplans/archived && (
     while IFS= read -r f; do
       base=${f##*/}; stem=${base%.md}; to="docs/execplans/archived/$base"; i=2
       while [ -e "$to" ] || [ -L "$to" ]; do to="docs/execplans/archived/$stem-$i.md"; i=$((i + 1)); done
       git mv -- "$f" "$to" || exit 1
       printf '%s -> %s\n' "$f" "$to"
     done < LIST_FILE > MOVES_FILE
   )
   ```
3. Check the change. This command prints the number of staged changes and the number of lines of `LIST_FILE`, and exits with an error unless every staged change is a rename into `docs/execplans/archived/` with the same content, one for each line:

   ```bash
   set -o pipefail
   git -c core.quotePath=false diff --cached --name-status -M100% \
     | awk -F '\t' -v want="$(wc -l < LIST_FILE)" '
         $(1) != "R100" || $(3) !~ /^docs\/execplans\/archived\// { bad = 1 }
         { n++ }
         END { print n + 0, "of", want + 0; exit (bad || n != want + 0) }'
   ```

   When it exits with an error, do not commit: tell the owner, and stop.
4. List the files outside `docs/execplans/archived/` that name a moved plan by its file name. The moves change no link, so the owner may want to fix these files later. This command prints nothing when no file names a moved plan:

   ```bash
   sed 's|.*/||' LIST_FILE > NAMES_FILE &&
     { git -c core.quotePath=false grep -l -F -f NAMES_FILE -- . ':(exclude)docs/execplans/archived/'; [ $? -le 1 ]; }
   ```
5. Commit, and push the branch:

   ```bash
   git commit -m "Move finished ExecPlans into docs/execplans/archived/" && git push -u origin HEAD
   ```

## Open the pull request

1. Write the body to `BODY_FILE`, with each paragraph and list item on one line:
   - the line `This pull request moves each finished ExecPlan from docs/execplans/ to docs/execplans/archived/, with the same content. It contains only these moves:`
   - an empty line, and one line `` - `<from>` → `<to>` `` for each line of `MOVES_FILE`. When the file name of `<to>` differs from the file name of `<from>`, add ` (new name, because the old name is taken)`.
   - an empty line, and either the line `These files name a moved plan, and their links are not changed:` and one line `` - `<file>` `` for each file of step 4 of "Move the plans", or the line `No other file names a moved plan.`

   Then check it. This command must print nothing:

   ```bash
   ! grep -n '^Part of #' BODY_FILE
   ```
2. Open the pull request. It is complete, so it is not a draft:

   ```bash
   gh pr create --base <default branch> --head <branch> --title "Move finished ExecPlans into docs/execplans/archived/" --body-file BODY_FILE
   ```

   It prints the URL of the pull request.

## Report

Tell the owner: the URL of the pull request, each move, each plan that got a new name and the name that was taken, the files that name a moved plan, and that the checkout is on `<branch>`. Never merge the pull request: that is the owner's step.

## Publication

The owner's request to archive is the approval to create the branch, to commit, to push, and to open the pull request. If the owner asks only for the list, show it, and stop.
