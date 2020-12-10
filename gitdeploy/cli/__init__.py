from .. import __version__


import typer


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


