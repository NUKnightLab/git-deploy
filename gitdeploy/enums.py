from enum import Enum
from pathlib import Path
from typing import List, Dict
from .config import get_config_dir
from .repo import get_repository


repo = get_repository()


def get_environments() -> Dict[str,str]:
    return {
        f.name.split('.')[1]:f.name.split('.')[1]
        for f in Path(get_config_dir()).glob('config.*.yml')
        if f.name != 'config.common.yml' }

Environments = Enum('Environments', get_environments()) # type:ignore


def get_versions() -> Dict[str,str]:
    return { x.name:x.name for x in repo.branches + repo.tags }

Versions = Enum('Versions', get_versions()) # type:ignore


class SecretsCommands(str, Enum):
    create = "create"
    decrypt = "decrypt"
    edit = "edit"
    view = "view"
    encrypt = "encrypt"
    rekey = "rekey"


def get_playbooks() -> Dict[str,str]:
    return { p.name:p.name for p in
        Path(get_config_dir()).glob('playbook.*.yml') }


Playbooks = Enum('Playbooks', get_playbooks()) # type:ignore
PLAYBOOKS = [n.value for n in Playbooks]
