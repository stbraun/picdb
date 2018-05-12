"""Logger initialization."""

import os
import logging
import logging.config
import pkgutil
import yaml

# Search path for config file. Will default to packaged file.
CONFIG_PATH = ['./picdb_log.yaml', '~/.picdb/picdb_log.yaml']

# The file used for logger configuration.
_CONFIG_FILE = None


def _lookup_configuration():
    """Lookup the configuration file.

    :return: opened configuration file
    :rtype: stream
    """
    global _CONFIG_FILE
    for pth in CONFIG_PATH:
        path = os.path.abspath(os.path.expanduser(pth))
        if os.path.exists(path):
            _CONFIG_FILE = path
            return open(path)
    _CONFIG_FILE = 'resources/config_log.yaml'
    return pkgutil.get_data('picdb', 'resources/config_log.yaml')


def initialize_logger():
    """Initalize logger based on configuration.

    :return: logger
    :rtype: logging.logger
    """
    config = __read_configuration()
    logging.config.dictConfig(config)
    logger = logging.getLogger('picdb.logging')
    logger.info('Logger configuration file: {}'.format(_CONFIG_FILE))


def __read_configuration():
    """Read the logging configuration from file.

    :return: configuration dictionary
    :rtype: dict
    """
    cfg = _lookup_configuration()
    conf_dict = yaml.safe_load(cfg)
    return conf_dict
