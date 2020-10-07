import os
from pathlib import Path
from enum import Enum
from typing import Optional
from .ansible import ansible_vault, ansible_playbook
from .ansible import deploy as ansible_deploy
from .ansible import PLAYBOOKS_DIR, get_config_dir
import typer

from git import Repo

__version__ = "0.1.0"


class SecretsCommands(str, Enum):
    create = "create"
    decrypt = "decrypt"
    edit = "edit"
    view = "view"
    encrypt = "encrypt"
    rekey = "rekey"


playbooks_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
        PLAYBOOKS_DIR)

Playbooks = Enum('Playbooks', {
    f.name:f.name for f in list(Path(playbooks_dir).glob('*.yml')) })


Environments = Enum('Environments', {
    f.name.split('.')[1]:f.name.split('.')[1]
    for f in Path(get_config_dir()).glob('config.*.yml')
    if f.name != 'config.common.yml' })

repo = Repo(os.getcwd())


Versions = Enum('Versions',
    { x.name:x.name for x in repo.branches + repo.tags })


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


def secrets_callback(env: str, command:str):
    pass 


def secrets(
    env: Environments,
    command: SecretsCommands,
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
):
    ansible_vault(env.value, command)


playbook_app = typer.Typer()

@playbook_app.callback()
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

deploy_app = typer.Typer()

#@deploy_app.callback()
#def deploy_callback(ctx: typer.Context):
#    print('deploy callback', ctx)


def playbook_callback(*args):
    print('playbook callback')
    print(args)


@deploy_app.callback()
def _deploy(
    ctx: typer.Context,
    env: Environments,
    project_version: Versions,
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
    playbook: Optional[str] = typer.Option(
        None, "--playbook", is_eager=True
    ),
):
    env = env.value
    print('deploy', env, project_version.value)
    ansible_args = ctx.args 
    ansible_args.extend(['-e', f'project_version={project_version}'])
    print('[blue]Passing arguments to ansible commands:[/blue] %s\n' % ' '.join(ansible_args))
    if playbook is not None:
        ansible_playbook(env, playbook, *ansible_args)
    #else:
    #ansible_deploy(env, project_version, *ansible_args)
    print('calling ansible_deploy')
    ansible_deploy(env, None, *ansible_args)


def run_secrets():
    typer.run(secrets)

def run_playbook():
    typer.run(playbook)

def deploy():
    typer.run(_deploy)
    

