# coding=utf-8
"""
Service functions for tags.
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
from .tag import Tag
from .tag import _tag_cache as cache

# _tag_cache = LRUCache(2000)
_tag_cache = cache


def save_tag(tag_):
    if tag_.key is None:
        add_tag(tag_)
    else:
        update_tag(tag_)


def add_tag(tag_):
    """Add given tag to database."""
    db = get_db()
    db.add_tag(tag_)


def delete_tag(tag_):
    """Delete given tag from database."""
    db = get_db()
    db.delete_tag(tag_)


def get_all_tags():
    """Get all tags from database."""
    db = get_db()
    d_tags = db.retrieve_all_tags()
    tags = [get_tag_from_d_object(d_tag) for d_tag in d_tags]
    return tags


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


def retrieve_tag_by_name(name):
    """Retrieve tag by given name."""
    global _tag_cache
    db = get_db()
    d_tag = db.retrieve_tag_by_name(name)
    if d_tag is None:
        raise UnknownEntityException(
            'Tag with name {} is unknown.'.format(name))
    tag = get_tag_from_d_object(d_tag)
    return tag


def retrieve_tags_by_name_segment(name, limit):
    """Retrieve tag by given name segment."""
    db = get_db()
    d_tags = db.retrieve_tags_by_name_segment(name)
    tags = [get_tag_from_d_object(d_tag) for d_tag in d_tags]
    return tags


def update_tag(tag_):
    """Update given tag in database."""
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


def number_of_tags():
    """Provide number of tags currently in database."""
    db = get_db()
    return db.number_of_tags()
