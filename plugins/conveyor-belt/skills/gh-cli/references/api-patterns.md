# Advanced `gh api` Patterns

This reference covers advanced usage of `gh api` for when the built-in `gh` subcommands don't cover what you need.

## Table of Contents

- [REST API basics](#rest-api-basics)
- [Sending data](#sending-data)
- [Pagination](#pagination)
- [GraphQL](#graphql)
- [Common API recipes](#common-api-recipes)

## REST API basics

`gh api` makes authenticated requests to the GitHub API. The base URL (`https://api.github.com`) is implied — just pass the path.

```bash
# GET request (default)
gh api repos/{owner}/{repo}

# Specify HTTP method
gh api repos/{owner}/{repo}/issues -X POST -f title="New issue"

# Include response headers
gh api repos/{owner}/{repo} --include

# Use a specific API version
gh api repos/{owner}/{repo} -H "X-GitHub-Api-Version: 2022-11-28"
```

Placeholders `{owner}`, `{repo}`, and `{branch}` are auto-filled from the current repo context.

## Sending data

Two flags for parameters, with different behavior:

- `-f key=value` — sends as a **string**
- `-F key=value` — "smart" field: `@file` reads a file, numbers stay as numbers, `true`/`false` become booleans, `null` is null
- Nested objects and arrays use bracket syntax with either flag: `-F 'parent[child]=value'` builds `{"parent":{"child":"value"}}`, repeated `-f 'list[]=a' -f 'list[]=b'` builds an array, and `key[]` alone sends an empty array.

Neither flag parses a JSON object string: `-F payload='{"a":1}'` sends the literal string `{"a":1}`, not an object. To send pre-constructed JSON, pipe it via `--input -`.

```bash
# String fields
gh api repos/{owner}/{repo}/issues -f title="Bug report" -f body="Details..."

# Typed fields
gh api repos/{owner}/{repo}/issues -F milestone=3  # number, not string "3"

# Read body from file
gh api repos/{owner}/{repo}/issues -F body=@issue_body.md -f title="From file"

# Send raw JSON body
echo '{"title":"Bug","body":"Details"}' | gh api repos/{owner}/{repo}/issues --input -
```

## Pagination

GitHub paginates most list endpoints (30 items by default). `gh api` handles this:

```bash
# Auto-paginate all results
gh api repos/{owner}/{repo}/issues --paginate

# With jq to extract specific fields across all pages
gh api repos/{owner}/{repo}/issues --paginate --jq '.[].title'

# Wrap all pages into a single JSON array (one document instead of concatenated pages)
gh api repos/{owner}/{repo}/issues --paginate --slurp

# Limit results per page (but still just one page)
gh api 'repos/{owner}/{repo}/issues?per_page=100'  # quote it: zsh treats ? as a glob
```

For very large result sets, combine `--paginate` with `--jq` to stream-process results and avoid loading everything into memory.

## GraphQL

Use `gh api graphql` for GitHub's GraphQL API (v4). This is powerful for fetching exactly the data you need in a single request.

```bash
# Simple query
gh api graphql -f query='
  query {
    viewer {
      login
      repositories(first: 5, orderBy: {field: UPDATED_AT, direction: DESC}) {
        nodes { nameWithOwner }
      }
    }
  }
'

# With variables (preferred for dynamic values)
gh api graphql -F owner='{owner}' -F repo='{repo}' -f query='
  query($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo) {
      issues(first: 10, states: OPEN) {
        nodes {
          number
          title
          labels(first: 5) { nodes { name } }
        }
      }
    }
  }
'

# Mutations (e.g., add a comment)
gh api graphql -F subjectId="<node-id>" -f query='
  mutation($subjectId: ID!) {
    addComment(input: {subjectId: $subjectId, body: "Automated comment"}) {
      commentEdge { node { url } }
    }
  }
'
```

To find a node ID, query it first:

```bash
gh api graphql -F owner='{owner}' -F repo='{repo}' -F number=42 -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      issue(number: $number) { id }
    }
  }
'
```

## Common API recipes

### Get repo traffic (views & clones)

```bash
gh api repos/{owner}/{repo}/traffic/views
gh api repos/{owner}/{repo}/traffic/clones
```

### List repository collaborators with permissions

```bash
gh api repos/{owner}/{repo}/collaborators --paginate --jq '.[] | {login: .login, role: .role_name}'
```

### Get branch protection rules

```bash
gh api repos/{owner}/{repo}/branches/main/protection
```

### Create or update a file via API

```bash
# Get current file SHA first (needed for updates)
SHA=$(gh api repos/{owner}/{repo}/contents/path/to/file.txt --jq '.sha')

# Create or update
gh api repos/{owner}/{repo}/contents/path/to/file.txt \
  -X PUT \
  -f message="Update file" \
  -f content="$(echo -n 'file content' | base64)" \
  -f sha="$SHA"
```

### Trigger a repository dispatch event

```bash
gh api repos/{owner}/{repo}/dispatches -f event_type=deploy -F 'client_payload[env]=production'

# or send pre-constructed JSON via --input:
echo '{"event_type":"deploy","client_payload":{"env":"production"}}' | gh api repos/{owner}/{repo}/dispatches --input -
```

### List organization members

```bash
gh api orgs/my-org/members --paginate --jq '.[].login'
```

### Get rate limit status

```bash
gh api rate_limit --jq '.resources.core | "Used: \(.used)/\(.limit), resets: \(.reset)"'
```

### Enable/disable Actions for a repo

```bash
# Check current status
gh api repos/{owner}/{repo}/actions/permissions

# Enable
gh api repos/{owner}/{repo}/actions/permissions -X PUT -F enabled=true -f allowed_actions=all
```

### Download a specific workflow artifact

```bash
# List artifacts from a run
gh api repos/{owner}/{repo}/actions/runs/12345/artifacts --jq '.artifacts[] | {name: .name, id: .id}'

# Download by ID
gh api repos/{owner}/{repo}/actions/artifacts/<id>/zip > artifact.zip
```
