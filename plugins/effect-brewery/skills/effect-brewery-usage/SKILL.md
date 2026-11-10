---
name: effect-brewery-usage
description: Use when a user asks how to use the effect-brewery plugin, what a working round looks like, which command starts a stage, or which effect-brewery stage comes next for a GitHub issue or pull request.
---

# Using effect-brewery

This skill explains a working round of the plugin `effect-brewery`, and says which stage comes next for an issue or a pull request. It only reads: it never changes an issue, a pull request, or the repository, and it never starts a stage. The user starts the stage with its command, in a fresh session.

## A working round

A working round takes a change from a GitHub issue to a merged pull request in four stages. Each stage is a skill of the plugin that the user starts with a command. In Claude Code, the command is `/effect-brewery:<skill> <argument>`. In Copilot CLI, it is `/<skill> <argument>`, or `/effect-brewery:<skill> <argument>` when another installed plugin has a skill of the same name. The list below gives the Claude Code form.

1. Issue: `/effect-brewery:local-issue <the goal, in your words>`, or `/effect-brewery:local-issue #<issue>` to refine an existing issue. The user describes the change, its acceptance criteria, and its context. The agent asks for the repository and for a project board, and one question at a time about gaps. It publishes only after the user approves. It produces a GitHub issue with a section `## Acceptance criteria` of checkboxes.
2. Plan: `/effect-brewery:local-plan #<issue>`, in a checkout of the issue's repository. The agent asks for the template of the branch name, and the questions that block an acceptance criterion. It records every other choice in the plan's Decision Log. It produces a branch, an ExecPlan file in `docs/execplans/`, and a draft pull request with the line `Part of #<issue>`. `/effect-brewery:local-plan #<pull request>` changes the plan of an open pull request after the user's review.
3. Implement: `/effect-brewery:local-implement #<pull request>`. The agent fixes failed checks, addresses review feedback, implements the plan's milestones, and replies to each review comment. The user's review comments are requirements. The agent asks only about an ambiguity that changes what the plan delivers or how it is accepted. It produces the commits of the plan in the pull request. Then the user reviews the pull request, marks it ready, and merges it: no stage does that.
4. Wrap Up: `/effect-brewery:local-wrap-up #<pull request>`, after the merge. The agent ticks the acceptance criteria that the evidence of the merged pull request shows are met, and posts one comment on the issue. It asks the user before it closes the issue. It produces ticked boxes, a comment, and, after the user's yes, a closed issue.

When Wrap Up leaves acceptance criteria unmet, another round starts at Plan with the same issue. When an issue has three merged pull requests, Plan asks to split it into smaller issues, which the user writes with Issue.

## Fresh sessions

Each stage reads what it needs from GitHub, and does not need the chat of an earlier stage. So each stage can start in a fresh session: `/clear` in Claude Code, `/new` in Copilot CLI. A fresh session keeps the context window small. Say so whenever you give a command.

## Say the next stage

Work in the repository of the current checkout. When a command exits with an error, report the error, and stop. When the user names no issue and no pull request and wants to start new work, the next stage is Issue.

When the user gives a number `<n>` and does not say whether it is an issue or a pull request, find out with this command. It prints `issue` or `pull request`. Do not use `gh issue view` for this: it also accepts the number of a pull request.

```bash
gh api "repos/{owner}/{repo}/issues/<n>" --jq 'if .pull_request then "pull request" else "issue" end'
```

### For an issue

1. Run `gh issue view <n> --json state --jq .state`. When it prints `CLOSED`, the round is over, and there is no next stage.
2. List the pull requests of the issue with the command "Pull requests of an issue". When one is `OPEN`, apply "For an open pull request" to it. Plan does not start while a pull request of the issue is open.
3. When none is `MERGED`, the next stage is Plan with the issue.
4. Take the newest `MERGED` pull request `<p>`. When the issue has no comment that starts with `Merged #<p> ` (the command "Wrap Up comment"), the next stage is Wrap Up with `<p>`.
5. Count the boxes of the issue's section `## Acceptance criteria` with the command "Acceptance criteria boxes". When there are boxes and none is unticked, the next stage is Wrap Up with `<p>`, which asks the user whether to close the issue.
6. Otherwise, a box is unticked, or the section has no box. With no box, only the user can judge whether the issue is done. Say so, and give the stage below for the case that work remains. With three or more `MERGED` pull requests, the issue is too big for Plan. The next stage is Issue, to split the issue into smaller issues. With fewer than three, the next stage is Plan with the issue.

