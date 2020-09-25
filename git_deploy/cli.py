#!/usr/bin/env python
"""
git subcommand to remotely deploy projects. Manages merging of git branches.
Uses Ansible for the heavy lifting of deploying branches to remote servers,
restarting appropriate services, and syncing static media to S3.
"""
import glob
import os
import sys
from subprocess import check_output as _check_output
from subprocess import call as _call
import yaml
from . import __version__

WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'

ASSETS_DIR = os.environ.get('GIT_DEPLOY_ASSETS_DIR',
    os.path.expanduser('~/.git-deploy-assets'))


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


#def usage():
#    print('Usage:')
#    envs = SUPPORTED_ENVIRONMENTS
#    if len(envs.keys()) > 0:
#        print('git-deploy (%s) [options]' % '|'.join(envs.keys()))
#        print('\noptions:')
#        print(' --verbose')
#    else:
#        print('No deployment environments found. ' \
#            'Please add supported_envs to your Ansible configs')


def get_common_config():
    fn = os.path.join(get_config_dir(), 'config.common.yml')
    with open(fn) as f:
        cfg = yaml.safe_load(f)
    return cfg
COMMON_CONFIG = get_common_config()
SUPPORTED_ENVIRONMENTS = COMMON_CONFIG['supported_envs']


def ansible_playbook(env, playbook, *ansible_args, **kwargs):
    # inventory is now based on ansible standards
    # https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html
    #hostfile = os.environ.get('GIT_DEPLOY_INVENTORY',
    #    os.path.join(ASSETS_DIR, 'hosts'))
    playbooks_dir = get_playbooks_dir()
    if not playbook.startswith(os.sep):
        playbook = os.path.join(playbooks_dir, playbook)
    command = 'ansible-playbook'
    #if verbose:
    #    command += ' -vvvv'
    #if hostfile:
    #    command += ' -i %s' % hostfile
    for a in ansible_args:
        command += f' {a}'
    command += ' -e env=%s' % env
    command += ' -e project_root=%s' % get_project_path()
    command += ' -e config_dir=%s' % get_config_dir()
    command += ' -e vault_dir=%s' % get_vault_dir()
    command += ' -e playbooks_dir=%s' % playbooks_dir
    for k,v in kwargs.items():
        command += ' -e %s=%s' % (k,v)
    command += ' %s' % playbook
    command += ' --vault-password-file %s' % get_vault_password_file()
    print('COMMAND:', command)
    call(command)


def sync_local_repository(env, *ansible_args):
    ansible_playbook(env, 'local.repository.yml', *ansible_args, merge_from=SUPPORTED_ENVIRONMENTS[env])


def deploy_repository(env, version, *ansible_args):
    ansible_playbook(env, 'deploy.repository.yml', *ansible_args, version=version)


def build_containers(env, *ansible_args):
    ansible_playbook(env, 'build.containers.yml', *ansible_args)


def deploy_application(env, *ansible_args):
    ansible_playbook(env, 'deploy.python.yml', *ansible_args)


def deploy_web(env, *ansible_args):
    ansible_playbook(env, 'deploy.web.yml', *ansible_args)


def deploy_static(env, project_virtualenv, *ansible_args):
    ansible_playbook(env, 'deploy.static.yml', project_virtualenv=project_virtualenv)


def deploy_extras(env, *ansible_args):
    for fn in glob.glob(os.path.join(get_config_dir(), 'playbook*.yml')):
        ansible_playbook(env, fn, *ansible_args)


SUPPORTED_PLAYBOOKS = [
    'deploy.python.yml',
    'deploy.static.yml',
    'deploy.repository.yml',
    'deploy.web.yml'
]

def deploy(env, version, *ansible_args, project_virtualenv=None, playbook=None):
    gitdeploy_version = COMMON_CONFIG.get('gitdeploy_version')
    if gitdeploy_version and gitdeploy_version != __version__:
        print(FAIL + \
            '\nThis project is designed for git-deploy version %s. Please ' \
            'checkout the %s version branch of git-deploy before executing.' % (
            gitdeploy_version, gitdeploy_version) + ENDC)
        sys.exit(0)
    if COMMON_CONFIG['type'] == 'repository':
        sync_local_repository(env, *ansible_args)
        deploy_repository(env, version, *ansible_args)
        return
    elif COMMON_CONFIG['type'] == 'static':
        sync_local_repository(env, *ansible_args)
        deploy_repository(env, version, *ansible_args)
        deploy_static(env, project_virtualenv, *ansible_args)
        return
    if playbook is not None:
        print('\nExecuting playbook: %s' % playbook)
        if playbook not in SUPPORTED_PLAYBOOKS:
            sys.exit("Unsupported playbook: %s. Options are: %s" % (
                playbook, ', '.join(SUPPORTED_PLAYBOOKS)))
        ansible_playbook(
            env, playbook, *ansible_args, project_virtualenv=project_virtualenv)
    else:
        sync_local_repository(env, *ansible_args)
        deploy_repository(env, version, *ansible_args)
        if COMMON_CONFIG.get('docker_compose_file'):
            build_containers(env, *ansible_args)
            ansible_playbook(env, 'deploy.web.1.05.yml', *ansible_args)
        else:
            print('No containers to build. Deploying legacy application ...')
            deploy_application(env, *ansible_args)
            deploy_static(env, project_virtualenv, *ansible_args)
            ansible_playbook(env, 'deploy.web.1.05.yml', *ansible_args)
    print('\nDone')


def main(env, version, *ansible_args):
    project_virtualenv = os.environ.get('VIRTUAL_ENV')
    playbook = None # TODO: support specific playbooks
    deploy(env, version, *ansible_args, playbook=playbook,
        project_virtualenv=project_virtualenv)


import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup


@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.pass_context
@click.version_option()
@click.argument('env')
@click.argument('project-version')
@click.option('-x')
def cli(ctx, env, project_version, x):
    """Deploy to deployment environment ENV, PROJECT_VERSION of the current
    project repository.

    ENV is a configuration evironment with hosts configured in the ansible inventory.

    PROJECT_VERSION is either HEAD, or a branch or tag name.
    """
    ansible_args = ctx.args 
    print('Passing arguments to ansible commands: %s\n' % ' '.join(ansible_args))
    main(env, project_version, *ansible_args)
