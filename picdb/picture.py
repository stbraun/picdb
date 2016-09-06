# coding=utf-8
"""
An entity for pictures.
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

from . import persistence
from .entity import Entity


class PictureReference(Entity):
    """A reference to an image on the file system."""

    def __init__(self, key, name, path, description=""):
        super().__init__(key, name, description)
        self.path = path
        self._tags = []
        self._groups = []

    def save(self):
        if self.key is None:
            persistence.add_picture(self)
        else:
            persistence.update_picture(self)

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, tags_):
        self._tags = tags_

    @property
    def groups(self):
        return self._groups

    @groups.setter
    def groups(self, groups_):
        self._groups = groups_

    def __str__(self):
        return '<{} ({}): {}>'.format(self.name, self.key, self.path)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.path == other.path

    def __lt__(self, other):
        return self.path < other.path

    def __hash__(self):
        return hash(self.path)
