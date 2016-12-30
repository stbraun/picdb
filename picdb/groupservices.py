# coding=utf-8
"""
Service functions for groups.
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
from .group import Group


def save_group(group_):
    if group_.key is None:
        __add_group(group_)
    else:
        update_group(group_)
        __update_pictures(group_)


def __add_group(group_):
    db = get_db()
    db.add_group(group_)


def __update_pictures(group_):
    """Remove and add pictures according to changes made during editing."""
    if group_.pictures is not None:
        saved_pics = set(retrieve_pictures_for_group(group_))
        _pictures = set(group_.pictures)
        pictures_to_add = _pictures.difference(saved_pics)
        pictures_to_remove = saved_pics.difference(_pictures)
        add_pictures_to_group(group_, pictures_to_add)
        remove_pictures_from_group(group_, pictures_to_remove)


def update_group(group):
    db = get_db()
    db.update_group(group)


def delete_group(group_):
    db = get_db()
    db.delete_group(group_)


def get_all_series():
    db = get_db()
    groups = db.retrieve_all_groups()
    return groups


def retrieve_series_by_key(key):
    db = get_db()
    group = db.retrieve_group_by_key(key)
    if group is None:
        raise UnknownEntityException(
            'Series with key {} is unknown.'.format(key))
    return group


def retrieve_series_by_name(name):
    db = get_db()
    group = db.retrieve_group_by_name(name)
    if group is None:
        raise UnknownEntityException(
            'Series with name {} is unknown.'.format(name))
    return group


def retrieve_series_by_name_segment(name, limit):
    db = get_db()
    return db.retrieve_groups_by_name_segment(name)


def retrieve_pictures_for_group(group):
    """Retrieve pictures for given group.

    :param group: given group.
    :type group: Group
    :return: assigned pictures
    :rtype: [Picture]
    """
    db = get_db()
    return db.retrieve_pictures_for_group(group)


def retrieve_groups_for_picture(picture):
    """Retrieve groups for given picture.

    :param picture: given group.
    :type picture: Picture
    :return: groups the picture is assigned to
    :rtype: [Group]
    """
    db = get_db()
    return db.retrieve_groups_for_picture(picture)


def add_picture_to_group(group_, picture):
    db = get_db()
    db.add_picture_to_group(picture, group_)


def add_pictures_to_group(group_, pictures_):
    """Add given set of pictures to group.

    :param group_: group to add pictures to
    :type group_: Group
    :param pictures_: pictures to add
    :type pictures_: [Picture]
    """
    for pic in pictures_:
        add_picture_to_group(group_, pic)


def add_picture_to_set_of_groups(picture, groups):
    for item in groups:
        add_picture_to_group(item, picture)


def remove_picture_from_group(group_, picture):
    db = get_db()
    db.remove_picture_from_group(picture, group_)


def remove_pictures_from_group(group_, pictures_):
    """Remove given set of pictures from group.

    :param group_: group to remove pictures from
    :type group_: Group
    :param pictures_: pictures to remove
    :type pictures_: [Picture]
    """
    for pic in pictures_:
        remove_picture_from_group(group_, pic)


def remove_picture_from_set_of_groups(picture, groups):
    for item in groups:
        remove_picture_from_group(item, picture)


def create_group(key=None, name='', description=''):
    """Create a new group instance.

    You may want to add pictures and parent to the new group.

    :param key: database key. May be None for transient group.
    :type key: int
    :param name: group name
    :param description: description of group.
    """
    grp_ = Group(key, name, description)
    return grp_


def number_of_groups():
    """Provide number of groups currently in database."""
    db = get_db()
    return db.number_of_groups()
