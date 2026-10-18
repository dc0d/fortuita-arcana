# fortuita-arcana

> Fortuita Arcana - playground collection of AI Agent Skills, and other stuff

## Plugins

This repository is a plugin marketplace for [Claude Code](https://code.claude.com/docs/en/plugin-marketplaces) and [GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace). The marketplace is `fortuita-arcana`.

| Plugin | Skills |
| :- | :- |
| `effect-brewery` | `execplans`, `gh-cli`, `local-archive`, `local-implement`, `local-issue`, `local-plan`, `local-wrap-up`, `the-architect` |

The plugin was named `fortuita-arcana` before. If you installed `fortuita-arcana@fortuita-arcana`, uninstall it, then install `effect-brewery@fortuita-arcana` as below.

## Claude Code

### Install

CLI:

```sh
claude plugin marketplace add dc0d/fortuita-arcana
claude plugin install effect-brewery@fortuita-arcana
```

TUI:

```text
/plugin marketplace add dc0d/fortuita-arcana
/plugin install effect-brewery@fortuita-arcana
```

In the TUI, `/plugin install` opens the plugin. Select a scope to install it.

### Update

CLI:

```sh
claude plugin marketplace update fortuita-arcana
claude plugin update effect-brewery@fortuita-arcana
```

TUI:

```text
/plugin marketplace update fortuita-arcana
```

This updates the marketplace and the plugins that you installed from it.

After an install or update, run `/reload-plugins` in an open session, or start a new session.

For scopes, version pins, and auto-update, see [Install and manage plugins](https://code.claude.com/docs/en/discover-plugins).

## GitHub Copilot CLI

### Install

CLI:

```sh
copilot plugin marketplace add dc0d/fortuita-arcana
copilot plugin install effect-brewery@fortuita-arcana
```

TUI:

```text
/plugin marketplace add dc0d/fortuita-arcana
/plugin install effect-brewery@fortuita-arcana
```

### Update

CLI:

```sh
copilot plugin marketplace update fortuita-arcana
copilot plugin update effect-brewery@fortuita-arcana
```

TUI:

```text
/plugin marketplace update fortuita-arcana
/plugin update effect-brewery@fortuita-arcana
```

After an install or update, start a new session, or run `/restart` in an open session.

For more, see [Finding and installing plugins](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing).

## Versioning

The plugin version is a single bare `X.Y.Z` value recorded in the plugin and
marketplace manifests (four spots). To bump it:

```sh
python3 scripts/version.py set 0.2.0
```

The script refuses malformed versions, out-of-sync manifests, and any value
not strictly greater than the current one. `python3 scripts/version.py check`
verifies the manifests agree and prints the current version.

When a bump lands on `main`, the "Tag version" workflow creates and pushes an
annotated `vX.Y.Z` tag (a no-op if the tag exists; it refuses to tag
backwards). Run the tests with:

```sh
python3 -m unittest discover -s tests -v
```

## About the Name

_Fortuita Arcana_ was a magical relic in a TTRPG campaign I once played.
