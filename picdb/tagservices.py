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


def save_tag(tag_):
    """Save given tag to database."""
    if tag_.key is None:
        add_tag(tag_)
    else:
        update_tag(tag_)


def add_tag(tag_):
    """Add given tag to database."""
    database = get_db()
    database.add_tag(tag_)


def update_tag(tag_):
    """Update given tag in database."""
    database = get_db()
    database.update_tag(tag_)


def delete_tag(tag_):
    """Delete given tag from database."""
    database = get_db()
    database.delete_tag(tag_)


def get_all_tags():
    """Get all tags from database."""
    database = get_db()
    tags = database.retrieve_all_tags()
    return tags


def retrieve_tag_by_key(key):
    """Retrieve tag by given key."""
    database = get_db()
    tag = database.retrieve_tag_by_key(key)
    if tag is None:
        raise UnknownEntityException(
            'Tag with key {} is unknown.'.format(key))
    return tag


def retrieve_tag_by_name(name):
    """Retrieve tag by given name."""
    database = get_db()
    tag = database.retrieve_tag_by_name(name)
    if tag is None:
        raise UnknownEntityException(
            'Tag with name {} is unknown.'.format(name))
    return tag


def retrieve_tags_by_name_segment(name, _):
    """Retrieve tag by given name segment."""
    database = get_db()
    tags = database.retrieve_tags_by_name_segment(name)
    return tags


def number_of_tags():
    """Provide number of tags currently in database."""
    database = get_db()
    return database.number_of_tags()
