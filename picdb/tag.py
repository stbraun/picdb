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
from .cache import LRUCache
from .entity import Entity

_tag_cache = LRUCache(200)


class Tag(Entity):
    """A tag."""

    def __init__(self, key, name, description, parent=None):
        super().__init__(key, name, description)
        self.parent_ = parent
        self._children = []

    def save(self):
        if self.key is None:
            add_tag(self)
        else:
            update_tag(self)

    def delete(self):
        """Delete tag and its assignments."""
        delete_tag(self)

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, children_):
        self._children = children_

    @property
    def parent(self):
        if self.parent_ is None:
            return None
        return retrieve_tag_by_key(self.parent_)

    @parent.setter
    def parent(self, parent_):
        if parent_ is None:
            self.parent_ = None
        else:
            self.parent_ = parent_.key


def add_tag(tag_):
    db = get_db()
    db.add_tag(tag_)


def delete_tag(tag_):
    db = get_db()
    db.delete_tag(tag_)


def get_all_tags():
    db = get_db()
    d_tags = db.retrieve_all_tags()
    tags = [get_tag_from_d_object(d_tag) for d_tag in d_tags]
    return tags


def retrieve_tag_by_key(key):
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


def retrieve_tag_by_name(name):
    global _tag_cache
    db = get_db()
    d_tag = db.retrieve_tag_by_name(name)
    if d_tag is None:
        raise UnknownEntityException(
            'Tag with name {} is unknown.'.format(name))
    tag = get_tag_from_d_object(d_tag)
    return tag


def retrieve_tags_by_name_segment(name, limit):
    db = get_db()
    d_tags = db.retrieve_tags_by_name_segment(name, limit)
    tags = [get_tag_from_d_object(d_tag) for d_tag in d_tags]
    return tags


def update_tag(tag_):
    global _tag_cache
    db = get_db()
    db.update_tag(tag_)
    _tag_cache.put(tag_.key, tag_)


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
