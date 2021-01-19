# Verify git repository first thing. In order to have a command-specific
# error message, we need to do this within each command module, which also
# means that the load_dotenv has to happen within each module instead of a
# common location.
from ..repo import verify_repo, get_project_path
verify_repo('git-deploy')

import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(get_project_path(), '.env'))

from typing import List, Optional
from rich import print
import typer
from . import version_callback
from ..ansible import deploy as ansible_deploy
from ..enums import Environments, Versions, Playbooks


context_settings = {
    'ignore_unknown_options': True,
    'allow_extra_args': True
}


deploy_app = typer.Typer()


@deploy_app.command(context_settings=context_settings)
def deploy(
    ctx: typer.Context,
    env: Environments,
    project_version: Versions,
    playbook: List[Playbooks] = typer.Option([]),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
):
    """
    Deploy a project version to an environment.

    For the given configured deployment environment, deploy the specified
    project version to that environment.
    """
    if playbook:
        playbook = [p.value for p in playbook]
    env = env.value
    project_version = project_version.value
    ansible_args = ctx.args 
    ansible_args.extend([
        '-e', f'project_version={project_version}',
        '-e', f'project_root={get_project_path()}',
    ])
    print(
        '[blue]Passing arguments to ansible commands:[/blue] %s\n' %
        ' '.join(ansible_args))
    ansible_deploy(env, None, *ansible_args, playbooks=playbook)


def run_deploy():
    deploy_app()
