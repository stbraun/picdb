"""Logger initialization."""

import logging
import logging.config
import pkgutil
import yaml


def initialize_logger():
    """Initalize logger based on configuration.

    :return: logger
    :rtype: logging.logger
    """
    config = __read_configuration()
    logging.config.dictConfig(config)


def __read_configuration():
    """Read the logging configuration from file.

    :return: configuration dictionary
    :rtype: dict
    """
    cfg = pkgutil.get_data('picdb', 'resources/config_log.yaml')
    conf_dict = yaml.load(cfg)
    return conf_dict
