#!/usr/bin/env python
"""
git subcommand to remotely deploy projects.

Uses Ansible for the heavy lifting of deploying branches to remote servers,
restarting appropriate services, and syncing static media to S3.
"""
import os
import sys
import yaml
from subprocess import check_output as _check_output
from subprocess import call as _call
from . import __version__
from rich import print
from dotenv import load_dotenv


PLAYBOOKS_DIR = 'playbooks'


def _sh(*args):
    return _check_output(args).decode('utf-8').strip()


def sh(command, **kwargs):
    if kwargs:
        command = command % kwargs
    return _sh(*command.split())


def get_project_path():
    return sh('git rev-parse --show-toplevel')


load_dotenv(dotenv_path=os.path.join(get_project_path(), '.env'))


def get_vault_dir():
    return os.environ.get('GIT_DEPLOY_VAULT_DIR')


def get_config_dir():
    return os.path.join(get_project_path(),
        os.environ.get('GIT_DEPLOY_PROJECT_CONFIG_DIR', 'deploy'))


def call(command, **kwargs):
    if kwargs:
        command = command % kwargs
    print(f'[bold yellow underline]Executing[/bold yellow underline][yellow]: {command}')
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
    command += f' -e env={env}'
    #command += ' -e project_root=%s' % get_project_path()
    command += ' -e config_dir=%s' % get_config_dir()
    command += ' -e vault_dir=%s' % get_vault_dir()
    for k,v in kwargs.items():
        command += f' -e {k}={v}'
    command += f' {playbook}'
    call(command)


def ansible_vault(env, command):
    project_name = COMMON_CONFIG['project_name']
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
    gitdeploy_version = COMMON_CONFIG.get('gitdeploy_version')
    if gitdeploy_version and gitdeploy_version != __version__:
        print('[bold red]' \
            '\nThis project is designed for git-deploy version %s. Please ' \
            'checkout the %s version branch of git-deploy before executing.' % (
            gitdeploy_version, gitdeploy_version))
        sys.exit()
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
        builtin_playbook(env, 'deploy.python.yml', *ansible_args)
        builtin_playbook(env, 'deploy.static.yml', *ansible_args)
        builtin_playbook(env, 'deploy.web.yml', *ansible_args)
    print('\n[green]Done')


import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup


class DefaultCommandGroup(click.Group):
    """Group with default command. From: https://stackoverflow.com/a/52069546
    """
    def command(self, *args, **kwargs):
        default_command = kwargs.pop('default_command', False)
        if default_command and not args:
            kwargs['name'] = kwargs.get('name', '<>')
        decorator = super(
            DefaultCommandGroup, self).command(*args, **kwargs)
        if default_command:
            def new_decorator(f):
                cmd = decorator(f)
                self.default_command = cmd.name
                return cmd
            return new_decorator
        return decorator

    def resolve_command(self, ctx, args):
        try:
            return super(
                DefaultCommandGroup, self).resolve_command(ctx, args)
        except click.UsageError:
            args.insert(0, self.default_command)
            return super(
                DefaultCommandGroup, self).resolve_command(ctx, args)


context_settings = {
    'ignore_unknown_options': True,
    'allow_extra_args': True
}

@click.group(cls=DefaultCommandGroup)
@click.version_option()
@click.pass_context
def cli(ctx):
    pass


@cli.command(default_command=True, context_settings=context_settings)
@click.pass_context
@click.argument('env')
@click.argument('project-version')
@click.option('-p', '--playbook', required=False,
    help='Specify a playbook to run rather than a project deployment.')
def default(ctx, env, project_version, playbook):
    """Deploy to environment ENV, PROJECT_VERSION of the current project repository.

    ENV: A configuration evironment with hosts configured in the ansible inventory.

    PROJECT_VERSION: Either HEAD, or a branch or tag name.

    ** Note: Additional arguments are passed (without validation) to Ansible.
    """
    ansible_args = ctx.args 
    ansible_args.extend(['-e', f'project_version={project_version}'])
    print('[blue]Passing arguments to ansible commands:[/blue] %s\n' % ' '.join(ansible_args))
    if playbook is not None:
        ansible_playbook(env, playbook, *ansible_args)
    else:
        deploy(env, project_version, *ansible_args)


@cli.command()
@click.pass_context
@click.argument('command')
@click.argument('env')
def vault(ctx, command, env):
    """Invoke an ansible-vault command on the env-specific vault file for this
    project.

    COMMAND: ansible-vault command (create|decrypt|edit|view|encrypt|rekey)

    ENV: A configuration evironment with hosts configured in the ansible inventory.
    """
    ansible_vault(env, command)
