#!/usr/bin/env python
"""
git subcommand to remotely deploy projects.

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


def get_vault_dir():
    return os.environ.get('GIT_DEPLOY_VAULT_DIR',
        os.path.join(ASSETS_DIR, 'vault'))


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


def get_common_config():
    fn = os.path.join(get_config_dir(), 'config.common.yml')
    with open(fn) as f:
        cfg = yaml.safe_load(f)
    return cfg
COMMON_CONFIG = get_common_config()


def ansible_playbook(env, playbook, *ansible_args, **kwargs):
    command = 'ansible-playbook'
    for a in ansible_args:
        command += f' {a}'
    command += ' -e env=%s' % env
    #command += ' -e project_root=%s' % get_project_path()
    command += ' -e config_dir=%s' % get_config_dir()
    command += ' -e vault_dir=%s' % get_vault_dir()
    for k,v in kwargs.items():
        command += ' -e %s=%s' % (k,v)
    command += ' %s' % playbook
    call(command)


def playbook_path(name):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ansible')
    return os.path.join(path, name)


def builtin_playbook(env, playbook_name, *ansible_args):
    playbook = playbook_path(playbook_name)
    ansible_playbook(env, playbook, *ansible_args)


def deploy(env, version, *ansible_args):
    gitdeploy_version = COMMON_CONFIG.get('gitdeploy_version')
    if gitdeploy_version and gitdeploy_version != __version__:
        print(FAIL + \
            '\nThis project is designed for git-deploy version %s. Please ' \
            'checkout the %s version branch of git-deploy before executing.' % (
            gitdeploy_version, gitdeploy_version) + ENDC)
        sys.exit(0)
    if COMMON_CONFIG['type'] == 'repository':
        builtin_playbook(env, 'deploy.repository.yml', *ansible_args)
        return
    elif COMMON_CONFIG['type'] == 'static':
        builtin_playbook(env, 'deploy.repository.yml', *ansible_args)
        builtin_playbook(env, 'deploy.static.yml', *ansible_args)
        return
    builtin_playbook(env, 'deploy.repository.yml', *ansible_args)
    if COMMON_CONFIG.get('docker_compose_file'):
        builtin_playbook(env, 'build.containers.yml', *ansible_args)
        builtin_playbook(env, 'deploy.web.yml', *ansible_args)
    else:
        print('No containers to build. Deploying legacy application ...')
        builtin_playbook(env, 'deploy.python.yml', *ansible_args)
        builtin_playbook(env, 'deploy.static.yml', *ansible_args)
        builtin_playbook(env, 'deploy.web.yml', *ansible_args)
    print('\nDone')


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
@click.option('-p', '--playbook', required=False,
    help='Specify a playbook to run rather than a project deployment.')
def cli(ctx, env, project_version, playbook):
    """Deploy to environment ENV, PROJECT_VERSION of the current project repository.

    ENV: A configuration evironment with hosts configured in the ansible inventory.

    PROJECT_VERSION: Either HEAD, or a branch or tag name.

    ** Note: Additional arguments are passed (without validation) to Ansible.
    """
    ansible_args = ctx.args 
    ansible_args.extend(['-e', f'project_version={project_version}'])
    print('Passing arguments to ansible commands: %s\n' % ' '.join(ansible_args))
    if playbook is not None:
        ansible_playbook(env, playbook, *ansible_args)
    else:
        deploy(env, project_version, *ansible_args)
