from enum import Enum
from pathlib import Path
from .config import get_config_dir
from .repo import get_repository

CUSTOM_PLAYBOOKS = list(Path(get_config_dir()).glob('playbook.*.yml'))

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


Playbooks = Enum('Playbooks', {
    f.name:f.name for f in CUSTOM_PLAYBOOKS })
