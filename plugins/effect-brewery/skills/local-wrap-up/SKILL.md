---
name: local-wrap-up
description: "Use in a chat when the owner has merged a pull request of this repository and wants its issue to record the merge: tick the acceptance criteria that the merge met, comment what it delivered, and close the issue when nothing remains."
---

# Wrapping up a merged pull request in a chat

Merging a pull request does not change its issue. This skill records the merge on the issue: it ticks the acceptance criteria that the merge met, posts one comment, and, when no criterion remains, offers to close the issue. The owner is in this chat: ask, never guess.

## Rules that always apply

- Work in the repository of the current checkout.
- The default branch is the output of `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`. This skill writes `<default branch>` for it.
- This skill may do three things to an issue, and nothing else: change an unticked box (`- [ ]`) to a ticked box (`- [x]`) in the section "Acceptance criteria" of its body; post one comment; close it after the owner says yes. Never untick a box, never change the words of the issue, and never change another section. Never change the pull request.
- Tick a box only when the evidence shows that its criterion is met. The evidence is the plan of the merged pull request (its Validation and Acceptance, its Progress, and its Outcomes & Retrospective) and the checks of the pull request. When the evidence is partial or missing, leave the box unticked, and say so in the comment.
- The owner's request to wrap up a pull request is the approval to tick and to comment. Closing the issue needs the owner's separate yes.
- If a command exits with an error, report the error, and stop.
- Post no other comment. Tell the owner in the chat what you did, with the URLs.
- Keep the text of the issue, the plan, and the comment out of shell command source: write each to a file outside the repository, such as in the session scratchpad directory, and pass the file. This skill writes `BODY_FILE`, `TICK_FILE`, `NEW_FILE`, and `COMMENT_FILE` for these files. Remove them when you are done.

## Find the merged pull request

The owner names a pull request or an issue.

- A pull request: run this command with its number. It prints the number, the state, the hash of the merge commit, and the title.

  ```bash
  gh pr view <p> --json number,state,title,mergeCommit --jq '"#\(.number) \(.state) \(.mergeCommit.oid // "-") \(.title)"'
  ```

  The state must be MERGED. When it is OPEN, tell the owner that the pull request is not merged yet, and stop. When it is CLOSED, it was closed without a merge: tell the owner, and stop. This skill writes `<sha>` for the hash and `<sha7>` for its first seven characters.
- An issue: run the command in "Find the pull requests of an issue", and take the newest MERGED pull request. With none, tell the owner, and stop. Then run the command above with the number of that pull request, to get its hash.

### Find the pull requests of an issue

```bash
set -o pipefail
gh pr list --state all --limit 1000 --json number,state,title,body \
  | jq -r --arg n "<n>" '[.[] | select((.body // "") | test("(^|\n)Part of #" + $n + "([^0-9]|$)"))] | sort_by(-.number) | .[] | "#\(.number) \(.state) \(.title)"'
```

The command prints one line for each pull request whose body has a line that starts with `Part of #<n>`, newest first, as `#<number> <STATE> <title>`. The state is OPEN, MERGED, or CLOSED. A pull request that is CLOSED did not merge, and it does not count. The command prints nothing when the issue has no pull request. It lists pull requests and does not search them, because a search can miss a pull request that was just opened. The first line makes the command fail when `gh` fails: if the command exits with an error, report the error, and stop. An empty output means that the issue has no pull request only when the command exits without an error.

## Find the issues of the pull request

```bash
set -o pipefail
gh pr view <p> --json body --jq '.body // ""' | tr -d '\r' | sed -n 's/^Part of #\([1-9][0-9]*\).*/\1/p' | awk '!seen[$(0)]++'
```

The command prints the number of each issue that the pull request body names with a line that starts with `Part of #<n>`, once each. When it prints nothing and exits without an error, the pull request names no issue: tell the owner, and stop. Do the next three sections for each issue, one issue at a time.

## Tick the criteria

1. Read the plan of the merged pull request. List the plan files that it added, changed, or renamed:

   ```bash
   gh api "repos/{owner}/{repo}/pulls/<p>/files" --paginate --jq '.[] | select(.status == "added" or .status == "modified" or .status == "renamed") | .filename | select(startswith("docs/execplans/") and endswith(".md"))'
   ```

   Read the file as it was in the merge commit. Do not read it on the default branch: a finished plan may have been deleted from the default branch since the merge.

   ```bash
   gh api -H "Accept: application/vnd.github.raw+json" "repos/{owner}/{repo}/contents/<file>?ref=<sha>"
   ```

   When the pull request changed no plan file, use its description and its checks as the only evidence. This command prints one line for each check, as `<name>  <result>`, and nothing when the pull request has no checks. Do not use `gh pr checks` here: it exits with an error when a check failed or when there is no check.

   ```bash
   gh pr view <p> --json statusCheckRollup --jq '.statusCheckRollup[] | "\(.name // .context)  \(if (.conclusion // "") != "" then .conclusion else (.status // .state) end)"'
   ```
