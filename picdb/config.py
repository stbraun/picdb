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
import collections.abc
import logging
import pkgutil
import yaml

logger = logging.getLogger('picdb.config')

# The configuration dictionary.
__config = None

# Search path for config file. Will default to packaged file.
config_path = ['./picdb_app.yaml', '~/.picdb/picdb_app.yaml']


def _lookup_configuration():
    """Lookup the configuration file.

    :return: opened configuration file
    :rtype: stream
    """
    global config_path
    for pth in config_path:
        path = os.path.abspath(os.path.expanduser(pth))
        logger.debug('Checking for {}'.format(path))
        if os.path.exists(path):
            logger.info('Config file: {}'.format(path))
            return open(path)
    return pkgutil.get_data('picdb', 'resources/config_app.yaml')


def __initialize_configuration():
    """Initialize application configuration.

    :return: configuration dictionary
    :rtype: dict
    """
    logger.info('Initializing application configuration ...')
    cfg = _lookup_configuration()
    conf_dict = yaml.safe_load(cfg)
    logger.info('Application configuration initialized.')
    return conf_dict


def get_configuration(key, default=None):
    """Retrieve configuration for given key."""
    logger.info('Retrieving application configuration key: <{}>'.format(key))
    global __config
    if __config is None:
        __config = Configuration(__initialize_configuration())
    value = __config.get_value(key, default)
    logger.info(
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
        keys = key.split('.')
        try:
            v = self._conf[keys[0]]
            for key in keys[1:]:
                v = v[key]
            return v
        except KeyError as e:
            if default is None:
                raise e
            return default
