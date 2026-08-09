#!/usr/bin/env bash
# Create and push annotated tag v<X.Y.Z> for HEAD.
#
# Safe to re-run: an already-existing v<X.Y.Z> tag is a no-op (exit 0).
# Refuses (exit 1) a malformed argument or a version that is not strictly
# greater than the highest existing v* tag, so tags can never move backwards.
# The caller must have git user.name/user.email configured.
#
# Portable: bash 3.2 (macOS) compatible; no sort -V.
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "usage: $0 X.Y.Z (bare version, no v prefix)" >&2
  exit 2
fi
version="$1"

semver_re='^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'
if ! [[ "$version" =~ $semver_re ]]; then
  echo "error: invalid version '$version' (expected bare X.Y.Z, no v prefix)" >&2
  exit 1
fi

tag="v$version"

if git rev-parse -q --verify "refs/tags/$tag" >/dev/null; then
  echo "tag $tag already exists; nothing to do"
  exit 0
fi

# Numeric field-by-field compare: returns 0 iff $1 > $2 (both bare X.Y.Z).
version_gt() {
  local IFS='.'
  local -a a b
  a=($1)
  b=($2)
  local i
  for i in 0 1 2; do
    if (( a[i] > b[i] )); then return 0; fi
    if (( a[i] < b[i] )); then return 1; fi
  done
  return 1
}

highest=""
for existing in $(git tag -l 'v*'); do
  bare="${existing#v}"
  [[ "$bare" =~ $semver_re ]] || continue
  if [ -z "$highest" ] || version_gt "$bare" "$highest"; then
    highest="$bare"
  fi
done

if [ -n "$highest" ] && ! version_gt "$version" "$highest"; then
  echo "error: version $version is not greater than highest existing tag v$highest" >&2
  exit 1
fi

prev="$(git describe --tags --abbrev=0 2>/dev/null || true)"
if [ -n "$prev" ]; then
  header="Changes since $prev:"
  range="$prev..HEAD"
else
  header="Initial release:"
  range="HEAD"
fi

message_file="$(mktemp)"
trap 'rm -f "$message_file"' EXIT
{
  echo "Release $version"
  echo
  echo "$header"
  echo
  git log --no-merges --pretty=format:'- %s (%h)' "$range"
  echo
} > "$message_file"

git tag -a "$tag" -F "$message_file"
git push origin "refs/tags/$tag"
echo "created and pushed $tag"
