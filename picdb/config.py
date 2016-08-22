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


import logging
import pkgutil
import yaml

logger = logging.getLogger('picdb.config')


def __initialize_configuration():
    """Initalize application configuration.

    :return: configuration dictionary
    :rtype: dict
    """
    logger.info('Initializing application configuration ...')
    cfg = pkgutil.get_data('picdb', 'resources/config_app.yaml')
    conf_dict = yaml.load(cfg)
    logger.info('Application configuration initialized.')
    return conf_dict


def get_configuration(key):
    """Retrieve configuration for given key."""
    logger.info('Retrieving application configuration key: <{}>'.format(key))
    config = __initialize_configuration()
    value = config[key]
    logger.info('Retrieved application configuration key: <{}> -> <{}>'.format(key, value))
    return value


