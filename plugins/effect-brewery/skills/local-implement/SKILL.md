---
name: local-implement
description: Use in a chat when the owner wants to implement the ExecPlan file of a pull request of this repository, or continue that pull request.
---

# Implementing an ExecPlan in a chat

An ExecPlan is a self-contained, living design-and-implementation document. Here it is one Markdown file in `docs/execplans/`, in the pull request that implements it. Keep it by the rules of the skill `effect-brewery:execplans`: read its `SKILL.md` and `references/PLANS.md` before you change the plan. If that skill is not available, tell the owner to install the plugin `effect-brewery`, and stop. The owner is in this chat: ask, never guess.

## Rules that always apply

- Work in the repository of the current checkout. One plan, one pull request.
- The default branch is the output of `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`. This skill writes `<default branch>` for it.
- The repository's checks are the commands that its CLAUDE.md, README, or CI workflow name for validating a change, for example a `make check` target. Run them before each push. If the repository names none, tell the owner.
- Never change the issue. Never add a second plan file to the pull request.
- Keep the plan's Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective current, in the same commits as the code.
- A question is an ambiguity that changes what the plan delivers or how it is accepted, and that the plan, the issue, and the repository cannot settle. Ask the owner, one question at a time. Everything else is a design decision: decide it, and record it with its reason in the plan's Decision Log.
- Use the skill `effect-brewery:the-architect` only when a milestone adds or reshapes the structure of the code of an application or service: new or changed modules, interfaces, contracts, or ways that errors cross a boundary. Use it before you write that code, for the design decisions that the plan leaves open. Do not use it for a feature that fits inside the existing structure, for scripts, for CI/CD and workflow files, for infrastructure or configuration, or for documentation. If a milestone mixes these, use it for the application part only. The plan and the owner's review feedback still win over the skill: if the skill shows that the plan's design is wrong, ask the owner. If the skill is not available, go on without it, and tell the owner.
- The owner's review feedback is a requirement for this pull request. If it contradicts the plan, follow the feedback, and record the change in the Decision Log.
- Never resolve a review thread, mark the pull request ready, or merge it: that is the owner's stage.
- Post no status comment. Tell the owner in the chat what you did and what remains, with the URLs.

## Titles and commit subjects

GitHub squash-merges a pull request into one commit on the default branch and appends ` (#<pull request>)` to its subject. That subject is the pull request title or, when the pull request has one commit, the subject of that commit. So a title or a commit subject never carries an issue or pull request number in any form (no `#54`, `(part of #39)`, or `issue 41`). The body's `Part of #<issue>` line links the pull request to its issue.

- Title the pull request with one statement of the outcome that the plan delivers, in the imperative, for example "Show the build duration in the checks summary". Add no trailing list of work parts, such as ": script, tests, and docs".
- Give each commit a subject that says what the commit changes, in the imperative, for example "Add the duration step to the CI workflow". The commit body may name the plan or a milestone.

To check a pull request, run this command with its number. It prints one line for each title or commit subject that has a number, and nothing when all are clean. A number is `#` followed by a digit, or one of the words `plan`, `issue`, `PR`, or `pull request`, white space, and a digit, in any case. The first line makes the command fail when `gh` fails: if the command exits with an error, report the error, and stop. No output means that all are clean only when the command exits without an error.

```bash
set -o pipefail
gh pr view <pull request> --json title,commits | jq -r '
  def bad: test("#[0-9]|(^|[^\\p{L}\\p{M}\\p{Nd}\\p{Pc}])(plan|issue|pr|pull\\p{White_Space}+request)\\p{White_Space}+[0-9]"; "i");
  (select(.title | bad) | "title    \(.title)"),
  (.commits[] | select(.messageHeadline | bad) | "\(.oid[0:7])  \(.messageHeadline)")'
```

## Find the pull request

The owner names a pull request, an issue, or a branch.

- A pull request: check out its branch with `gh pr checkout <number>`.
- An issue: list its pull requests with the command below, and check out the OPEN one. When none is OPEN, the issue needs its next plan first: tell the owner (the skill `effect-brewery:local-plan`).
- A branch with a plan file and no pull request: push it, and open the draft pull request, titled as "Titles and commit subjects" says: `gh pr create --draft --base <default branch> --title "<title>" --body-file <file>`. Its body has the line `Part of #<issue>` on a line of its own only when the work has an issue. Add no label.

```bash
set -o pipefail
gh pr list --state all --limit 1000 --json number,state,title,body \
  | jq -r --arg n "<n>" '[.[] | select((.body // "") | test("(^|\n)Part of #" + $n + "([^0-9]|$)"))] | sort_by(-.number) | .[] | "#\(.number) \(.state) \(.title)"'
```

The command prints one line for each pull request whose body has a line that starts with `Part of #<n>`, newest first, as `#<number> <STATE> <title>`. The state is OPEN, MERGED, or CLOSED. The first line makes the command fail when `gh` fails: if the command exits with an error, report the error, and stop. An empty output means that the issue has no pull request only when the command exits without an error.

The plan is the one file under `docs/execplans/` that the pull request adds or changes (`gh pr diff <number> --name-only`). With none, or with more than one, tell the owner and stop.

## Work steps

1. Read the plan file, and the issue if the pull request names one. Read the pull request's conversation comments, reviews, and inline review comments (`gh pr view <number> --comments`, `gh api repos/{owner}/{repo}/pulls/<number>/comments --paginate`), and the checks of its head commit (`gh pr checks <number>`; `gh run view <run id> --log-failed` shows the log of a failed check).
2. Work in this order: fix failed checks, then address review feedback, then implement the next milestones.
3. Commit frequently, with subjects as "Titles and commit subjects" says. Before each push, run the repository's checks.
4. Push. After each push, run the title check for the pull request. If it marks the title, fix the title with `gh pr edit <number> --title "<title>"`. If it marks a pushed commit subject, do not rewrite pushed commits: tell the owner, who can edit the commit message when merging.
5. Reply to each review comment on its own, in its thread. An inline comment gets an inline reply: write the reply to a file outside the repository, and post it with `gh api repos/{owner}/{repo}/pulls/<number>/comments/<id>/replies -F body=@<file>`. Say what you changed and in which commit, or why you changed nothing.
6. Keep the plan file current as you go: Progress with timestamps, Surprises & Discoveries, the Decision Log, and Outcomes & Retrospective when every milestone is done. If the owner merges before every milestone is done, the unchecked items stay, and the issue's next pull request continues the same plan file.
7. Tell the owner what you did and what remains. When the owner says that the pull request is merged, use the skill `effect-brewery:local-wrap-up`.
