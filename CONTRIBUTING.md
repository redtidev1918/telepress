# Contributing to TelePress

Thank you for improving TelePress. Small, focused pull requests with tests and
clear commit messages are easiest to review and release.

## Development setup

TelePress supports Python 3.10 and newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --editable ".[dev]"
```

Run the same core checks used by CI:

```bash
python -m pytest --cov
python -m build
python -m twine check dist/*
```

Tests must not require real Telegraph or image-host credentials. Mock network
boundaries and use temporary files for filesystem behavior.

## Commit messages

The release workflow uses
[Conventional Commits](https://www.conventionalcommits.org/) to calculate the
next version and generate release notes.

```text
fix: clean temporary files when publishing fails
feat: add a new image host
docs: document custom API configuration
refactor: simplify gallery pagination
feat!: remove a deprecated public method
```

- `fix:` produces a patch release.
- `feat:` produces a minor release.
- `type!:` or a `BREAKING CHANGE:` footer marks a breaking release. Before
  1.0 it increments the minor version; from 1.0 onward it increments the major
  version.
- Documentation, test, build, and maintenance commits appear in history but do
  not force a release by themselves.

Keep the subject imperative, concise, and scoped to one logical change.

## Pull requests

Before requesting review:

- Add or update tests for behavior changes.
- Update both `README.md` and `README_CN.md` when user-facing behavior changes.
- Do not edit `src/telepress/version.py` or `CHANGELOG.md` for ordinary pull
  requests; the release pull request manages them.
- Confirm the complete local test suite passes.
- Explain compatibility or security implications in the pull request body.

See [docs/RELEASING.md](docs/RELEASING.md) for maintainer release operations.
