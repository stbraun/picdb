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

logger = logging.getLogger('picdb.config')

# The configuration dictionary.
__config = None

# Search path for config file. Will default to packaged file.
config_path = ['./picdb_app.yaml', '~/.picdb_app.yaml']


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
    conf_dict = yaml.load(cfg)
    logger.info('Application configuration initialized.')
    return conf_dict


def get_configuration(key):
    """Retrieve configuration for given key."""
    logger.info('Retrieving application configuration key: <{}>'.format(key))
    global __config
    if __config is None:
        __config = __initialize_configuration()
    value = __config[key]
    logger.info(
        'Retrieved application configuration key: <{}> -> <{}>'.format(key,
                                                                       value))
    return value
