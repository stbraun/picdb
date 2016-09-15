# coding=utf-8
"""
An entity for pictures.
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
from .entity import Entity
from .tag import get_tag_from_d_object

_picture_cache = LRUCache(200)


class Picture(Entity):
    """A reference to an image on the file system."""

    def __init__(self, key, name, path, description=""):
        super().__init__(key, name, description)
        self.path = path
        # Currently assigned tags. May not be saved yet.
        self._tags = None

    def save(self):
        if self.key is None:
            add_picture(self)
        else:
            update_picture(self)
        self._update_tags()

    def _update_tags(self):
        """Remove and add tags according to changes made during editing."""
        saved_tags = set(retrieve_tags_for_picture(self))
        _tags = set(self._tags)
        tags_to_add = _tags.difference(saved_tags)
        tags_to_remove = saved_tags.difference(_tags)
        add_tags_to_picture(self, tags_to_add)
        remove_tags_from_picture(self, tags_to_remove)

    def delete(self):
        """Delete picture from database.

        Does also remove group and tag assignments.
        """
        delete_picture(self)

    @property
    def tags(self):
        if self._tags is None:
            self._tags = retrieve_tags_for_picture(self)
        return self._tags

    @tags.setter
    def tags(self, tags_):
        """Replace the complete tag set of this picture.

        :param tags_: complete set of tags to assign to the picture.
        :type tags_: [Tag]
        """
        self._tags = tags_

    def assign_tag(self, tag_):
        """Assign a single tag to the picture.

        You must save the picture to persist this assignment.

        :param tag_: a tag to assign.
        :type tag_: Tag
        """
        if self._tags is None:
            self._tags = [tag_]
        else:
            self._tags.append(tag_)

    def remove_tag(self, tag_):
        """Remove given tag from picture.

        If the tag was not assigned, this operation is ignored.

        :param tag_: tag to remove
        :type tag_: Tag
        """
        if self._tags is not None and tag_ in self._tags:
            self._tags.remove(tag_)

    def __str__(self):
        return '<{} ({}): {}>'.format(self.name, self.key, self.path)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.path == other.path

    def __lt__(self, other):
        return self.path < other.path

    def __hash__(self):
        return hash(self.path)


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


# TODO move to service layer above entities because of dependency to Group.
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
