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

from .cache import LRUCache
from .persistence import get_db
from .tagservices import get_tag_from_d_object
from .picture import Picture


_picture_cache = LRUCache(20000)


def add_picture(picture):
    db = get_db()
    db.add_picture(picture)


def delete_picture(picture):
    """Delete picture and tag assignments.

    :param picture: picture to delete
    :type picture: Picture
    """
    db = get_db()
    db.delete_picture(picture)


def retrieve_picture_by_key(key):
    """Retrieve picture.

    :param key: key of picture
    :type key: int
    :return: picture object
    :rtype: Picture
    """
    global _picture_cache
    try:
        picture = _picture_cache.get(key)
    except KeyError:
        db = get_db()
        d_pic = db.retrieve_picture_by_key(key)
        picture = Picture(*d_pic)
        _picture_cache.put(key, picture)
    return picture


def retrieve_picture_by_path(path):
    """Retrieve picture.

    :param path: path to picture
    :type path: str
    :return: picture object
    :rtype: Picture
    """
    global _picture_cache
    db = get_db()
    d_pic = db.retrieve_picture_by_path(path)
    picture = Picture(*d_pic)
    _picture_cache.put(picture.key, picture)
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
    global _picture_cache
    db = get_db()
    d_pictures = db.retrieve_filtered_pictures(path, limit, groups, tags)
    pictures = [get_picture_from_d_object(d_pic) for d_pic in d_pictures]
    for picture in pictures:
        _picture_cache.put(picture.key, picture)
    return pictures


def update_picture(picture):
    global _picture_cache
    db = get_db()
    db.update_picture(picture)
    _picture_cache.put(picture.key, picture)


def add_tag_to_picture(picture, tag):
    db = get_db()
    db.add_tag_to_picture(picture, tag)


def add_tags_to_picture(picture, tags):
    for tag in tags:
        add_tag_to_picture(picture, tag)


def remove_tag_from_picture(picture, tag):
    db = get_db()
    db.remove_tag_from_picture(picture, tag)


def remove_tags_from_picture(picture, tags):
    for tag in tags:
        remove_tag_from_picture(picture, tag)


def retrieve_tags_for_picture(picture):
    db = get_db()
    d_tags = db.retrieve_tags_for_picture(picture)
    tags = [get_tag_from_d_object(d_tag) for d_tag in d_tags]
    return tags


def retrieve_pictures_by_tag(tag_):
    db = get_db()
    d_pics = db.retrieve_pictures_by_tag(tag_)
    pics = [get_picture_from_d_object(d_pic) for d_pic in d_pics]
    return pics


def get_picture_from_d_object(picture_):
    """Create picture or retrieve from picture cache.

    :param picture_: data object of picture
    :type picture_: DPicture
    :return: picture object
    :rtype: Picture
    """
    pic = None
    try:
        pic = _picture_cache.get(picture_.key)
    except KeyError:
        pic = Picture(*picture_)
        _picture_cache.put(pic.key, pic)
    finally:
        return pic


def number_of_pictures():
    """Provide number of pictures currently in database."""
    db = get_db()
    return db.number_of_pictures()