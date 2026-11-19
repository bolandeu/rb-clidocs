# clidocs

Human CLI help in the browser: renders a tool's docs with InSpectra

## Usage

```bash
clidocs render semkit          # ~/Work/tools/docs/semkit/index.html, opened in the browser
clidocs render serp --no-open  # a tool without `docs` is rendered from `describe`
```

Mac only: needs dotnet (`brew install dotnet`) and InSpectra
(`dotnet tool install -g InSpectra.Gen`; found on PATH or in `~/.dotnet/tools`).
`DOTNET_ROOT` defaults to Homebrew's `/opt/homebrew/opt/dotnet/libexec`. The tool
is asked for `describe --json` first and for `docs` only when describe lists it, in
an empty working directory — never a blind `TOOL docs`.

## Development

```bash
uv sync
uv run clidocs --help
gate check                        # the full gate (run before every commit, on this machine)
uv run pytest --snapshot-update  # after changing a command's help; review tests/snapshots/help/
```

`pytest` fails below the coverage floor in `pyproject.toml`; `ruff` includes
the security (`S`) rules; the gate also scans `uv.lock` for known
vulnerabilities when `osv-scanner` is installed (`brew install osv-scanner`),
and says it skipped the scan otherwise. The gate runs locally: `[publish]
gate_command` in `.agents/antagor/antagor.toml`; no workflow runs it.

## Release

The version is the git tag (`vX.Y.Z`) — `pyproject.toml` has no `version =`.
Work goes through Antagor tickets (`.agents/antagor/`); a release (run by the Human) is

```bash
antagor publish --bump   # SemVer; at 0.x: patch = fix/feature, minor = breaking
```

It tags the release, builds `CHANGELOG.md` from the ticket titles and runs
`scripts/deploy.sh`: push `main` with tags to `origin`. Nobody tags or
pushes by hand.

## Install

**On this machine, from a local checkout:**

```bash
uv tool install .
```

**On any other machine (any OS), once this repo is pushed to GitHub — no
PyPI publish needed:**

```bash
uv tool install "rb-clidocs @ git+https://github.com/bolandeu/clidocs.git@vX.Y.Z"
```

Replace `vX.Y.Z` with the latest release tag (a tag cut by
`antagor publish`; never install a branch). This is also how an AI agent
bootstraps this CLI on a fresh machine/sandbox where it isn't installed
yet — see `src/rb_clidocs/data/SKILL.md`.

**Private repo?** The command above is unchanged — `uv` runs git under the
hood, so it authenticates the same way `git clone` does. On a machine
where the install is refused with an auth error, do one of these once:

```bash
gh auth login          # interactive login also sets up git's credential helper
gh auth setup-git      # only needed if gh was logged in with --with-token / in CI
```

or use the SSH form instead of HTTPS:

```bash
uv tool install "rb-clidocs @ git+ssh://git@github.com/bolandeu/clidocs.git@vX.Y.Z"
```

**Update** an installed copy to the latest commit:

```bash
uv tool upgrade rb-clidocs
```

After install, the command `clidocs` is available globally, on
macOS, Linux and Windows alike (see `architecture.md` in the cli-generator
plugin for why: no shelling out, no hardcoded POSIX paths).

To pick up later architecture changes from the `cli-generator` template
itself, run `copier update` in this repo (requires this repo and the
template to both be git repos; see the `cli-generator` plugin's README).

## Architecture

This project follows a fixed CLI architecture:

- `src/rb_clidocs/commands/` — argument parsing only, no business logic.
- `src/rb_clidocs/core/` — services, models, errors: the real logic.
- `src/rb_clidocs/providers/` — external APIs/integrations.
- `src/rb_clidocs/credentials/` — secrets via the OS keychain (`keyring`)
  and environment variables. Secrets never live in `.rb_clidocs/config.toml`.
- `src/rb_clidocs/output/` — human (`rich`) and `--json` rendering.

Run `clidocs doctor` to check environment/config/auth readiness, and
`clidocs --help` for the full command surface. Every command supports
`--json` for machine/agent consumption; errors are structured (`error.code`,
fixed exit codes, `error.action` telling you what to do next) and go to
stderr in human mode, so stdout is always safe to pipe.

A project can require a minimum CLI version in its `.rb_clidocs/config.toml`
(`[cli] min_version = "..."`); an older install refuses with exit 6 and
`uv tool upgrade rb-clidocs` fixes it.

See `src/rb_clidocs/data/SKILL.md` for the agent-facing usage guide
bundled with this package — install it into an AI tool with
`clidocs skill install`, or get it as plain text with
`clidocs --ai` (works even without file access).
