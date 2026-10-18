---
name: gh-cli
description: "Use when the user wants to do anything on GitHub from the terminal — create, review, merge, or check pull requests; file or triage issues; check CI status or failing checks; manage repos, releases, gists, labels, or Actions workflows and runs; search across GitHub; or query the GitHub REST or GraphQL API. Also use when the user mentions gh, wants to script GitHub operations, or says things like merge that PR or what's failing in CI — if the action lives on GitHub's servers, this skill applies."
---

# GitHub CLI (`gh`)

The GitHub CLI lets you do almost everything you'd do on github.com, but from your terminal. It's especially useful because it understands your repo context — if you're inside a git repo, `gh` already knows the owner and repo name, so commands are short.

This skill helps you pick the right `gh` command for any GitHub task and use it effectively.

## When to use `gh` vs other approaches

| Want to...                                                 | Use                                       |
| ---------------------------------------------------------- | ----------------------------------------- |
| Interact with GitHub (PRs, issues, releases, Actions, API) | `gh`                                      |
| Do local git operations (commit, branch, rebase, stash)    | `git`                                     |
| View a repo page or complex diff in a browser              | `gh browse` (opens browser from terminal) |

The general rule: if the action lives on GitHub's servers (creating a PR, checking CI, filing an issue), `gh` is the right tool. If it's local version control, use `git`.

## Authentication

Before using `gh`, the user needs to be authenticated. If a command fails with an auth error, suggest:

```bash
gh auth status          # check current auth state
gh auth login           # interactive login
gh auth login --with-token < token.txt  # non-interactive
```

Most users are already authenticated if they've used `gh` before. Don't preemptively ask about auth — just handle the error if it comes up.

## Repo context and the `-R` flag

By default, `gh` infers the repository from the current directory's git remote. This means most commands "just work" when you're inside a cloned repo.

To target a different repo, use `-R owner/repo`:

```bash
gh issue list -R cli/cli          # issues on the cli/cli repo
gh pr view 123 -R facebook/react  # PR #123 on facebook/react
```

## Core commands quick reference

### Pull Requests

PRs are the most common `gh` use case. Here are the essential commands:

```bash
# Create
gh pr create                        # interactive — prompts for title, body, base branch
gh pr create --title "Fix bug" --body "Details here" --base main
gh pr create --fill                 # auto-fill title/body from commits
gh pr create --draft                # create as draft PR
gh pr create --reviewer user1,user2 --assignee @me --label bugfix

# List & view
gh pr list                          # open PRs in current repo
gh pr list --state all              # include closed/merged
gh pr list --author @me             # your PRs
gh pr list --search "review:required" # advanced GitHub search syntax
gh pr view 42                       # view PR #42 details
gh pr view 42 --web                 # open in browser
gh pr view --json title,url,reviewDecision  # machine-readable output

# Review workflow
gh pr checkout 42                   # fetch and check out PR branch locally
gh pr diff 42                       # view the diff
gh pr review 42 --approve           # approve
gh pr review 42 --request-changes --body "Please fix X"
gh pr review 42 --comment --body "Looks mostly good, one question"

# Merge & manage
gh pr merge 42                      # interactive merge (asks merge/squash/rebase)
gh pr merge 42 --squash --delete-branch  # squash merge and clean up
gh pr merge 42 --auto --squash      # enable auto-merge when checks pass
gh pr close 42                      # close without merging
gh pr reopen 42
gh pr ready 42                      # mark draft PR as ready for review
gh pr edit 42 --add-label "needs-review" --add-reviewer user1
gh pr edit 42 --add-reviewer "@copilot"  # request a review from GitHub Copilot

# CI status
gh pr checks 42                     # show CI check status for the PR
gh pr checks 42 --watch             # stream updates until checks complete
```

### Issues

```bash
# Create
gh issue create                     # interactive
gh issue create --title "Bug: X" --body "Steps to reproduce..." --label bug
gh issue create --assignee @me

# List & search
gh issue list                       # open issues
gh issue list --label "bug" --assignee @me
gh issue list --search "is:open sort:updated"
gh issue view 99                    # view issue details
gh issue view 99 --web

# Manage
gh issue close 99
gh issue close 99 --reason "not planned"    # reasons: completed | "not planned" | duplicate
gh issue reopen 99
gh issue comment 99 --body "Working on this"
gh issue edit 99 --add-label "priority:high" --add-assignee user1
gh issue pin 99                     # pin to repo
gh issue transfer 99 owner/other-repo   # destination must have the same owner
gh issue develop 99                 # create a linked branch for this issue
gh issue develop 99 --checkout      # create branch and check it out
```

### Repositories

```bash
# Create
gh repo create my-project --public --clone     # create and clone locally
gh repo create my-project --private --add-readme
gh repo create org/project --public            # create under an org

# Clone & fork
gh repo clone owner/repo                       # clone via gh (handles auth)
gh repo fork owner/repo --clone                # fork and clone your fork

# View & manage
gh repo view                        # view current repo info
gh repo view owner/repo --web       # open in browser
gh repo list --limit 20             # your repos
gh repo list my-org --limit 50      # org repos
gh repo edit --default-branch main
gh repo sync                        # sync fork with upstream
gh repo archive owner/repo          # archive a repo
```

### Releases

