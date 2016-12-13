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

from .cache import LRUCache
from .persistence import get_db, UnknownEntityException
from .picture import get_picture_from_d_object
from .group import Group

from .group import _group_cache as cache

# _group_cache = LRUCache(2000)
_group_cache = cache


def save_group(group_):
    if group_.key is None:
        add_group(group_)
    else:
        update_group(group_)
        group_.update_pictures()


def add_group(group_):
    db = get_db()
    db.add_group(group_)


def delete_group(group_):
    db = get_db()
    db.delete_group(group_)


def get_all_series():
    db = get_db()
    d_groups = db.retrieve_all_series()
    groups = [get_group_from_d_object(d_grp) for d_grp in d_groups]
    return groups


def retrieve_series_by_key(key):
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


def retrieve_series_by_name(name):
    global _group_cache
    db = get_db()
    d_group = db.retrieve_series_by_name(name)
    if d_group is None:
        raise UnknownEntityException(
            'Series with name {} is unknown.'.format(name))
    group = get_group_from_d_object(d_group)
    return group


def retrieve_series_by_name_segment(name, limit):
    db = get_db()
    d_groups = db.retrieve_series_by_name_segment(name)
    groups = [get_group_from_d_object(d_grp) for d_grp in d_groups]
    return groups


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


def retrieve_groups_for_picture(picture):
    """Retrieve groups for given picture.

    :param picture: given group.
    :type picture: Picture
    :return: groups the picture is assigned to
    :rtype: [Group]
    """
    db = get_db()
    d_groups = db.retrieve_series_for_picture(picture)
    groups = [get_group_from_d_object(d_grp) for d_grp in d_groups]
    return groups


def update_group(group):
    global _group_cache
    db = get_db()
    db.update_group(group)
    _group_cache.put(group.key, group)


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


def add_picture_to_set_of_series(picture, series):
    for item in series:
        add_picture_to_group(item, picture)


def remove_picture_from_group(group_, picture):
    db = get_db()
    db.remove_picture_from_series(picture, group_)


def remove_pictures_from_group(group_, pictures_):
    """Remove given set of pictures from group.

    :param group_: group to remove pictures from
    :type group_: Group
    :param pictures_: pictures to remove
    :type pictures_: [Picture]
    """
    for pic in pictures_:
        remove_picture_from_group(group_, pic)


def remove_picture_from_set_of_series(picture, series):
    for item in series:
        remove_picture_from_group(item, picture)


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


def number_of_groups():
    """Provide number of groups currently in database."""
    db = get_db()
    return db.number_of_groups()