# effect-brewery

The plugin `effect-brewery` takes a change from a GitHub issue to a merged pull request. A working round has four stages: Issue, Plan, Implement, and Wrap Up. Each stage is a skill that you start with a command. The other skills support the stages.

| Skill | Role |
| :- | :- |
| `local-issue` | Issue: writes the GitHub issue |
| `local-plan` | Plan: writes the ExecPlan in a draft pull request |
| `local-implement` | Implement: implements the plan in that pull request |
| `local-wrap-up` | Wrap Up: records the merge on the issue |
| `effect-brewery-usage` | Explains the round, and says which stage comes next |
| `execplans` | The ExecPlan format that Plan and Implement follow |
| `the-architect` | Design decisions, which Implement uses when it shapes the structure of code |
| `local-archive` | Moves finished ExecPlans to `docs/execplans/archived/` |
| `gh-cli` | Reference for `gh`, the GitHub CLI |

## Before you start

Install the plugin as the root README says for [Claude Code](../../README.md#claude-code) or [GitHub Copilot CLI](../../README.md#github-copilot-cli). Sign in to `gh`, the GitHub CLI, with `gh auth login`. Every stage reads and writes GitHub with it.

Plan, Implement, and Wrap Up work in the repository of the current checkout. Start the agent for these stages in a checkout of the issue's repository.

A command starts a skill. In Claude Code, the command is `/effect-brewery:<skill> <argument>`, for example `/effect-brewery:local-plan #49`. In Copilot CLI, it is `/<skill> <argument>`, for example `/local-plan #49`. When another installed plugin has a skill of the same name, Copilot CLI needs `/effect-brewery:<skill> <argument>` too. `copilot skill list` shows the name to use.

## A working round

You start Issue with a goal, Plan with the number of the issue, and Implement with the number of the pull request that Plan opened. Then you review and merge the pull request: no stage does that for you. Last, you start Wrap Up with the number of the merged pull request.

Each stage reads what it needs from GitHub: the issue, the pull request, and the plan in the pull request. It does not need the chat of an earlier stage. So start each stage in a fresh session: `/clear` in Claude Code, `/new` in Copilot CLI. A fresh session keeps the context window small. The context window is the text that the model holds in one conversation, and a long session fills it with earlier stages.

## Issue

Start it with `/effect-brewery:local-issue <the goal, in your words>` in Claude Code, or `/local-issue <the goal, in your words>` in Copilot CLI. To refine an existing issue, give its number instead: `#<issue>`.

**You:** Describe the change, its acceptance criteria, and its context. Give the agent access to what it needs for context, for example GitHub, the services that the change touches, or MCP tools. MCP, the Model Context Protocol, connects an agent to tools.

**The agent:** It drafts the issue from your words and the context that it gathers. The issue has the sections Problem, Desired outcome, and Acceptance criteria, which is a list of checkboxes. Out of scope, Constraints, Context, and Open questions are optional. The issue describes outcomes, not an implementation, and the agent does not implement it. When an existing issue has an open or merged pull request, the agent asks before it changes the goal under that work.

**It asks:** For the repository of the issue (`OWNER/REPO` or a URL). A local checkout is only a candidate that you confirm. Whether to put the issue on a project board. One question at a time about gaps in the issue. When you say that the issue is good, it stops asking, and records what is still open as open questions. It shows the title, the body, the repository, and the project, and publishes only after you approve them. For an existing issue, your request to refine it is the approval, unless you asked only for a draft.

**It produces:** A GitHub issue and its URL. Wrap Up ticks its acceptance criteria later.

## Plan

Start it in a checkout of the issue's repository with `/effect-brewery:local-plan #<issue>` in Claude Code, or `/local-plan #<issue>` in Copilot CLI.

**You:** Review the plan in the draft pull request that the agent opens. A draft pull request is one that GitHub marks as not ready to merge. To change the plan, comment on the pull request, then start the stage with the number of the pull request: `#<pull request>`. You can also describe the change in that chat. The agent makes the change, addresses the review comments, and replies to each comment in its thread.

**The agent:** It stops when the issue is closed, or when a pull request of the issue is open. When the issue already has three merged pull requests, it comments on the issue that the issue must be split, and stops. Otherwise, it reads the issue with its comments, and researches the repository without changing it. It writes an ExecPlan: a self-contained design-and-implementation document in `docs/execplans/YYYYMMDD-NN-<name>.md`. It commits only the plan file, on a new branch from the default branch, runs the repository's checks, and pushes. It opens a draft pull request whose body has the line `Part of #<issue>`. This line links the pull request to the issue for the later stages. The agent never edits the issue: it proposes changes to the scope or the acceptance criteria in the chat.

**It asks:** For the template of the branch name, for example `feature/*`, unless you gave it in the chat. It never chooses a branch name without it, because CI/CD can run only on branches that match a template. It asks the open questions of the issue, and about each gap that makes an acceptance criterion impossible to verify, one question at a time. It decides every other choice, and records the choice and its reason in the plan's Decision Log.

**It produces:** A branch, a plan file in it, and a draft pull request that links to the issue. Your review of the plan steers Implement.

## Implement

Start it in a checkout of the repository with `/effect-brewery:local-implement #<pull request>` in Claude Code, or `/local-implement #<pull request>` in Copilot CLI. You can give the number of the issue instead: then the agent takes the open pull request of the issue.

**You:** Make sure that the repository names its checks in its CLAUDE.md, README, or CI workflow, for example a `make check` target. The agent runs these checks. Review the pull request, and start the stage again to address your review comments. When the work is done, mark the pull request ready, and merge it.

**The agent:** It checks out the branch of the pull request. It reads the plan, the issue, the review comments, and the checks. It fixes failed checks first, then addresses the review feedback, then implements the next milestones of the plan. It commits often. In the same commits, it keeps the plan's Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective current. Before each push, it runs the repository's checks. It replies to each review comment in its thread. It never resolves a review thread, marks the pull request ready, or merges it.

**It asks:** Your review comments are requirements. When a comment contradicts the plan, the agent follows the comment, and records the change in the Decision Log. It asks you only about an ambiguity that changes what the plan delivers or how it is accepted. Even then, it asks only when the plan, the issue, and the repository cannot settle the ambiguity. It decides every other choice, and records it in the Decision Log.

**It produces:** The commits of the plan's milestones in the pull request, a current plan, and replies to the review comments. When you merge before every milestone is done, the unchecked items of Progress stay. The next pull request of the issue continues the same plan.

## Wrap Up

After you merge the pull request, start it in a checkout of the repository with `/effect-brewery:local-wrap-up #<pull request>` in Claude Code, or `/local-wrap-up #<pull request>` in Copilot CLI. You can give the number of the issue instead: then the agent takes the newest merged pull request of the issue.

**The agent:** It works on each issue that the pull request names with `Part of #<issue>`. It reads the plan as it was in the merge commit, and the checks of the pull request. It ticks each box of the issue's acceptance criteria that this evidence shows is met. When the evidence is partial or missing, it leaves the box unticked. It posts one comment on the issue: what the pull request delivered, which boxes it ticked, and which remain. It changes nothing else on the issue, and never changes the pull request.

**It asks:** Your request to wrap up is the approval to tick boxes and to comment. When no box remains and no pull request of the issue is open, the agent asks whether to close the issue. It closes the issue only after your yes. When the acceptance criteria have no box, the agent cannot judge whether the issue is complete. It tells you, and closes the issue only if you say so.

**It produces:** Ticked acceptance criteria and one comment on the issue. When nothing remains and you say yes, a closed issue.

## Another round

When Wrap Up leaves acceptance criteria unmet, the next round starts at Plan with the same issue. Plan continues the plan file of the last merged pull request when that plan has unchecked items in Progress. Otherwise, it writes a new plan. When the issue already has three merged pull requests, Plan asks you to split the issue into smaller issues. Write them with Issue.

## Which stage comes next

The agent can tell you which stage comes next for an issue or a pull request. Start it in a checkout of the repository with `/effect-brewery:effect-brewery-usage #<issue or pull request>` in Claude Code, or `/effect-brewery-usage #<issue or pull request>` in Copilot CLI. You can also ask in your own words, for example "Which effect-brewery stage comes next for #49?". The agent reads the issue or the pull request on GitHub, and changes nothing. It gives you the command of the next stage, to run in a fresh session. Ask "How do I use effect-brewery?" to make it explain the round.

## Archive finished plans

A finished plan stays in `docs/execplans/`. To move every finished plan to `docs/execplans/archived/`, start `/effect-brewery:local-archive` in Claude Code, or `/local-archive` in Copilot CLI, in a checkout of the repository. The agent opens one pull request that holds only the moves. It asks for the template of the branch name, as Plan does.
