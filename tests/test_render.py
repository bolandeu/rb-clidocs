"""`clidocs render TOOL`: the tool's help document rendered by InSpectra into ~/Work/tools/docs/TOOL/.

The tool and inspectra are fake executables on PATH: the tests check what clidocs
asks them and what it writes, not InSpectra itself (Mac-only, not in the gate).
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import pytest
from typer.testing import CliRunner

from rb_clidocs.cli import app
from rb_clidocs.core import render

DOC = {"opencli": "0.1", "info": {"title": "demo", "version": "1.0"}, "commands": [{"name": "go"}]}
DESCRIBE = {
    "opencli": "0.1",
    "info": {"title": "demo", "version": "1.0"},
    "command": {"name": "demo", "commands": [{"name": "go"}], "exitCodes": [{"code": 0}]},
}


def _script(path: Path, body: str) -> None:
    path.write_text("#!/bin/sh\n" + body)
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


@pytest.fixture
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    home = tmp_path / "home"
    home.mkdir()
    # inspectra writes index.html into --out-dir and records its arguments.
    _script(
        bin_dir / "inspectra",
        f'echo "$@" > {tmp_path}/inspectra.args\n'
        'while [ $# -gt 0 ]; do [ "$1" = --out-dir ] && out="$2"; shift; done\n'
        # like InSpectra, --overwrite empties the output directory first
        'rm -rf "$out" && mkdir -p "$out" && echo "<html>" > "$out/index.html"\n',
    )
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("HOME", str(home))
    opened: list[str] = []
    monkeypatch.setattr(render.webbrowser, "open", lambda url: opened.append(url) or True)
    return {"bin": bin_dir, "home": home, "opened": opened, "tmp": tmp_path}


def _tool(env: dict, body: str) -> None:
    _script(env["bin"] / "demo", f'echo "$@" >> {env["tmp"]}/demo.calls\n' + body)


def _calls(env: dict) -> list[str]:
    path = env["tmp"] / "demo.calls"
    return path.read_text().splitlines() if path.exists() else []


DESCRIBE_WITH_DOCS = {**DESCRIBE, "command": {**DESCRIBE["command"], "commands": [{"name": "go"}, {"name": "docs"}]}}
WITH_DOCS = (
    f"[ \"$1\" = describe ] && echo '{json.dumps(DESCRIBE_WITH_DOCS)}' && exit 0\n"
    f"[ \"$1\" = docs ] && echo '{json.dumps(DOC)}' && exit 0\nexit 2\n"
)


def _render(*args: str):
    return CliRunner().invoke(app, ["--json", "render", *args])


def _out(env: dict) -> Path:
    return env["home"] / "Work" / "tools" / "docs" / "demo"


def test_a_tool_with_docs_is_rendered_from_its_docs_document(env: dict) -> None:
    _tool(env, WITH_DOCS)
    result = _render("demo", "--no-open")
    assert result.exit_code == 0, result.output
    assert json.loads((_out(env) / "opencli.json").read_text()) == DOC
    assert (_out(env) / "index.html").is_file()
    args = (env["tmp"] / "inspectra.args").read_text().split()
    assert args[:3] == ["render", "file", "html"]
    assert args[3].endswith("opencli.json")
    assert args[4:] == ["--out-dir", str(_out(env)), "--overwrite"]
    data = json.loads(result.output)
    assert data["source"] == "docs"
    assert data["html"] == str(_out(env) / "index.html")
    assert env["opened"] == []


def test_a_tool_without_docs_is_rendered_from_describe_with_the_command_lifted_to_the_root(env: dict) -> None:
    _tool(env, f"[ \"$1\" = describe ] && echo '{json.dumps(DESCRIBE)}' && exit 0\nexit 2\n")
    result = _render("demo", "--no-open")
    assert result.exit_code == 0, result.output
    lifted = json.loads((_out(env) / "opencli.json").read_text())
    assert lifted == {
        "opencli": "0.1",
        "info": {"title": "demo", "version": "1.0"},
        "commands": [{"name": "go"}],
        "exitCodes": [{"code": 0}],
    }
    assert json.loads(result.output)["source"] == "describe"
    assert _calls(env) == ["describe --json"]  # docs is never run blind: it may be another command's argument


def test_a_tool_whose_describe_fails_is_never_asked_for_docs(env: dict) -> None:
    _tool(env, "exit 2\n")
    _render("demo", "--no-open")
    assert _calls(env) == ["describe --json"]


def test_without_no_open_the_page_is_opened_in_the_browser(env: dict) -> None:
    _tool(env, WITH_DOCS)
    assert _render("demo").exit_code == 0
    assert env["opened"] == [(_out(env) / "index.html").as_uri()]


def test_a_tool_that_is_not_installed_is_a_dependency_error(env: dict) -> None:
    result = _render("nope-not-here", "--no-open")
    assert result.exit_code == 1
    error = json.loads(result.output)["error"]
    assert error["code"] == "DEPENDENCY_TOO_OLD"
    assert "nope-not-here" in error["message"]


def test_a_tool_with_neither_docs_nor_describe_is_a_clear_error(env: dict) -> None:
    _tool(env, "exit 2\n")
    result = _render("demo", "--no-open")
    assert result.exit_code == 5
    error = json.loads(result.output)["error"]
    assert error["code"] == "PROVIDER_ERROR"
    assert "neither docs nor describe" in error["message"]
    assert not _out(env).exists()


def test_a_failing_docs_command_is_reported_not_replaced_by_describe(env: dict) -> None:
    _tool(
        env,
        f"[ \"$1\" = describe ] && echo '{json.dumps(DESCRIBE_WITH_DOCS)}' && exit 0\n"
        '[ "$1" = docs ] && echo "example outside path" >&2 && exit 1\nexit 0\n',
    )
    result = _render("demo", "--no-open")
    assert result.exit_code == 5
    assert "example outside path" in json.loads(result.output)["error"]["message"]


def test_a_failing_inspectra_is_reported(env: dict) -> None:
    _tool(env, WITH_DOCS)
    _script(env["bin"] / "inspectra", 'echo "bad document" >&2\nexit 3\n')
    result = _render("demo", "--no-open")
    assert result.exit_code == 5
    error = json.loads(result.output)["error"]
    assert error["provider"] == "inspectra"
    assert "bad document" in error["message"]


def test_dry_run_writes_nothing_and_says_where_it_would_write(env: dict) -> None:
    _tool(env, WITH_DOCS)
    result = CliRunner().invoke(app, ["--json", "--dry-run", "render", "demo"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["html"] == str(_out(env) / "index.html")
    assert not _out(env).exists()
    assert env["opened"] == []


def test_dotnet_root_is_set_for_inspectra_only_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DOTNET_ROOT", raising=False)
    assert render.inspectra_env()["DOTNET_ROOT"] == render.DEFAULT_DOTNET_ROOT
    monkeypatch.setenv("DOTNET_ROOT", "/custom")
    assert render.inspectra_env()["DOTNET_ROOT"] == "/custom"


def test_the_tool_runs_in_an_empty_directory(env: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    # A tool without describe may read 'describe' as a folder in the current directory (hostme deploys one).
    work = env["tmp"] / "work"
    (work / "describe").mkdir(parents=True)
    monkeypatch.chdir(work)
    _tool(env, f"ls -A > {env['tmp']}/demo.ls\nexit 2\n")
    _render("demo", "--no-open")
    assert (env["tmp"] / "demo.ls").read_text() == ""
