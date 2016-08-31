# coding=utf-8
"""
Model classes.
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


class Entity:
    """An abstract entity."""

    def __init__(self, key, name, description):
        self.key = key
        self.name = name
        self.description = description

    def __str__(self):
        return '<{} ({})>'.format(self.name, self.key)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if self.key is None or other.key is None:
            return False
        return self.key == other.key

    def __lt__(self, other):
        return self.name < other.name

    def __hash__(self):
        return self.key


class PictureSeries(Entity):
    """A series of pictures."""

    def __init__(self, key, name, description):
        super().__init__(key, name, description)


class Tag(Entity):
    """A tag."""

    def __init__(self, key, name, description):
        super().__init__(key, name, description)


class PictureReference(Entity):
    """A reference to an image on the file system."""

    def __init__(self, key, name, path, description=""):
        super().__init__(key, name, description)
        self.path = path
        self._tags = []
        self._series = []

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, tags_: [Tag]):
        self._tags = tags_

    @property
    def series(self):
        return self._series

    @series.setter
    def series(self, series_: [PictureSeries]):
        self._series = series_

    def __str__(self):
        return '<{} ({}): {}>'.format(self.name, self.key, self.path)

    def __repr__(self):
        return self.__str__()
