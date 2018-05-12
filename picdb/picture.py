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
from .entity import Entity


class Picture(Entity):
    """A reference to an image on the file system."""

    def __init__(self, key, name, path, description=""):
        super().__init__(key, name, description)
        self.path = path
        # Currently assigned tags. May not be saved yet.
        self._tags = []

    @property
    def tags(self):
        """Get pictures tags."""
        return self._tags

    @tags.setter
    def tags(self, tags_):
        """Replace the complete tag set of this picture.

        :param tags_: complete set of tags to assign to the picture.
        :type tags_: [Tag]
        """
        self._tags = tags_

    def assign_tag(self, tag_):
        """Assign a single tag to the picture.

        You must save the picture to persist this assignment.

        :param tag_: a tag to assign.
        :type tag_: Tag
        """
        if tag_ not in self._tags:
            self._tags.append(tag_)

    def remove_tag(self, tag_):
        """Remove given tag from picture.

        If the tag was not assigned, this operation is ignored.

        :param tag_: tag to remove
        :type tag_: Tag
        """
        if tag_ in self._tags:
            self._tags.remove(tag_)

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

    def __iter__(self):
        return iter(self._tags)

    def __len__(self):
        return len(self._tags)
