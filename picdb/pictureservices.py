# coding=utf-8
"""
Service functions for pictures.
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

from .persistence import get_db


def save_picture(picture):
    """Save given picture to database.

    Takes care for assigned tags.
    """
    if picture.key is None:
        _add_picture(picture)
    else:
        _update_picture(picture)
        _update_tags(picture)


def _update_tags(picture):
    """Remove and add tags according to changes made during editing."""
    saved_tags = set(retrieve_tags_for_picture(picture))
    _tags = set(picture.tags)
    tags_to_add = _tags.difference(saved_tags)
    tags_to_remove = saved_tags.difference(_tags)
    add_tags_to_picture(picture, tags_to_add)
    remove_tags_from_picture(picture, tags_to_remove)


def _add_picture(picture):
    database = get_db()
    database.add_picture(picture)


def _update_picture(picture):
    database = get_db()
    database.update_picture(picture)


def delete_picture(picture):
    """Delete picture and tag assignments.

    :param picture: picture to delete
    :type picture: Picture
    """
    database = get_db()
    database.delete_picture(picture)


def retrieve_picture_by_key(key):
    """Retrieve picture.

    :param key: key of picture
    :type key: int
    :return: picture object
    :rtype: Picture
    """
    database = get_db()
    picture = database.retrieve_picture_by_key(key)
    return picture


def retrieve_picture_by_path(path):
    """Retrieve picture.

    :param path: path to picture
    :type path: str
    :return: picture object
    :rtype: Picture
    """
    database = get_db()
    picture = database.retrieve_picture_by_path(path)
    return picture


def retrieve_filtered_pictures(path, limit, groups, tags):
    """Retrieve pictures applying filter.

    :param path: path to picture, may include SQL wildcards
    :type path: str
    :param limit: maximum number of records.
    :type limit: int
    :param groups: groups the pictures shall be assigned to.
    :type groups: [Group]
    :param tags: tags which shall be assigned to the pictures.
    :type tags: [Tag]
    :return: pictures matching given criteria.
    :rtype: [Picture]
    """
    database = get_db()
    pictures = database.retrieve_filtered_pictures(path, limit, groups, tags)
    return pictures


def add_tag_to_picture(picture, tag):
    """Tag oicture."""
    database = get_db()
    database.add_tag_to_picture(picture, tag)


def add_tags_to_picture(picture, tags):
    """Add set of tags to picture."""
    for tag in tags:
        add_tag_to_picture(picture, tag)


def remove_tag_from_picture(picture, tag):
    """Remove given tag from picture."""
    database = get_db()
    database.remove_tag_from_picture(picture, tag)


def remove_tags_from_picture(picture, tags):
    """Remove given tags from picture."""
    for tag in tags:
        remove_tag_from_picture(picture, tag)


def retrieve_tags_for_picture(picture):
    """Retrieve all tags for picture."""
    database = get_db()
    return database.retrieve_tags_for_picture(picture)


def retrieve_pictures_by_tag(tag_):
    """Retrieve all pictures for given tag."""
    database = get_db()
    return database.retrieve_pictures_by_tag(tag_)


def number_of_pictures():
    """Provide number of pictures currently in database."""
    database = get_db()
    return database.number_of_pictures()
