---
id: CLIDOCS-001
title: Apply the verified copier update to template v1.27.1
status: in_progress
attempts: 1
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: human
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

## Feedback

### Attempt 1: checks failed

- `uvx --from 'git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@v1.27.1#subdirectory=gate' rb-release --project /Users/bolandau/Work/tools/clidocs check` (exit 1)

```
release: gate step 'pytest' failed:
E       AssertionError: assert 'items: [1]' in 'items: \x1b[1m[\x1b[0m\x1b[1;36m1\x1b[0m\x1b[1m]\x1b[0m\n'
E        +  where 'items: \x1b[1m[\x1b[0m\x1b[1;36m1\x1b[0m\x1b[1m]\x1b[0m\n' = <Result SystemExit(2)>.stdout
E       AssertionError: assert [+ received] == [- snapshot]
E           
E           ...
E           
E         - ╭─ Options ────────────────────────────────────────────────────────────────────────────────────────╮
E         + ╭─ Options ────────────────────────────────────────────────────────────────────╮
E         - │ --help          Show this message and exit.                                                      │
E         + │ --help          Show this message and exit.                                  │...
E         
E         ...Full output truncated (11 lines hidden), use '-vv' to show
E       AssertionError: assert [+ received] == [- snapshot]
E           
E           ...
E           
E         -  Report every provider's credential: where it comes from and whether it works. Never prints values.
E         +  Report every provider's credential: where it comes from and whether it works.
E         +  Never prints values.
E           ...
E         
E         ...Full output truncated (28 lines hidden), use '-vv' to show
E       AssertionError: assert [+ received] == [- snapshot]
E           
E           ...
E           
E         + ╭─ Options ────────────────────────────────────────────────────────────────────╮
E         
…
-------------
14 snapshots failed. 1 snapshot passed.
=========================== short test summary info ============================
FAILED tests/test_cli.py::test_report_with_a_problem_keeps_the_payload - AssertionError: assert 'items: [1]' in 'items: \x1b[1m[\x1b[0m\x1b[1;36m1\x...
FAILED tests/test_help.py::test_help_snapshot[auth] - AssertionError: assert [+ received] == [- snapshot]
FAILED tests/test_help.py::test_help_snapshot[auth-status] - AssertionError: assert [+ received] == [- snapshot]
FAILED tests/test_help.py::test_help_snapshot[config] - AssertionError: assert [+ received] == [- snapshot]
FAILED tests/test_help.py::test_help_snapshot[config-get] - AssertionError: assert [+ received] == [- snapshot]
FAILED tests/test_help.py::test_help_snapshot[config-list] - AssertionError: assert [+ received] == [- snapshot]
FAILED tests/test_help.py::test_help_snapshot[config-set] - AssertionError: assert [+ received] == [- snapshot]
FAILED tests/test_help.py::test_help_snapshot[describe] - AssertionError: assert [+ received] == [- snapshot]
FAILED tests/test_help.py::test_help_snapshot[docs] - AssertionError: assert [+ received] == [- snapshot]
FAILED tests/test_help.py::test_help_snapshot[doctor] - AssertionError: assert [+ received] == [- snapshot]
FAILED tests/test_help.py::test_help_snapshot[init] - AssertionError: assert [+ received] == [- snapshot]
FAILED tests/test_help.py::test_help_snapshot[render] - AssertionError: assert [+ received] == [- snapshot]
FAILED tests/test_help.py::test_help_snapshot[skill] - AssertionError: assert [+ received] == [- snapshot]
FAILED tests/test_help.py::test_help_snapshot[skill-install] - AssertionError: assert [+ received] == [- snapshot]
FAILED tests/test_help.py::test_help_snapshot[status] - AssertionError: assert [+ received] == [- snapshot]
FAILED tests/test_scripts.py::test_antagor_project_config - KeyError: 'worker'
======================== 16 failed, 170 passed in 5.83s ========================
release: code failed
```

### Blocked: no_progress (head 71dc339c16ffc4c91ab45f782691d93bebde4fef)

Work is on the branch (patch applied, patch file deleted, one commit 71dc339); recheck the same work.
