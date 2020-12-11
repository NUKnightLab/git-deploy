import os
import subprocess
import sys
from pathlib import Path
from typing import Optional
from rich import print
from dotenv import load_dotenv
from .config import get_env_config, get_config_dir, get_common_config
from .enums import PLAYBOOKS, Playbooks
from . import __version__


def call(command:str, **kwargs) -> int:
    if kwargs:
        command = command % kwargs
    print(f'[bold green underline]Executing[/bold green underline][green]: {command}')
    return subprocess.call(command.split())


def get_vault(env:str, project_name) -> Optional[Path]:
    vault_dir = os.environ.get('GIT_DEPLOY_VAULT_DIR')
    if vault_dir:
        vault_path = Path(vault_dir) / project_name / f'vault.{env}.yml'
        if not vault_path.exists():
            print(f'[bold red]' \
            'No vault file found at: {vault_path}. Executing without vault.\n')
    else:
        vault_path = Path.home() / '.vault' / project_name / f'vault.{env}.yml'
        if not vault_path.exists():
            print(f'[bold yellow]'\
            'No vault file available. Executing without vault.\n')
    if vault_path.exists():
        return vault_path
    return None


def ansible_playbook(env:str, playbook:str, *ansible_args, **kwargs) -> None:
    cfg = get_env_config(env)
    vault = get_vault(env, cfg['project_name'])
    command = 'ansible-playbook'
    for a in ansible_args:
        command += f' {a}'
    command += f' -e env={env}'
    command += ' -e config_dir=%s' % get_config_dir()
    if vault is not None:
        command += f' -e vault={vault}'
    for k,v in kwargs.items():
        command += f' -e {k}={v}'
    command += f' {playbook}'
    call(command)


def ansible_vault(env, command:str) -> None:
    project_name = get_common_config()['project_name']
    vault_file = get_vault(env, project_name)
    command = f'ansible-vault {command} {vault_file}'
    call(command)


def playbook_path(name:str) -> str:
    return os.path.join(get_config_dir(), name)


def deploy(env, version:str, *ansible_args, playbooks=None) -> None:
    gitdeploy_version = get_common_config().get('gitdeploy_version')
    if gitdeploy_version and gitdeploy_version != __version__:
        print('[bold red]' \
            '\nThis project is designed for git-deploy version %s. Please ' \
            'checkout the %s version branch of git-deploy before executing.' % (
            gitdeploy_version, gitdeploy_version))
        sys.exit()
    conf = get_env_config(env)
    if not playbooks:
        if 'playbooks' in conf:
            playbooks = get_env_config(env)['playbooks']
        else:
            print('[bold red]playbooks must be specified')
            sys.exit()
    for book in playbooks:
        if book in PLAYBOOKS:
            ansible_playbook(env, playbook_path(book), *ansible_args)
        else:
            print(f'[bold red]Unknown playbook: {book}')
    print('\n[green]Done')
