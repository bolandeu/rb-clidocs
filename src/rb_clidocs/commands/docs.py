from __future__ import annotations

from pathlib import Path

import typer

from .. import output
from ..core import docs as docs_module
from ..core.errors import InvalidArguments


@output.guard
def docs(
    ctx: typer.Context,
    out: Path = typer.Option(None, "--out", metavar="FILE", help="Write the document to FILE (replaced when it exists); by default to stdout."),
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
    verbose: bool = output.VerboseOption,
) -> None:  # fmt: skip
    """Write the help of every command as one document for people: OpenCLI with the commands at the root.

    The document follows the help standard: each command has its summary, description and examples apart, and each option ends with its default and allowed values. The same version writes the same bytes. A viewer such as InSpectra renders it as HTML.

    Example: {cli} docs --out docs.json
    """
    text = docs_module.text(ctx.find_root().command)
    if out is None:
        typer.echo(text, nl=False)
        return
    try:
        out.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise InvalidArguments(f"Cannot write {out}: {exc.strerror}.") from exc
