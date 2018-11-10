# coding=utf-8
"""
Version number.
"""
# Copyright (c) 2016 Stefan Braun
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

from os import environ

# Keys of environment variables to overwrite version number, build number,
# and release type. This can be used for building in a CI server.
VERSION_KEY = 'APP_VERSION'
"""Set version number via environment variable."""

BUILD_KEY = 'BUILD_NUMBER'
"""Set the build number via environment variable."""

RELEASE_KEY = 'RELEASE_TYPE'
"""Release type is an optional arbitrary string for providing additional
information to the current instance of a product, e.g. 'SNAPSHOT', 'debug'."""


def get_version(default_version='0.0.0'):
    """Provide version number.

    Looks for version number in environment. If none, default_version is used.
    If a build number is defined in environment it is appended to the version.

    :param default_version: used if no version found in environment.
    :type default_version: str
    :return: version string
    :rtype: str
    """
    if VERSION_KEY in environ.keys():
        version_number = environ[VERSION_KEY]
    else:
        version_number = default_version
    if BUILD_KEY in environ.keys():
        build_number = environ[BUILD_KEY]
        version_number = version_number + '.' + build_number
    if RELEASE_KEY in environ.keys():
        release_type = environ[RELEASE_KEY]
        version_number = version_number + '-' + release_type
    return version_number