2. Save the body of the issue to `BODY_FILE`, and read its section "Acceptance criteria":

   ```bash
   gh issue view <n> --json body --jq .body > BODY_FILE
   ```

   When the section has no box, tell the owner that there is nothing to tick, and go to "Comment". When it has no unticked box, go to "Comment".
3. For each unticked box, decide from the evidence, by the rule above, whether to tick it. Write the text of each box that you tick to `TICK_FILE`, one per line: the text after `- [ ] `, exactly as it is in the body. When you tick none, go to "Comment".
4. Make the new body in `NEW_FILE`:

   ```bash
   awk -v tickfile=TICK_FILE '
     BEGIN { while ((getline line < tickfile) > 0) want[line] = 1 }
     /^# / || /^## / { inac = ($(0) ~ /^## Acceptance criteria[ \t\r]*$/) }
     inac && match($(0), /^[ \t]*[-*+][ \t]+\[ \][ \t]+/) {
       text = substr($(0), RLENGTH + 1)
       sub(/\r$/, "", text)
       if (text in want) { sub(/\[ \]/, "[x]"); ticked[text] = 1 }
     }
     { print }
     END {
       for (t in want) if (!(t in ticked)) { print "NOT FOUND: " t > "/dev/stderr"; bad = 1 }
       exit bad
     }' BODY_FILE > NEW_FILE
   ```

   When it prints `NOT FOUND` and exits with an error, a text in `TICK_FILE` is not an unticked box of the section. Correct `TICK_FILE` and run the command again, or stop and tell the owner.
5. Check the change: `diff BODY_FILE NEW_FILE` must show only the lines that you meant to tick, each as a `- [ ]` line and the same line with `- [x]`. If it shows anything else, stop and tell the owner.
6. Check that the issue did not change since step 2: `gh issue view <n> --json body --jq .body | cmp - BODY_FILE` must print nothing. If it prints a difference, the issue changed in the meantime: tell the owner, and stop.
7. Apply the change. `BODY_FILE` and `NEW_FILE` end with a newline that `jq` added in step 2, and that is not part of the body. This command removes that one newline, and uploads the rest:

   ```bash
   set -o pipefail
   jq -Rsj 'rtrimstr("\n")' NEW_FILE | gh issue edit <n> --body-file -
   ```

   Then run the check of step 6 again, with `NEW_FILE` in place of `BODY_FILE`. If it prints a difference, show the difference to the owner and say so; do not edit again.

## Comment

1. If a comment of the issue already starts with `Merged #<p> `, skip this section. This command prints the id of such a comment, and nothing when there is none:

   ```bash
   gh api "repos/{owner}/{repo}/issues/<n>/comments" --paginate --jq '.[] | select(.body | startswith("Merged #<p> ")) | .id'
   ```
2. Read the body of the issue again, and find which criteria remain: the boxes of the section "Acceptance criteria" that are still unticked.
3. Write the comment to `COMMENT_FILE`, with each paragraph and list item on one line (no hard wrapping):
   - the first line, exactly: `Merged #<p> into <default branch> as <sha7>.`
   - an empty line, and then two to four sentences on what the pull request delivered, in your own words, from the title of the pull request and the Purpose and the Outcomes of its plan. Claim nothing that the evidence does not show.
   - an empty line, the line `Ticked:`, and then one line `- <text of the box>` for each box that you ticked; or the line `Ticked: none.`
   - an empty line, the line `Remaining:`, and then one line `- <text of the box>` for each unticked box, with a short reason after it when the pull request met the criterion in part; or the line `Remaining: nothing.`
4. Post it with `gh issue comment <n> --body-file COMMENT_FILE`.

## Close

Count the boxes of the section "Acceptance criteria" in the current body of the issue. This command prints the number of unticked boxes and the number of all boxes, for example `1 15`:

```bash
set -o pipefail
gh issue view <n> --json body --jq .body | awk '
  /^# / || /^## / { inac = ($(0) ~ /^## Acceptance criteria[ \t\r]*$/) }
  inac && /^[ \t]*[-*+][ \t]+\[[ xX]\]/ { total++ }
  inac && /^[ \t]*[-*+][ \t]+\[ \]/ { open++ }
  END { print open + 0, total + 0 }'
```

- Some box is unticked: do not close the issue. Tell the owner which criteria remain. When no pull request of the issue is OPEN (use the command in "Find the pull requests of an issue"), the next step is the skill `effect-brewery:local-plan`.
- No box is unticked, there is at least one box, and no pull request of the issue is OPEN: tell the owner that the issue looks complete, and ask whether to close it. Close it only after the owner says yes, with `gh issue close <n> --reason completed`.
- The section has no box: a program cannot judge whether the issue is complete. Tell the owner, and close the issue only if the owner says so.

## Report

Tell the owner, for each issue: the lines that you ticked, the URL of the comment (or that the comment existed already), what remains, and whether the issue is closed.