```bash
gh release create v1.0.0                              # interactive
gh release create v1.0.0 --title "v1.0.0" --notes "Release notes here"
gh release create v1.0.0 ./dist/*.tar.gz              # upload assets
gh release create v1.0.0 --generate-notes              # auto-generate from commits
gh release create v1.0.0 --draft                       # create as draft
gh release list
gh release view v1.0.0
gh release download v1.0.0                             # download all assets
gh release download v1.0.0 --pattern "*.tar.gz"        # download matching assets
gh release delete v1.0.0 --yes
```

### GitHub Actions (Workflows & Runs)

```bash
# Workflows
gh workflow list                     # list all workflows
gh workflow view "CI"                # view workflow details
gh workflow run "CI"                 # trigger a workflow_dispatch event
gh workflow run "CI" -f param1=value1  # with input parameters
gh workflow enable "CI"
gh workflow disable "CI"

# Runs
gh run list                          # recent runs
gh run list --workflow "CI"          # runs for a specific workflow
gh run view 12345                    # view run details
gh run view 12345 --log              # view full logs
gh run view 12345 --log-failed       # view only failed step logs
gh run watch 12345                   # live-stream run progress
gh run rerun 12345                   # rerun a failed run
gh run rerun 12345 --failed          # rerun only failed jobs
gh run cancel 12345
gh run download 12345                # download artifacts from a run
```

### Search

Search across all of GitHub — repos, issues, PRs, code, commits:

```bash
gh search repos "machine learning" --language python --sort stars
gh search issues "memory leak" --repo owner/repo --state open
gh search prs "review:approved" --repo owner/repo
gh search code "TODO fixme" --repo owner/repo --extension py
gh search commits "fix bug" --repo owner/repo --author user1
```

### Gists

```bash
gh gist create file.py                          # create from file
gh gist create file.py --public --desc "My snippet"
echo "hello" | gh gist create                   # create from stdin
gh gist list
gh gist view <gist-id>
gh gist edit <gist-id>
```

## Structured output with `--json` and `--jq`

Most `gh` commands support `--json` for machine-readable output. This is invaluable for scripting and when you need to extract specific fields:

```bash
# Get specific fields as JSON
gh pr list --json number,title,author
gh issue list --json number,title,labels,assignees

# Filter with jq expressions inline
gh pr list --json number,title,reviewDecision --jq '.[] | select(.reviewDecision == "APPROVED")'
gh pr view 42 --json commits --jq '.commits | length'

# Combine with other tools
gh pr list --json url --jq '.[].url'   # just URLs, one per line
```

To see which JSON fields are available for any command, run it with `--json` and no field names — it'll list the options.

## The `gh api` escape hatch

When there's no built-in subcommand for what you need, `gh api` lets you call any GitHub REST or GraphQL endpoint directly. It handles authentication automatically. It returns one page of a list (30 items by default); add `--paginate` to fetch all pages.

```bash
# REST examples
gh api repos/{owner}/{repo}/contributors          # {owner}/{repo} auto-filled
gh api repos/{owner}/{repo}/topics
gh api /user                                       # the authenticated user
gh api repos/{owner}/{repo}/actions/runners        # list self-hosted runners

# With parameters
gh api repos/{owner}/{repo}/dispatches -f event_type=deploy
gh api repos/{owner}/{repo}/dispatches -f event_type=deploy -F 'client_payload[env]=production'  # nested object via key[subkey]=value
# check for a builtin first — e.g. labels have one: gh label create urgent --color ff0000

# Pagination
gh api repos/{owner}/{repo}/issues --paginate      # auto-paginate all results

# GraphQL
gh api graphql -f query='{ viewer { login } }'
```

For detailed `gh api` patterns including GraphQL mutations and complex queries, read `references/api-patterns.md`.

## Common workflows

### "I want to start working on an issue"

```bash
gh issue view 42                    # read the issue
gh issue develop 42 --checkout      # create and check out a linked branch
# ... make changes, commit ...
gh pr create --fill                 # create PR (auto-links to issue)
```

### "I want to review someone's PR"

```bash
gh pr checkout 42                   # check out the PR locally
gh pr diff 42                       # view the changes
gh pr checks 42                     # see if CI passes
# ... test locally ...
gh pr review 42 --approve           # or --request-changes
```

### "What needs my attention?"

```bash
gh status                           # overview: assigned issues, review requests, mentions
gh pr list --search "review-requested:@me"  # PRs waiting for your review
gh pr list --author @me              # your open PRs
gh issue list --assignee @me         # issues assigned to you
```

### "Check why CI is failing"

```bash
gh pr checks 42                     # which checks failed?
gh run view <run-id> --log-failed   # see just the failure logs
gh run rerun <run-id> --failed      # retry only the failed jobs
```

### "I need to make a release"

```bash
gh release create v2.0.0 --generate-notes  # auto-generate changelog from commits
# or with assets:
gh release create v2.0.0 ./build/*.zip --title "v2.0.0" --notes-file CHANGELOG.md
```

## Tips

- **Tab completion**: `gh completion -s zsh` (or bash/fish/powershell) generates shell completions — suggest this if the user seems to be exploring commands frequently.
- **Aliases**: `gh alias set` creates shortcuts. E.g., `gh alias set prs 'pr list --author @me'` → `gh prs`.
- **Environment variables**: `GH_REPO=owner/repo` sets the default repo without `-R`. `GH_TOKEN` can provide auth for scripts.
- **`--web` flag**: Most view commands accept `--web` to open the result in a browser instead of the terminal.
- **Interactive vs scripted**: Without flags, most create/merge commands are interactive with prompts. Add explicit flags (`--title`, `--body`, `--squash`, etc.) for scriptable/non-interactive usage.
