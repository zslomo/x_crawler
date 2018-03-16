import yaml
from attrdict import AttrDict


def read_yaml(filepath):
    with open(filepath, encoding='utf-8') as f:
        config = yaml.load(f)
    return AttrDict(config)


def read_params():
    config = read_yaml('config.yml')
    params = config.parameters
    return params
