from .repo import verify_repo, get_project_path
verify_repo('git-secrets')

import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(get_project_path(), '.env'))

from typing import Optional
import typer
from . import version_callback
from ..ansible import ansible_vault
from ..enums import Environments, SecretsCommands


secrets_app = typer.Typer()


@secrets_app.command()
def secrets(
    env: Environments,
    command: SecretsCommands,
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
):
    """
    Manage env-specific ansible-vault secrets.

    For the given configured deployment environment, execute a specified
    ansible-vault command on the secrets file configured for that environment.
    """
    ansible_vault(env.value, command.value)


def run_secrets():
    secrets_app()
