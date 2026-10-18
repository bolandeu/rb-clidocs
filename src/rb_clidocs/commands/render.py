from __future__ import annotations

import typer

from .. import output
from ..core import render as rendering


@output.guard
def render(
    ctx: typer.Context,
    tool: str = typer.Argument(..., help="The command of an installed tool, e.g. semkit."),
    no_open: bool = typer.Option(False, "--no-open", help="Write the page but do not open it in the browser."),
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
    dry_run: bool = output.DryRunOption,
) -> None:
    """Render a tool's help as an HTML page with search and open it in the browser.

    The page goes to ~/Work/tools/docs/TOOL/index.html, built by InSpectra from the tool's docs document, or from describe when the tool has no docs. Mac only: InSpectra needs dotnet.

    Example: {cli} render semkit --no-open
    -> ~/Work/tools/docs/semkit/index.html
    """
    target = rendering.Target(tool)
    found, source = rendering.document(tool)
    payload = {"tool": tool, "source": source, "document": str(target.document), "html": str(target.html)}
    if output.is_dry_run(ctx):
        output.emit_success(
            ctx,
            {**payload, "result": "dry-run"},
            render_human=lambda d: output.human.echo(f"Dry run: would write {d['html']} (from {d['source']})."),
        )
        return
    page = rendering.write(target, found)
    if not no_open:
        rendering.open_page(page)
    output.emit_success(ctx, payload, render_human=lambda d: output.human.echo(f"{d['html']} (from {d['source']})"))
