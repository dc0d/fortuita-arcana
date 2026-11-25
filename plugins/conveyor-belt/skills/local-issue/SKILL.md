---
name: local-issue
description: Use in a chat when a user wants to draft, clarify, or create a GitHub issue for agents to work on, or to refine an existing issue, including requests to place the issue on a team or project board.
---

# Creating GitHub Issue

Create an issue that agents can understand without this conversation or access to the author's machine. Describe the problem, intent, and observable outcomes, not an implementation plan. Do not implement the issue.

## Refine an existing issue

When the user names an existing issue (a number, `#<n>`, or a URL), continue that issue instead of creating one.

- The destination is the issue's repository. Read its title, body, and all comments with `gh issue view <n> --repo OWNER/REPO --comments`. The owner's latest words win over earlier ones.
- Check whether the issue has pull requests, with the command in "Find the pull requests of an issue". If it has an open or merged one, say so: a rewrite changes the goal under that work. Continue only if the user confirms.
- Clarify and draft as the sections below say, from the current body and comments. Keep every fact and intent of the owner's words. Remove each open question that the user answered, and work the answer into the body.
- The user's request to refine the issue is the approval to publish it, unless the user asked only for a draft. Publish with `approved_title=$(cat -- "TITLE_FILE") && gh issue edit <n> --repo OWNER/REPO --title "$approved_title" --body-file "BODY_FILE"`, and verify the result as for a new issue.

### Find the pull requests of an issue

```bash
set -o pipefail
gh pr list --repo OWNER/REPO --state all --limit 1000 --json number,state,title,body \
  | jq -r --arg n "<n>" '[.[] | select((.body // "") | test("(^|\n)Part of #" + $n + "([^0-9]|$)"))] | sort_by(-.number) | .[] | "#\(.number) \(.state) \(.title)"'
```

The command prints one line for each pull request whose body has a line that starts with `Part of #<n>`, newest first, as `#<number> <STATE> <title>`. The state is OPEN, MERGED, or CLOSED. A pull request that is CLOSED did not merge, and it does not count. The command prints nothing when the issue has no pull request. It lists pull requests and does not search them, because a search can miss a pull request that was just opened. The first line makes the command fail when `gh` fails: if the command exits with an error, report the error, and stop. An empty output means that the issue has no pull request only when the command exits without an error.

## Establish the destination

- Require a repository URL or `OWNER/REPO` before publication. If none is supplied, ask. A repository from local context is a candidate, not a confirmed destination. Ask the user to confirm it.
- Verify that the selected repository is accessible, not archived, and has issues enabled. Use the `gh repo view` command under Publish and report. Report access or configuration blockers; do not silently choose another repository.
- Always establish whether the user wants project placement. Honor an existing answer; otherwise ask, with no project as a valid choice.
- For project placement, resolve a project URL or its owner and number. A team name alone does not identify a project. If discovery is needed, use `gh project list --owner PROJECT_OWNER`. Do not assume the project owner is the repository owner.

## Clarify without pressure

Use the supplied context first. If a local checkout matches the selected repository, inspect relevant context read-only to establish facts.

Ask one focused question at a time about gaps that affect the problem, outcome, scope, constraints, or acceptance criteria. Skip questions already answered. Do not conduct a fixed interview or turn clarification into solution design.

When the user says the issue is satisfactory or asks to proceed, stop content questions. Record unresolved decisions as open questions instead of inventing answers. Questions that block future implementation do not block issue creation. Still resolve a missing repository or project choice. Satisfaction or a request to proceed is not publication approval; see Publish and report.

## Draft for agents

Read `references/issue-template.md` in the folder of this skill before you draft, and use its template. Do not hard-wrap text: write each paragraph and list item as one line in the file so GitHub reflows it.

- State established facts separately from assumptions and open questions.
- Include the context and evidence that a future agent needs. Use repository-relative paths or accessible URLs, not absolute local paths or references to this chat. Explain relevant local-only observations without assuming those files exist in the target repository. Exclude secrets and unrelated local data.
- Describe observable behavior and genuine constraints. Do not prescribe architecture, libraries, algorithms, file edits, or implementation steps. Preserve explicit external contracts and compatibility requirements.
- Use measurable limits and their applicable conditions when supplied. Do not invent thresholds to make the issue look complete.
- For investigations, define completion through findings, evidence, or decisions rather than changed software behavior.
- Add or remove acceptance criteria as needed. Omit optional sections that add no information. Remove placeholders, empty sections, and author guidance before publication.

For example, "Repeated submissions with the same request identifier create one order" specifies an outcome. "Add Redis deduplication middleware" prescribes an implementation.

## Publish and report

Show the title, body, repository, and project choice for approval before publication. An explicit instruction to publish that draft to those destinations is approval; do not ask again. Satisfaction with the wording alone is not permission to publish. If the user requests only a draft, stop at the draft.

Use `gh` with explicit destinations. Replace the command placeholders with confirmed destinations and file paths only. Use a file-writing tool to store the approved title and body in separate temporary files outside the repository, such as in the session scratchpad directory. Keep issue text out of shell command source. Read the title from its file and pass it as a quoted argument.

```bash
gh repo view OWNER/REPO --json nameWithOwner,url,hasIssuesEnabled,isArchived
approved_title=$(cat -- "TITLE_FILE") &&
  gh issue create --repo OWNER/REPO --title "$approved_title" --body-file "BODY_FILE"
```

If the user selected a project, add the created issue to that project:

```bash
gh project item-add PROJECT_NUMBER --owner PROJECT_OWNER --url ISSUE_URL
```

This command needs the `project` token scope. If it fails for a missing scope, ask the user to run `gh auth refresh -s project`, then retry placement only.

Verify the published title, body, repository, and requested project membership through GitHub. `gh` cannot read board view filters, so report project membership only. Do not claim the issue appears in a specific board view. Ask before setting project fields.

If creation has an uncertain result, check whether the issue exists before retrying. If project placement fails, retain the created issue and report the issue URL plus the placement blocker. Retry placement only; do not create a duplicate issue.

Report the issue URL and project placement result, or state that no project was requested. Post no status comment on the issue. Remove the temporary title and body files. Do not commit repository changes as part of this workflow.
