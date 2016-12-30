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
from .pictureservices import get_picture_from_d_object
from .group import Group

_group_cache = LRUCache(2000)


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


def delete_group(group_):
    db = get_db()
    db.delete_group(group_)


def get_all_series():
    db = get_db()
    d_groups = db.retrieve_all_series()
    groups = [create_group_from_d_object(d_grp) for d_grp in d_groups]
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
        group = create_group_from_d_object(d_group)
    return group


def retrieve_series_by_name(name):
    global _group_cache
    db = get_db()
    d_group = db.retrieve_series_by_name(name)
    if d_group is None:
        raise UnknownEntityException(
            'Series with name {} is unknown.'.format(name))
    group = create_group_from_d_object(d_group)
    return group


def retrieve_series_by_name_segment(name, limit):
    db = get_db()
    d_groups = db.retrieve_series_by_name_segment(name)
    groups = [create_group_from_d_object(d_grp) for d_grp in d_groups]
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
    groups = [create_group_from_d_object(d_grp) for d_grp in d_groups]
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


def add_picture_to_set_of_groups(picture, groups):
    for item in groups:
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


def remove_picture_from_set_of_groups(picture, groups):
    for item in groups:
        remove_picture_from_group(item, picture)


def create_group_from_d_object(d_group):
    """Create group or retrieve from group cache.

    :param d_group: data object of group
    :type d_group_: DGroup
    :return: group object
    :rtype: Group
    """
    group = None
    try:
        group = _group_cache.get(d_group.key)
    except KeyError:
        # group = Group(*d_group)
        group = create_group(d_group.key, d_group.name, d_group.description)
        if d_group.parent is not None:
            # replace key with Group instance
            parent = retrieve_series_by_key(d_group.parent)
            group.parent = parent
        group.pictures = retrieve_pictures_for_group(group)
        _group_cache.put(group.key, group)
    finally:
        return group


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
