# fortuita-arcana

> Fortuita Arcana - playground collection of AI Agent Skills, and other stuff

## Usage

### From Claude

This repository is a [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces). Inside Claude Code, run:

```
/plugin marketplace add dc0d/fortuita-arcana
/plugin install effect-brewery@fortuita-arcana
```

This installs the `effect-brewery` plugin, making its skills (such as `the-architect`) available in all your projects. To get newer versions later, run `/plugin marketplace update fortuita-arcana`.

### From GitHub Copilot

This repository is also a [Copilot CLI plugin marketplace](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace). In a terminal, run:

```sh
copilot plugin marketplace add dc0d/fortuita-arcana
copilot plugin install effect-brewery@fortuita-arcana
```

To get newer versions later, run `copilot plugin update effect-brewery`.

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
