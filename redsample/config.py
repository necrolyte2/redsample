import os.path
import yaml


DEFAULT_PATH = 'redsample.config.default'

def load_config(configpath):
    '''
    Load yaml config from a path

    :param str configpath: Path to config
    :return: yaml dictionary
    '''
    return yaml.load(open(configpath))

def get_user_config_path():
    return os.path.join(os.path.expanduser('~/'), '.redsample.config')

def load_user_config():
    '''
    Loads config from user home directory

    :return: yaml dict
    '''
    return load_config(get_user_config_path())

def load_default():
    path = get_user_config_path() or DEFAULT_PATH
    return load_config(path)

