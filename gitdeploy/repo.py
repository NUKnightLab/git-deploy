import os, sys
from git import Repo
from git.exc import InvalidGitRepositoryError
from rich import print


def get_repository() -> Repo:
    return Repo(search_parent_directories=True)


def verify_repo(command:str) -> None:
    try:
        get_repository()
    except InvalidGitRepositoryError:
        print('[bold red]\nNot a git repository.[/bold red]\n\n' \
              f'[yellow]{command} is a git subcommand. ' \
              'Please execute within a git repository.[/yellow]')
        sys.exit()


def get_project_path() -> str:
    return get_repository().working_dir
