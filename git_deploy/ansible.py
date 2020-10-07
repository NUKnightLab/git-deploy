import os
import sys
import yaml
from rich import print
from dotenv import load_dotenv
from .sh import call
from .repo import get_project_path
from . import __version__

PLAYBOOKS_DIR = 'playbooks'



def get_vault_dir():
    return os.environ.get('GIT_DEPLOY_VAULT_DIR')


def get_config_dir():
    return os.path.join(get_project_path(),
        os.environ.get('GIT_DEPLOY_PROJECT_CONFIG_DIR', 'deploy'))


def get_common_config():
    fn = os.path.join(get_config_dir(), 'config.common.yml')
    with open(fn) as f:
        cfg = yaml.safe_load(f)
    return cfg


_common_config = None
def common_config():
    global _common_config
    if _common_config is None:
        _common_config = get_common_config()
    return _common_config
    


def ansible_playbook(env, playbook, *ansible_args, **kwargs):
    command = 'ansible-playbook'
    for a in ansible_args:
        command += f' {a}'
    command += f' -e env={env}'
    #command += ' -e project_root=%s' % get_project_path()
    command += ' -e config_dir=%s' % get_config_dir()
    command += ' -e vault_dir=%s' % get_vault_dir()
    for k,v in kwargs.items():
        command += f' -e {k}={v}'
    command += f' {playbook}'
    call(command)


def ansible_vault(env, command):
    project_name = common_config()['project_name']
    vault_file = os.path.join(get_vault_dir(), project_name, f'vault.{env}.yml')
    command = f'ansible-vault {command} {vault_file}'
    call(command)


def playbook_path(name):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
        PLAYBOOKS_DIR)
    return os.path.join(path, name)


def builtin_playbook(env, playbook_name, *ansible_args):
    playbook = playbook_path(playbook_name)
    ansible_playbook(env, playbook, *ansible_args)


def deploy(env, version, *ansible_args):
    gitdeploy_version = common_config().get('gitdeploy_version')
    if gitdeploy_version and gitdeploy_version != __version__:
        print('[bold red]' \
            '\nThis project is designed for git-deploy version %s. Please ' \
            'checkout the %s version branch of git-deploy before executing.' % (
            gitdeploy_version, gitdeploy_version))
        sys.exit()
    if common_config()['type'] == 'repository':
        builtin_playbook(env, 'deploy.repository.yml', *ansible_args)
        return
    elif common_config()['type'] == 'static':
        builtin_playbook(env, 'deploy.repository.yml', *ansible_args)
        builtin_playbook(env, 'deploy.static.yml', *ansible_args)
        return
    builtin_playbook(env, 'deploy.repository.yml', *ansible_args)
    if common_config().get('docker_compose_file'):
        builtin_playbook(env, 'build.containers.yml', *ansible_args)
        builtin_playbook(env, 'deploy.web.yml', *ansible_args)
    else:
        builtin_playbook(env, 'deploy.python.yml', *ansible_args)
        builtin_playbook(env, 'deploy.static.yml', *ansible_args)
        builtin_playbook(env, 'deploy.web.yml', *ansible_args)
    print('\n[green]Done')
