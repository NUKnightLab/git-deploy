import os
import yaml
from typing import Dict
from .repo import get_project_path


def get_config_dir() -> str:
    return os.path.join(get_project_path(),
        os.environ.get('GIT_DEPLOY_PROJECT_CONFIG_DIR', 'deploy'))


_common_config = None
def get_common_config() -> Dict:
    global _common_config
    if _common_config is None:
        fn = os.path.join(get_config_dir(), 'config.common.yml')
        with open(fn) as f:
            _common_config = yaml.safe_load(f)
    return _common_config


def get_env_config(env:str) -> Dict:
    config = get_common_config()
    fn = os.path.join(get_config_dir(), f'config.{env}.yml')
    with open(fn) as f:
        cfg = yaml.safe_load(f)
    config.update(cfg)
    return config
    
