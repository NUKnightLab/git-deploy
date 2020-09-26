#!/usr/bin/env python
"""
git subcommand to remotely deploy projects.

Uses Ansible for the heavy lifting of deploying branches to remote servers,
restarting appropriate services, and syncing static media to S3.
"""
from rich import print
import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from .ansible import deploy, ansible_vault, ansible_playbook


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
