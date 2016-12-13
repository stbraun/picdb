# coding=utf-8
"""
Tag entity.
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

from .persistence import get_db, UnknownEntityException
from .entity import Entity
from .cache import LRUCache

_tag_cache = LRUCache(2000)


class Tag(Entity):
    """A tag."""

    def __init__(self, key, name, description, parent=None):
        super().__init__(key, name, description)
        self.parent_ = parent
        self._children = []

    @property
    def children(self):
        """Return list of children."""
        return self._children

    @children.setter
    def children(self, children_):
        """Set a list of children. This replaces the current list,
        so be careful to set a complete list."""
        self._children = children_

    @property
    def parent(self):
        """Get the tags parent."""
        if self.parent_ is None:
            return None
        return retrieve_tag_by_key(self.parent_)

    @parent.setter
    def parent(self, parent_):
        """Set the tags parent."""
        if parent_ is None:
            self.parent_ = None
        else:
            self.parent_ = parent_.key


def retrieve_tag_by_key(key):
    """Retrieve tag by given key."""
    global _tag_cache
    try:
        tag = _tag_cache.get(key)
    except KeyError:
        db = get_db()
        d_tag = db.retrieve_tag_by_key(key)
        if d_tag is None:
            raise UnknownEntityException(
                'Tag with key {} is unknown.'.format(key))
        tag = get_tag_from_d_object(d_tag)
    return tag


def get_tag_from_d_object(d_tag):
    """Create tag or retrieve from tag cache.

    :param d_tag: data object of tag
    :type d_tag: DTag
    :return: tag object
    :rtype: Tag
    """
    tag = None
    try:
        tag = _tag_cache.get(d_tag.key)
    except KeyError:
        tag = Tag(*d_tag)
        _tag_cache.put(tag.key, tag)
    finally:
        return tag
