---
name: local-plan
description: Use in a chat when the owner wants to write the ExecPlan of the next pull request of a GitHub issue of this repository as a file in a draft pull request, or to change the plan in a pull request.
---

# Planning in a chat

An ExecPlan is a self-contained, living design-and-implementation document. Here it is one Markdown file in `docs/execplans/`, in the draft pull request that will implement it, so the owner reviews the plan as a pull request. The owner is in this chat: ask, never guess.

Write and change a plan with the skill `effect-brewery:execplans`: read its `SKILL.md` and `references/PLANS.md` in full before you start, follow them to the letter, and start a new plan from the skeleton of `references/PLANS.md`. Be thorough in reading (and re-reading) source material. When a design has challenging requirements or significant unknowns, use milestones with proofs of concept. If that skill is not available, tell the owner to install the plugin `effect-brewery`, and stop.

- A new plan file is `docs/execplans/YYYYMMDD-NN-<brief-description>.md`: today's date (UTC), and NN is one more than the highest counter of that date in `docs/execplans/`, or `01`.
- In place of the skeleton's paragraph about PLANS.md, write: "This document must be maintained in accordance with `references/PLANS.md` of the skill `execplans` of the plugin `effect-brewery`." Then a line `Issue: #<n>`, or `Issue: none` for a plan without an issue.

## Rules that always apply

- Work in the repository of the current checkout. One plan per pull request, for one smallest coherent vertical slice.
- The default branch is the output of `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`. This skill writes `<default branch>` for it.
- The repository's checks are the commands that its CLAUDE.md, README, or CI workflow name for validating a change, for example a `make check` target. Run them before each push. If the repository names none, tell the owner.
- Change and commit only the plan file.
- Never edit the issue. Propose changes to its scope or acceptance criteria in the chat.
- A question is an open question that the issue lists, or a gap or contradiction that makes an acceptance criterion impossible to verify. Ask the owner, one question at a time, and record each answer in the Decision Log. Everything else is a design decision: decide it, and record it with its reason in the Decision Log.
- With an issue, restate its acceptance criteria in Validation and Acceptance, without checkboxes. Without one, the plan states its own goal in Purpose.
- Never resolve a review thread, mark the pull request ready, or merge it: that is the owner's step.
- Post no status comment. Tell the owner in the chat what you did, with the URLs.

## Titles and commit subjects

GitHub squash-merges a pull request into one commit on the default branch and appends ` (#<pull request>)` to its subject. So a title or a commit subject never carries an issue or pull request number in any form. Title the pull request with one statement of the outcome that the plan delivers, in the imperative, for example "Show the build duration in the checks summary". Give each commit a subject that says what it changes, for example "Add the ExecPlan to show the build duration in the checks summary".

To check a pull request, run this command with its number. It prints one line for each title or commit subject that has a number, and nothing when all are clean. A number is `#` followed by a digit, or one of the words `plan`, `issue`, `PR`, or `pull request`, white space, and a digit, in any case. The first line makes the command fail when `gh` fails: if the command exits with an error, report the error, and stop. No output means that all are clean only when the command exits without an error.

```bash
set -o pipefail
gh pr view <pull request> --json title,commits | jq -r '
  def bad: test("#[0-9]|(^|[^\\p{L}\\p{M}\\p{Nd}\\p{Pc}])(plan|issue|pr|pull\\p{White_Space}+request)\\p{White_Space}+[0-9]"; "i");
  (select(.title | bad) | "title    \(.title)"),
  (.commits[] | select(.messageHeadline | bad) | "\(.oid[0:7])  \(.messageHeadline)")'
```

## Find the pull requests of an issue

```bash
set -o pipefail
gh pr list --state all --limit 1000 --json number,state,title,body \
  | jq -r --arg n "<n>" '[.[] | select((.body // "") | test("(^|\n)Part of #" + $n + "([^0-9]|$)"))] | sort_by(-.number) | .[] | "#\(.number) \(.state) \(.title)"'
```

The command prints one line for each pull request whose body has a line that starts with `Part of #<n>`, newest first, as `#<number> <STATE> <title>`. The state is OPEN, MERGED, or CLOSED. A pull request that is CLOSED did not merge, and it does not count. The command prints nothing when the issue has no pull request. It lists pull requests and does not search them, because a search can miss a pull request that was just opened. The first line makes the command fail when `gh` fails: if the command exits with an error, report the error, and stop. An empty output means that the issue has no pull request only when the command exits without an error.

## Plan an issue

