"""Logger initialization."""

import os
import logging
import logging.config
import pkgutil
import yaml

# Search path for config file. Will default to packaged file.
CONFIG_PATH = ['./picdb_log.yaml', '~/.picdb/picdb_log.yaml']


def _lookup_configuration():
    """Lookup the configuration file.

    :return: path to config file, opened configuration file
    :rtype: (str, stream)
    """
    for pth in CONFIG_PATH:
        path = os.path.abspath(os.path.expanduser(pth))
        if os.path.isfile(path):
            return path, open(path)
    pkg_path = 'resources/config_log.yaml'
    return pkg_path, pkgutil.get_data('picdb', pkg_path)


def initialize_logger():
    """Initialize logger based on configuration.

    :return: logger
    :rtype: logging.logger
    """
    path_cfg_file, config = __read_configuration()
    logging.config.dictConfig(config)
    logger = logging.getLogger('picdb.logging')
    logger.info('Logger configuration file: %s', path_cfg_file)


def __read_configuration():
    """Read the logging configuration from file.

    :return: path to config file, configuration dictionary
    :rtype: (str, dict)
    """
    path, cfg = _lookup_configuration()
    conf_dict = yaml.safe_load(cfg)
    return path, conf_dict