### For a pull request

1. Run `gh pr view <p> --json state --jq .state`. When it prints `OPEN`, apply "For an open pull request".
2. When it prints `MERGED` or `CLOSED`, find its issues with the command "Issues of a pull request". With none, effect-brewery has no next stage for it: say so. For each issue, check its state: when the issue is `CLOSED`, its round is over.
3. When the pull request is `MERGED` and the open issue has no comment that starts with `Merged #<p> `, the next stage is Wrap Up with `<p>`. Otherwise, apply "For an issue". A `CLOSED` pull request was closed without a merge, so it never leads to Wrap Up.

### For an open pull request

Count its plan files with the command "Plan files of a pull request". With exactly one, the next stage is Implement with `<p>`. Add that `/effect-brewery:local-plan #<p>` changes its plan when the plan needs a change before the work. Wrap Up with `<p>` comes after the user reviews and merges it. With none or more than one, effect-brewery cannot continue it: Implement needs exactly one plan file under `docs/execplans/` in the pull request. Say so, with the number of plan files that you found.

### Commands

`gh` fills in `{owner}/{repo}` from the current checkout. Each command that starts with `set -o pipefail` fails when `gh` fails. An empty output means "none" only when the command exits without an error.

Pull requests of an issue. It prints one line for each pull request whose body has a line that starts with `Part of #<n>`, newest first, as `#<number> <STATE> <title>`. The state is `OPEN`, `MERGED`, or `CLOSED`. It prints nothing when the issue has none. The stage skills use the same command.

```bash
set -o pipefail
gh pr list --state all --limit 1000 --json number,state,title,body \
  | jq -r --arg n "<n>" '[.[] | select((.body // "") | test("(^|\n)Part of #" + $n + "([^0-9]|$)"))] | sort_by(-.number) | .[] | "#\(.number) \(.state) \(.title)"'
```

Wrap Up comment. It prints the id of each comment of issue `<n>` that starts with `Merged #<p> `, and nothing when there is none. Wrap Up posts this comment.

```bash
gh api "repos/{owner}/{repo}/issues/<n>/comments" --paginate --jq '.[] | select(.body | startswith("Merged #<p> ")) | .id'
```

Acceptance criteria boxes. It prints the number of unticked boxes and the number of all boxes of the section `## Acceptance criteria` of issue `<n>`, for example `1 8`.

```bash
set -o pipefail
gh issue view <n> --json body --jq .body | awk '
  /^# / || /^## / { inac = ($(0) ~ /^## Acceptance criteria[ \t\r]*$/) }
  inac && /^[ \t]*[-*+][ \t]+\[[ xX]\]/ { total++ }
  inac && /^[ \t]*[-*+][ \t]+\[ \]/ { open++ }
  END { print open + 0, total + 0 }'
```

Issues of a pull request. It prints the number of each issue that pull request `<p>` names with a line `Part of #<n>` in its body, once each. It prints nothing when the body names none.

```bash
set -o pipefail
gh pr view <p> --json body --jq '.body // ""' | tr -d '\r' | sed -n 's/^Part of #\([1-9][0-9]*\).*/\1/p' | awk '!seen[$(0)]++'
```

Plan files of a pull request. It prints the number of files under `docs/execplans/` that pull request `<p>` adds or changes, for example `1`. Implement finds the plan with the same list.

```bash
set -o pipefail
gh pr diff <p> --name-only | awk '/^docs\/execplans\// { n++ } END { print n + 0 }'
```

## Answer

Say the stage and the reason in one or two sentences, with the states that you found. Give the command for Claude Code and the command for Copilot CLI, with the number filled in. Tell the user to run it in a fresh session. When there is no next stage, say why. When the user asked how to use effect-brewery, explain the round from "A working round" instead. For each stage, give its commands, what the user does, what the agent does, and what the stage produces. End with the advice about fresh sessions.
