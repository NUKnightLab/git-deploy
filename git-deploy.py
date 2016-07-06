#!/usr/bin/env python
"""
git subcommand to remotely deploy projects. Manages merging of git branches.
Uses Ansible for the heavy lifting of deploying branches to remote servers,
restarting appropriate services, and syncing static media to S3.

If you require support for Python3 projects or non-python projects or for
using specific versions of git-deploy itsef, call this via the provided
`git-deploy.wrapper.sh`. See the included README for details.
"""
import os
import sys
from subprocess import check_output as _check_output
from subprocess import call as _call
import yaml
from version import __version__

WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'

ASSETS_DIR = os.environ.get('GIT_DEPLOY_ASSETS_DIR',
    os.path.expanduser('~/.git-deploy'))


def _sh(*args):
    return _check_output(args).decode('utf-8').strip()


def sh(command, **kwargs):
    if kwargs:
        command = command % kwargs
    return _sh(*command.split())


def get_playbooks_dir():
    if os.environ.get('GIT_DEPLOY_PLAYBOOKS_DIR'):
        return os.environ['GIT_DEPLOY_PLAYBOOKS_DIR']
    else:
        dirname = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(dirname, 'ansible')


def get_vault_dir():
    return os.environ.get('GIT_DEPLOY_VAULT_DIR',
        os.path.join(ASSETS_DIR, 'vault'))


def get_vault_password_file():
    return os.environ.get('GIT_DEPLOY_VAULT_PASSWORD_FILE',
        os.path.join(ASSETS_DIR, 'vault_password'))


def get_project_path():
    return sh('git rev-parse --show-toplevel')


def get_config_dir():
    return os.path.join(get_project_path(),
        os.environ.get('GIT_DEPLOY_PROJECT_CONFIG_DIR', 'deploy'))


def call(command, **kwargs):
    if kwargs:
        command = command % kwargs
    print(command)
    return _call(command.split())


def usage():
    print('Usage:')
    envs = SUPPORTED_ENVIRONMENTS
    if len(envs.keys()) > 0:
        print('git-deploy (%s) [options]' % '|'.join(envs.keys()))
        print('\noptions:')
        print(' --verbose')
    else:
        print('No deployment environments found. ' \
            'Please add supported_envs to your Ansible configs')


def get_common_config():
    fn = os.path.join(get_config_dir(), 'config.common.yml')
    with open(fn) as f:
        cfg = yaml.safe_load(f)
    return cfg
COMMON_CONFIG = get_common_config()
SUPPORTED_ENVIRONMENTS = COMMON_CONFIG['supported_envs']


def ansible_playbook(env, playbook, verbose, **kwargs):
    hostfile = os.environ.get('GIT_DEPLOY_INVENTORY',
        os.path.join(ASSETS_DIR, 'hosts'))
    playbook = os.path.join(get_playbooks_dir(), playbook)
    command = 'ansible-playbook'
    if verbose:
        command += ' -vvv'
    if hostfile:
        command += ' -i %s' % hostfile
    command += ' -e env=%s' % env
    command += ' -e project_root=%s' % get_project_path()
    command += ' -e config_dir=%s' % get_config_dir()
    command += ' -e vault_dir=%s' % get_vault_dir()
    for k,v in kwargs.items():
        command += ' -e %s=%s' % (k,v)
    command += ' %s' % playbook
    command += ' --vault-password-file %s' % get_vault_password_file()
    call(command)


def sync_local_repository(env, verbose):
    ansible_playbook(env, 'local.repository.yml', verbose, merge_from=SUPPORTED_ENVIRONMENTS[env])


def deploy_repository(env, verbose):
    ansible_playbook(env, 'deploy.repository.yml', verbose)


def deploy_application(env, verbose):
    ansible_playbook(env, 'deploy.python.yml', verbose)


def deploy_web(env, verbose):
    ansible_playbook(env, 'deploy.web.yml', verbose)


def deploy_static(env, verbose, project_virtualenv):
    ansible_playbook(env, 'deploy.static.yml', verbose,
        project_virtualenv=project_virtualenv)


SUPPORTED_PLAYBOOKS = [
    'deploy.python.yml',
    'deploy.static.yml',
    'deploy.repository.yml',
    'deploy.web.yml'
]

def deploy(env, verbose=False, project_virtualenv=None, playbook=None):
    gitdeploy_version = COMMON_CONFIG.get('gitdeploy_version')
    if gitdeploy_version and gitdeploy_version != __version__:
        print(FAIL + \
            '\nThis project is designed for git-deploy version %s. Please ' \
            'checkout the %s version branch before executing git-deploy or ' \
            'use git-deploy wrapper for automated version management\n' \
             % (gitdeploy_version, gitdeploy_version) \
            + ENDC)
        sys.exit(0)
    if COMMON_CONFIG['type'] == 'repository':
        deploy_repository_only(env, verbose)
        return
    if playbook is not None:
        print('\nExecuting playbook: %s' % playbook)
        if playbook not in SUPPORTED_PLAYBOOKS:
            sys.exit("Unsupported playbook: %s. Options are: %s" % (
                playbook, ', '.join(SUPPORTED_PLAYBOOKS)))
        ansible_playbook(
            env, playbook, verbose, project_virtualenv=project_virtualenv)
    else:
        sync_local_repository(env, verbose)
        deploy_repository(env, verbose)
        deploy_application(env, verbose)
        deploy_static(env, verbose, project_virtualenv)
        deploy_web(env, verbose)
    print('\nDone')


if __name__=='__main__':
    verbose = False
    project_virtualenv = os.environ['VIRTUAL_ENV']
    playbook = None
    try:
        env = sys.argv[1]
    except IndexError:
        usage()
        sys.exit(0)
    if env not in SUPPORTED_ENVIRONMENTS:
        usage()
        sys.exit(0)
    _args = []
    for arg in sys.argv[2:]:
        if arg == '--verbose':
            verbose = True
        if arg.startswith('--project-virtualenv'):
            project_virtualenv = arg.split('=')[1]
        if arg.startswith('--playbook'):
            playbook = arg.split('=')[1]
    deploy(env, verbose=verbose, playbook=playbook,
        project_virtualenv=project_virtualenv)
