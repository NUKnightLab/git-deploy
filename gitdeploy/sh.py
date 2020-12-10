import os
from rich import print
from subprocess import CalledProcessError, STDOUT
from subprocess import check_output as _check_output
from subprocess import call as _call


def _sh(*args):
    return _check_output(args, stderr=STDOUT).decode('utf-8').strip()


def sh(command, **kwargs):
    if kwargs:
        command = command % kwargs
    return _sh(*command.split())


def call(command, **kwargs):
    if kwargs:
        command = command % kwargs
    print(f'[bold yellow underline]Executing[/bold yellow underline][yellow]: {command}')
    return _call(command.split())
