import os
from enum import Enum
from pathlib import Path
from git import Repo
from .ansible import PLAYBOOKS_DIR, get_config_dir
from .repo import get_repository

#repo = Repo(os.getcwd())
repo = get_repository()

Environments = Enum('Environments', {
    f.name.split('.')[1]:f.name.split('.')[1]
    for f in Path(get_config_dir()).glob('config.*.yml')
    if f.name != 'config.common.yml' })


Versions = Enum('Versions',
    { x.name:x.name for x in repo.branches + repo.tags })


class SecretsCommands(str, Enum):
    create = "create"
    decrypt = "decrypt"
    edit = "edit"
    view = "view"
    encrypt = "encrypt"
    rekey = "rekey"


playbooks_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
        PLAYBOOKS_DIR)

Playbooks = Enum('Playbooks', {
    f.name:f.name for f in list(Path(playbooks_dir).glob('*.yml')) })
