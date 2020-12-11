import os
import subprocess
import sys
from pathlib import Path
from rich import print
from dotenv import load_dotenv
from .config import get_env_config, get_config_dir, get_common_config
from .enums import PLAYBOOKS, Playbooks
from .sh import call
from . import __version__


def call(command, **kwargs):
    if kwargs:
        command = command % kwargs
    print(f'[bold green underline]Executing[/bold green underline][green]: {command}')
    return subprocess.call(command.split())


def get_vault(env, project_name):
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


def ansible_playbook(env, playbook, *ansible_args, **kwargs):
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


def ansible_vault(env, command):
    project_name = get_common_config()['project_name']
    vault_file = get_vault(env, project_name)
    command = f'ansible-vault {command} {vault_file}'
    call(command)


def playbook_path(name):
    return os.path.join(get_config_dir(), name)


def deploy(env, version, *ansible_args, playbooks=None):
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
        if Path(playbook_path(book)) in PLAYBOOKS:
            ansible_playbook(env, playbook_path(book), *ansible_args)
        else:
            print(f'[bold red]Unknown playbook: {book}')
    print('\n[green]Done')
