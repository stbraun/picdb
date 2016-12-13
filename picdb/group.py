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
from .cache import LRUCache
from .persistence import get_db, UnknownEntityException
from .entity import Entity
from .pictureservices import get_picture_from_d_object

_group_cache = LRUCache(2000)


class Group(Entity):
    """A series of pictures."""

    def __init__(self, key, name, description, parent=None):
        super().__init__(key, name, description)
        self._parent = parent
        self._children = []
        # Currently assigned pictures. May not be saved yet.
        self._pictures = None

    @property
    def pictures(self):
        """Get pictures assigned to this group."""
        if self._pictures is None:
            self._pictures = retrieve_pictures_for_group(self)
        return self._pictures

    @pictures.setter
    def pictures(self, pictures_):
        """Replace the complete picture set of this group.

        :param pictures_: complete set of pictures to assign to the group.
        :type pictures_: [Picture]
        """
        self._pictures = pictures_

    @property
    def parent(self):
        """Get parent."""
        if self._parent is None:
            return None
        return retrieve_series_by_key(self._parent)

    @parent.setter
    def parent(self, parent_):
        """Set parent."""
        if parent_ is None:
            self._parent = None
        else:
            self._parent = parent_.key

    def assign_picture(self, picture_):
        """Assign a single picture to the group.

        You must save the group to persist this assignment.

        :param picture_: picture to remove
        :type picture_: Picture
        """
        if self._pictures is None:
            self._pictures = self.pictures
        self._pictures.append(picture_)

    def remove_picture(self, picture_):
        """Remove given picture from group.

        If the tag was not assigned, this operation is ignored.
        You must save the group to persist this assignment.

        :param picture_: picture to remove
        :type picture_: Picture
        """
        if self._pictures is None:
            self._pictures = self.pictures
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


def retrieve_series_by_key(key):
    """Retrieve group by its key."""
    global _group_cache
    try:
        group = _group_cache.get(key)
    except KeyError:
        db = get_db()
        d_group = db.retrieve_series_by_key(key)
        if d_group is None:
            raise UnknownEntityException(
                'Series with key {} is unknown.'.format(key))
        group = get_group_from_d_object(d_group)
    return group


def retrieve_pictures_for_group(group):
    """Retrieve pictures for given group.

    :param group: given group.
    :type group: DGroup
    :return: assigned pictures
    :rtype: [Picture]
    """
    db = get_db()
    d_pictures = db.retrieve_pictures_for_group(group)
    pics = [get_picture_from_d_object(d_pic) for d_pic in d_pictures]
    return pics


def get_group_from_d_object(group_):
    """Create group or retrieve from group cache.

    :param group_: data object of group
    :type group_: DGroup
    :return: group object
    :rtype: Group
    """
    group = None
    try:
        group = _group_cache.get(group_.key)
    except KeyError:
        group = Group(*group_)
        _group_cache.put(group.key, group)
    finally:
        return group
