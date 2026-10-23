---
id: CLIDOCS-001
title: Apply the verified copier update to template v1.27.1
status: ideas
attempts: 0
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: null
worker: claude-code
type: chore
owns_paths:
- .copier-answers.yml
- .gitea
- .github/dependabot.yml
- .gitignore
- .gitleaks.toml
- pyproject.toml
- scripts/check_command_docstrings.py
- scripts/detach.py
- scripts/release.py
- src/rb_clidocs
- tests
- uv.lock
- docs/plans/copier-update-v1.27.1.patch
test_paths: []
docs: none
tools: []
worker_args: null
decision: false
visual: null
depends_on: []
budget_usd: null
epic: null
spec_refs: []
checks:
- uv run pytest
- uv run ruff check .
- uv run ruff format --check .
- uv lock --check
- uvx --from 'git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@v1.27.1#subdirectory=gate'
  rb-release --project /Users/bolandau/Work/tools/clidocs check
resident: null
tool: null
pr: null
translation: Применить проверенный патч обновления шаблона cli-generator до v1.27.1
  и удалить патч в том же коммите.
---

Apply the patch docs/plans/copier-update-v1.27.1.patch with 'git apply --index docs/plans/copier-update-v1.27.1.patch' on the clean tree, then delete the patch file in the same commit ('git rm docs/plans/copier-update-v1.27.1.patch'; remove docs/plans/ if empty). Do not edit anything else: the merge is already verified (rb-release gate passes with the patch applied). The patch includes the inspectra [[tool.rb.external]] block in pyproject.toml (the template merge had dropped it) and antagor_prefix: CLIDOCS in .copier-answers.yml. If a check fails, report the failure; do not change the patched code.

## Out of scope

- Any change beyond applying the patch and deleting it
- AGENTS.md, CODING_STANDARDS.md and .agents/antagor/ (already committed)
