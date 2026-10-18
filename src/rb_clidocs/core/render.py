"""A tool's help document rendered by InSpectra into ~/Work/tools/docs/<tool>/index.html.

The document is the tool's `docs` output (cli-generator template >= 1.17: OpenCLI with the
commands at the root). A tool without `docs` falls back to `describe --json`, whose root
`command` is lifted to the top level so InSpectra shows its commands. Rendering the HTML is
InSpectra's job (`inspectra render file html`); this module only feeds it and opens the page.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import webbrowser
from dataclasses import dataclass
from pathlib import Path

from .errors import DependencyTooOld, ProviderError

DEFAULT_DOTNET_ROOT = "/opt/homebrew/opt/dotnet/libexec"  # Homebrew's dotnet: inspectra needs it to start
TIMEOUT = 120


@dataclass(frozen=True)
class Target:
    """Where the document and the page of one tool go."""

    tool: str

    @property
    def directory(self) -> Path:
        return Path.home() / "Work" / "tools" / "docs" / self.tool

    @property
    def document(self) -> Path:
        return self.directory / "opencli.json"

    @property
    def html(self) -> Path:
        return self.directory / "index.html"


def document(tool: str) -> tuple[dict, str]:
    """The help document of `tool` and its source: `docs`, or `describe` when the tool has no `docs`.

    `describe --json` comes first and decides: `docs` runs only when describe lists it. A tool
    without describe may take `docs` as an argument of another command (hostme deploys a folder
    named docs), so it is never run blind.
    """
    exe = shutil.which(tool)
    if exe is None:
        raise DependencyTooOld(tool, None, None)
    describe = _run([exe, "describe", "--json"])
    if describe.returncode != 0:
        raise ProviderError(
            tool,
            "has neither docs nor describe",
            action=f"Update {tool} to cli-generator template 1.17 or later (copier update), then retry.",
        )
    described = _json(tool, "describe --json", describe.stdout)
    if not any(command.get("name") == "docs" for command in described.get("command", {}).get("commands", [])):
        return lifted(described), "describe"
    docs = _run([exe, "docs"])
    if docs.returncode != 0:
        raise ProviderError(tool, f"'{tool} docs' failed: {_tail(docs)}", action=f"Fix '{tool} docs', then retry.")
    return _json(tool, "docs", docs.stdout), "docs"


def lifted(described: dict) -> dict:
    """A `describe` document with its root `command` at the top level, as InSpectra reads it."""
    command = {key: value for key, value in described.get("command", {}).items() if key != "name"}
    return {"opencli": described.get("opencli"), "info": described.get("info"), **command}


def inspectra_env() -> dict[str, str]:
    """The environment for inspectra: DOTNET_ROOT defaults to Homebrew's dotnet when it is unset."""
    return {**os.environ, "DOTNET_ROOT": os.environ.get("DOTNET_ROOT") or DEFAULT_DOTNET_ROOT}


def inspectra() -> str:
    """Path of inspectra: on PATH, else where `dotnet tool install -g` puts it."""
    found = shutil.which("inspectra") or shutil.which("inspectra", path=str(Path.home() / ".dotnet" / "tools"))
    if found is None:
        raise DependencyTooOld("inspectra", None, None, dist="InSpectra.Gen (dotnet tool install -g InSpectra.Gen)")
    return found


def write(target: Target, found: dict) -> Path:
    """Render the document with InSpectra, then keep it next to the page; the path of the page.

    InSpectra empties its output directory (`--overwrite`), so it reads the document from a
    temporary file and the copy in the directory is written after it.
    """
    exe = inspectra()
    text = json.dumps(found, ensure_ascii=False, indent=2) + "\n"
    with tempfile.TemporaryDirectory() as scratch:
        source = Path(scratch) / target.document.name
        source.write_text(text, encoding="utf-8")
        argv = [exe, "render", "file", "html", str(source), "--out-dir", str(target.directory), "--overwrite"]
        result = _run(argv, env=inspectra_env())
    if result.returncode != 0:
        raise ProviderError("inspectra", _tail(result), action="Check the document it names, then retry.")
    target.document.write_text(text, encoding="utf-8")
    return target.html


def open_page(page: Path) -> None:
    webbrowser.open(page.as_uri())


def _run(argv: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Run in an empty directory: a tool that reads an argument as a path finds nothing to act on."""
    with tempfile.TemporaryDirectory() as empty:
        return subprocess.run(  # noqa: S603 — argv of a resolved executable
            argv, capture_output=True, text=True, timeout=TIMEOUT, check=False, env=env, cwd=empty
        )


def _json(tool: str, command: str, text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProviderError(tool, f"'{tool} {command}' did not print JSON: {exc}") from exc


def _tail(result: subprocess.CompletedProcess[str]) -> str:
    text = (result.stderr or result.stdout).strip()
    return text.splitlines()[-1] if text else f"exit code {result.returncode}"
