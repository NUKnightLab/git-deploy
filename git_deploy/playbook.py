from .repo import verify_repo, get_project_path
verify_repo('git-playbook')

import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(get_project_path(), '.env'))

from typing import Optional
from . import version_callback
from .ansible import ansible_playbook
from .enums import Environments, Playbooks
import typer


context_settings = {
    'ignore_unknown_options': True,
    'allow_extra_args': True
}


playbook_app = typer.Typer()


@playbook_app.command(context_settings=context_settings)
def playbook(
    ctx: typer.Context,
    env: Environments,
    playbook: Playbooks,
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
):
    from .ansible import builtin_playbook
    ansible_args = ctx.args 
    builtin_playbook(env.value, playbook.value, *ansible_args)


def run_playbook():
    playbook_app()
