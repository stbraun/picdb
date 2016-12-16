# coding=utf-8
"""
An entity for a group of pictures.
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


class Group(Entity):
    """A series of pictures."""

    def __init__(self, key, name, description, pictures=None, parent=None):
        super().__init__(key, name, description)
        self._parent = parent
        self._children = []
        # Currently assigned pictures. May not be saved yet.
        if pictures is None:
            self._pictures = []
        else:
            self._pictures = pictures

    @property
    def pictures(self):
        """Get pictures assigned to this group.

        :return: pictures assigned to group.
        :rtype: [Picture]
        """
        return self._pictures

    @pictures.setter
    def pictures(self, pictures_):
        """Replace the complete picture set of this group.

        :param pictures_: complete set of pictures to assign to the group.
        :type pictures_: [Picture]
        """
        self._pictures = pictures_

    def __iter__(self):
        """Make Group iterable."""
        return self._pictures.__iter__()

    def __len__(self):
        """Determine number of pictures assigned to group."""
        return len(self._pictures)

    @property
    def parent(self):
        """Get parent."""
        return self._parent

    @parent.setter
    def parent(self, parent_):
        """Set parent.

        :param parent_: the parent group
        :type parent_: Group
        """
        self._parent = parent_

    def assign_picture(self, picture_):
        """Assign a single picture to the group.

        You must save the group to persist this assignment.

        :param picture_: picture to remove
        :type picture_: Picture
        """
        if picture_ not in self._pictures:
            self._pictures.append(picture_)

    def remove_picture(self, picture_):
        """Remove given picture from group.

        If the tag was not assigned, this operation is ignored.
        You must save the group to persist this assignment.

        :param picture_: picture to remove
        :type picture_: Picture
        """
        if picture_ in self._pictures:
            self._pictures.remove(picture_)

    @property
    def children(self):
        """Get children."""
        return self._children

    @children.setter
    def children(self, children_):
        """Set children. Note that the given list overwrites all children of
        this group. So always add all children when using this method."""
        self._children = children_
