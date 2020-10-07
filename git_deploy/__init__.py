__version__='1.0.6'


import os
import typer


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


