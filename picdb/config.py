# coding=utf-8
"""
Configuration items.

Configure the application for your needs.
"""
# Copyright (c) 2015 Stefan Braun
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and
# associated documentation files (the "Software"), to deal in the Software
# without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to
# whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE
# AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
#  LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import logging
import pkgutil
import yaml

LOGGER = logging.getLogger('picdb.config')

# The configuration dictionary.
__CONFIG = None

# Search path for config file. Will default to packaged file.
CONFIG_PATH = ['./picdb_app.yaml', '~/.picdb/picdb_app.yaml']


def _lookup_configuration():
    """Lookup the configuration file.

    :return: opened configuration file
    :rtype: stream
    """
    for pth in CONFIG_PATH:
        path = os.path.abspath(os.path.expanduser(pth))
        LOGGER.debug('Checking for {}'.format(path))
        if os.path.exists(path):
            LOGGER.info('Config file: {}'.format(path))
            return open(path)
    return pkgutil.get_data('picdb', 'resources/config_app.yaml')


def __initialize_configuration():
    """Initialize application configuration.

    :return: configuration dictionary
    :rtype: dict
    """
    LOGGER.info('Initializing application configuration ...')
    cfg = _lookup_configuration()
    conf_dict = yaml.safe_load(cfg)
    LOGGER.info('Application configuration initialized.')
    return conf_dict


def get_configuration(key, default=None):
    """Retrieve configuration for given key."""
    LOGGER.info('Retrieving application configuration key: <{}>'.format(key))
    global __CONFIG
    if __CONFIG is None:
        __CONFIG = Configuration(__initialize_configuration())
    value = __CONFIG.get_value(key, default)
    LOGGER.info(
        'Retrieved application configuration key: <{}> -> <{}>'.format(key,
                                                                       value))
    return value


class Configuration:
    """Configuration container."""

    def __init__(self, conf_dict=None):
        self._conf = conf_dict.copy() if conf_dict is not None else {}

    def get_value(self, key, default=None):
        """Retrieve a configuration based on its key.

        For nested configuration items a hierarchical key may be given,
        e.g. parent.child.

        If key is unknown the default value will be returned. If no default
        value is given a KeyError is raised.

        :param key: the key.
        :type key: str
        :param default: optional default value.
        :return: configured value for given key.
        :raises: KeyError if key is unknown and no default is given.
        """
        sub_keys = key.split('.')
        try:
            value = self._conf[sub_keys[0]]
            for child_key in sub_keys[1:]:
                value = value[child_key]
            return value
        except KeyError as err:
            if default is None:
                raise err
            return default

    def set_value(self, key, value):
        """Set the value of a configuration item. """
        self._conf[key] = value
