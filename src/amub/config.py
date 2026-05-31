import yaml
from pathlib import Path

class AMUBConfig:
    def __init__(self, config_dict):
        self._raw = config_dict
        for k, v in config_dict.items():
            setattr(self, k, v)

    def __getitem__(self, key):
        return self._raw[key]

    def __contains__(self, key):
        return key in self._raw

    def get(self, key, default=None):
        return self._raw.get(key, default)

    def to_dict(self):
        return self._raw

def load_config(path: str) -> AMUBConfig:
    """
    Load and parse a YAML configuration file.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    
    with open(path_obj, "r") as f:
        config_dict = yaml.safe_load(f)
        
    return AMUBConfig(config_dict)