1. Check that the issue is open: `gh issue view <n> --json state --jq .state` prints `OPEN`. If it does not, tell the owner, and stop. Then run the command in "Find the pull requests of an issue", and take the first rule below that fits:
   - A listed pull request is OPEN: tell the owner "#<p> is open. The next pull request starts after it is merged.", and stop. To change that pull request's plan, see "Change a plan".
   - Three or more listed pull requests are MERGED: the issue is too big. If a comment of the issue already starts with `This issue is too big:` (this command prints its id: `gh api "repos/{owner}/{repo}/issues/<n>/comments" --paginate --jq '.[] | select(.body | startswith("This issue is too big:")) | .id'`), tell the owner, and stop. Otherwise write the comment to a file outside the repository: the line `This issue is too big: it already has three pull requests.`, an empty line, one line `- #<p> <title>` for each merged pull request, an empty line, and the line `Split it into smaller issues.`. Post it with `gh issue comment <n> --body-file <file>`, tell the owner, and stop.
   - The newest MERGED pull request left an unfinished plan: follow "Read the plan of a merged pull request". When it names an unfinished file, revise that file and keep its name. This continues the plan; the pull request is the next one of the issue.
   - Otherwise, write a new plan file.
2. Read the issue with all its comments (`gh issue view <n> --comments`), and research the repository without changing it. Ask each question before you write the part that depends on it.
3. Ask the owner for the template of the branch name, for example `feature/*`, unless the owner gave it in this chat. Never choose a branch name without it: the repository's CI/CD may run only on branches that match a template. Make a name from it, with a short name of the plan in its variable part, for example `feature/build-duration`. These commands print nothing when the name is new: `git branch --list "<branch>"; git ls-remote --heads origin "<branch>"`. If one prints a line, choose another short name. Create the branch from an up-to-date default branch: `git switch <default branch> && git pull --ff-only && git switch -c "<branch>"`.
4. Write the plan in full, commit it, run the repository's checks, and push with `git push -u origin HEAD`.
5. Open the draft pull request: `gh pr create --draft --base <default branch> --title "<title>" --body-file <file>`, with a short summary of the plan and the line `Part of #<n>` on a line of its own. Add no label. Run the title check for the new pull request; if it prints a line, fix the title with `gh pr edit <number> --title "<title>"`.

A plan without an issue works the same way without step 1: the header says `Issue: none`, and the body has no `Part of` line.

### Read the plan of a merged pull request

Take the newest MERGED pull request, number <p>. List the plan files that it added, changed, or renamed:

```bash
gh api "repos/{owner}/{repo}/pulls/<p>/files" --paginate --jq '.[] | select(.status == "added" or .status == "modified" or .status == "renamed") | .filename | select(startswith("docs/execplans/") and endswith(".md"))'
```

For each file it prints, in that order, read the file as it is on the default branch and test whether its plan is finished. A plan is finished when it has a `## Progress` section and no line of that section is an unchecked box (`- [ ]`, `* [ ]`, or `+ [ ]`, indented or not). The command prints `finished` or `not finished`:

```bash
text=$(gh api -H "Accept: application/vnd.github.raw+json" "repos/{owner}/{repo}/contents/<file>?ref=<default branch>") &&
  printf '%s\n' "$text" | awk '
    /^## Progress[ \t\r]*$/ { seen = 1; inp = 1; next }
    /^# / || /^## /         { inp = 0; next }
    inp && /^[ \t]*[-*+][ \t]+\[ \]/ { open = 1 }
    END { print (seen && !open) ? "finished" : "not finished" }'
```

When `gh` fails with `HTTP 404`, the file is no longer on the default branch: print nothing, and go to the next file. For any other `gh` error, tell the owner, and stop. The first file that is `not finished` is the plan to continue. When no file is `not finished`, or the pull request changed no plan file, the next plan is a new one.

## Change a plan

1. Check out the pull request with `gh pr checkout <p>`. Read the plan file, the issue if there is one, and the pull request's comments, reviews, and inline review comments (`gh pr view <p> --comments`, `gh api repos/{owner}/{repo}/pulls/<p>/comments --paginate`).
2. Make the change that the owner asks for, or address the review. Record each answer and decision in the Decision Log, update every section that the change affects, Progress, and Revision Notes.
3. Commit, run the repository's checks, and push. Reply to each review comment on its own, in its thread (an inline comment gets an inline reply: write the reply to a file outside the repository, and post it with `gh api repos/{owner}/{repo}/pulls/<p>/comments/<id>/replies -F body=@<file>`). Say what you changed and in which commit, or why you changed nothing.

## Publication

The owner's request to plan an issue or to change a plan is the approval to push, to open the pull request, and to post the comment that "Plan an issue" describes. If the owner asks only for a draft, show it and stop.
