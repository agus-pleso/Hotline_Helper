"""Command-line entry point: `hotline-helper ...`"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from hotline_helper.loader import (
    DataError,
    country_files_dir,
    iter_country_paths,
    load_all,
    load_country_file,
)

app = typer.Typer(help="Hotline Helper — government-sourced crisis hotline data.", no_args_is_help=True)
console = Console()


@app.command()
def serve(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
) -> None:
    """Run the FastAPI server locally."""
    uvicorn.run("hotline_helper.api:app", host=host, port=port, reload=reload)


@app.command()
def validate(
    country: Annotated[
        str | None,
        typer.Option("--country", "-c", help="ISO code; validate only this file."),
    ] = None,
) -> None:
    """Validate every country YAML against the schema. Exit nonzero on any failure."""
    paths = (
        [country_files_dir() / f"{country.upper()}.yml"]
        if country
        else list(iter_country_paths())
    )
    if not paths:
        console.print("[yellow]No country files found.[/yellow]")
        raise typer.Exit(code=1)

    failures: list[tuple[Path, str]] = []
    for path in paths:
        if not path.exists():
            failures.append((path, "file not found"))
            continue
        try:
            load_country_file(path)
        except DataError as e:
            failures.append((path, str(e)))

    if failures:
        for path, msg in failures:
            console.print(f"[red]✗[/red] {path.name}: {msg}")
        console.print(f"\n[red]{len(failures)} file(s) failed validation.[/red]")
        raise typer.Exit(code=1)

    console.print(f"[green]✓ All {len(paths)} country files valid.[/green]")


@app.command(name="list")
def list_cmd() -> None:
    """Print a one-line summary of every country."""
    table = Table(title="Hotline Helper — coverage")
    table.add_column("ISO", style="cyan")
    table.add_column("Country")
    table.add_column("Hotlines", justify="right")
    table.add_column("Status")
    table.add_column("Last updated")
    for iso, cf in sorted(load_all().items()):
        status = cf.metadata.verification_status
        status_str = status if isinstance(status, str) else status.value
        color = {
            "verified": "green",
            "unverified": "yellow",
            "no_government_source": "dim",
        }.get(status_str, "white")
        table.add_row(
            iso,
            cf.country.name,
            str(len(cf.hotlines)),
            f"[{color}]{status_str}[/{color}]",
            cf.metadata.last_updated.isoformat(),
        )
    console.print(table)


@app.command()
def build_static(
    output: Annotated[Path, typer.Option("--output", "-o")] = Path("dist/api"),
) -> None:
    """Build the static JSON tree (countries/, categories/, index.json)."""
    from scripts.build_static import build  # local import to avoid heavy import at CLI start

    build(output)


@app.command()
def scrape(
    country: Annotated[
        str | None,
        typer.Option("--country", "-c", help="ISO code; scrape only this country."),
    ] = None,
    write: Annotated[
        bool,
        typer.Option("--write", help="Write changes to YAML. Without it, prints diff and exits."),
    ] = False,
) -> None:
    """Run the scraper(s). With --write, updates YAML files in place."""
    from hotline_helper.scraper.runner import run

    changed = run(country=country, write=write)
    if not changed:
        console.print("[green]No changes detected.[/green]")
        return
    console.print(f"[yellow]{len(changed)} country file(s) would change:[/yellow]")
    for iso in changed:
        console.print(f"  • {iso}")
    if not write:
        console.print("\n[dim]Re-run with --write to apply.[/dim]")


@app.command()
def export_json(
    iso_code: str,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    """Print or write one country's JSON."""
    from hotline_helper.loader import get_country

    cf = get_country(iso_code)
    if cf is None:
        console.print(f"[red]Country '{iso_code}' not found.[/red]")
        raise typer.Exit(code=1)
    payload = json.dumps(cf.model_dump(mode="json"), indent=2, ensure_ascii=False)
    if output:
        output.write_text(payload, encoding="utf-8")
        console.print(f"[green]Wrote {output}[/green]")
    else:
        sys.stdout.write(payload + "\n")


if __name__ == "__main__":
    app()
