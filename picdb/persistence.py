# coding=utf-8
"""
Persistence.
"""
# Copyright (c) 2015 Stefan Braun
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

import logging
import os
import sqlite3
from tkinter import messagebox

from .cache import LRUCache

from .config import get_configuration
from .model import PictureReference, PictureSeries, Tag

# This module global variable will hold the expanded database name
_db_name = None

# Caches for PictureReference, PictureSeries, Tag
_tag_cache = LRUCache(200)
_series_cache = LRUCache(200)
_picture_cache = LRUCache(200)


def get_db():
    """Get connected persistence instance."""
    global _db_name
    if _db_name is None:
        db = get_configuration('database')
    else:
        db = _db_name
    return Persistence(db)


class Persistence:
    """SQLite implementation of MonitorDB API."""

    def __init__(self, db: str):
        """Initialize persistence mechanism.

        :param db: path to database.
        :type db: str
        """
        global _db_name
        self.logger = logging.getLogger('picdb.db')
        self.db_name = None
        self.determine_db_name(db)
        if not os.path.exists(self.db_name):
            self.conn = sqlite3.connect(self.db_name)
            self.setup_db()
        else:
            self.conn = sqlite3.connect(self.db_name)

    def determine_db_name(self, db):
        global _db_name
        if _db_name is None:
            self.db_name = os.path.expanduser(db)
            self.logger.info('DB name: {}'.format(self.db_name))
            _db_name = self.db_name
        else:
            self.db_name = _db_name

    def close(self):
        """Close database."""
        self.conn.close()
        self.logger.debug('database connection closed.')

    def setup_db(self):
        """Setup database schema."""
        cursor = self.conn.cursor()
        # Create tables
        try:
            cursor.execute('CREATE TABLE series ( '
                           'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                           'identifier TEXT UNIQUE, '
                           'description TEXT)')
            cursor.execute('CREATE TABLE tags ( '
                           'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                           'identifier TEXT UNIQUE, '
                           'description TEXT)')
            cursor.execute('CREATE TABLE pictures ( '
                           'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                           'identifier TEXT, '
                           'path TEXT UNIQUE, '
                           'description TEXT)')
            cursor.execute('CREATE TABLE picture2series ('
                           'picture INTEGER REFERENCES "pictures" ("id"), '
                           'series INTEGER REFERENCES "series" ("id"))')
            cursor.execute('CREATE TABLE picture2tag ('
                           'picture INTEGER REFERENCES "pictures" ("id"), '
                           'tag INTEGER REFERENCES "tags" ("id"))')
        except Exception as e:
            self.logger.warning(e)

    def add_series(self, series: PictureSeries):
        """Add a new series.

        :param series: the series to add
        :type series: PictureSeries
        """
        self.logger.debug("Add series to DB: {}".format(series.name))
        stmt = '''INSERT INTO series VALUES (?, ?, ?)'''
        self.execute_sql(stmt, (None, series.name, series.description))

    def update_series(self, series: PictureSeries):
        self.logger.debug("Update series: {}".format(series.name))
        stmt = "UPDATE series SET identifier='{}', description='{}' " \
               "WHERE id={}".format(series.name,
                                    series.description, series.key)
        self.execute_sql(stmt)

    def add_tag(self, tag: Tag):
        """Add a new tag.

        :param tag: tag to add
        :type tag: Tag
        """
        self.logger.debug("Add tag to DB: {}".format(tag))
        stmt = '''INSERT INTO tags VALUES (?, ?, ?)'''
        self.execute_sql(stmt, (None, tag.name, tag.description))

    def update_tag(self, tag: Tag):
        self.logger.debug("Update tag: {}".format(tag.name))
        stmt = "UPDATE tags SET identifier='{}', description='{}' " \
               "WHERE id={}".format(tag.name,
                                    tag.description, tag.key)
        self.execute_sql(stmt)

    def add_picture(self, picture: PictureReference):
        """Add a new picture.

        :param picture: picture to add
        :type picture: PictureReference
        """
        self.logger.debug("Add picture to DB: {} ({})".format(picture.name,
                                                              picture.path))
        stmt = '''INSERT INTO pictures VALUES (?, ?, ?, ?)'''
        self.execute_sql(stmt, (None, picture.name,
                                picture.path, picture.description))

    def update_picture(self, picture: PictureReference):
        self.conn.cursor()
        self.logger.debug("Update picture: {} ({})".format(picture.name,
                                                           picture.path))
        stmt = "UPDATE pictures SET identifier='{}', path='{}', " \
               "description='{}' WHERE id={}".format(picture.name,
                                                     picture.path,
                                                     picture.description,
                                                     picture.key)
        self.execute_sql(stmt)

    def add_tag_to_picture(self, picture: PictureReference, tag: Tag):
        """Add tag to a picture.

        :param picture: the picture
        :type picture: PictureReference
        :param tag: the tag
        :type tag: Tag
        """
        self.logger.debug(
            "Adding tag {} to picture {}.".format(tag, picture))
        stmt = '''INSERT INTO picture2tag VALUES(?, ?)'''
        self.execute_sql(stmt, (picture.key, tag.key))

    def remove_tag_from_picture(self, picture: PictureReference, tag: Tag):
        """Remove tag from given picture.

        :param picture: the picture
        :type picture: PictureReference
        :param tag: the tag
        :type tag: Tag
        """
        self.logger.debug(
            "Removing tag {} from picture {}.".format(tag, picture))
        stmt = '''DELETE FROM picture2tag WHERE picture=? AND tag=?'''
        self.execute_sql(stmt, (picture.key, tag.key))

    def add_picture_to_series(self, picture: PictureReference,
                              series: PictureSeries):
        """Add picture to a series.

        :param picture: the picture
        :type picture: PictureReference
        :param series: the series
        :type series: PictureSeries
        """
        self.logger.debug(
            "Adding picture {} to series {}.".format(picture, series))
        stmt = '''INSERT INTO picture2series VALUES(?, ?)'''
        self.execute_sql(stmt, (picture.key, series.key))

    def remove_picture_from_series(self, picture: PictureReference,
                                   series: PictureSeries):
        """Remove picture from a series.

        :param picture: the picture
        :type picture: PictureReference
        :param series: the series
        :type series: PictureSeries
        """
        self.logger.debug(
            "Removing picture {} from series {}.".format(picture, series))
        stmt = '''DELETE FROM picture2series WHERE picture=? AND series=?'''
        self.execute_sql(stmt, (picture.key, series.key))

    def retrieve_picture_by_key(self, key: int):
        """Retrieve picture by key.

        :param key: the id of the picture
        :type key: int
        :return: picture.
        :rtype: PictureReference
        """
        stmt = 'SELECT id, identifier, path, description ' \
               'FROM pictures WHERE "id"=?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (key,))
        row = cursor.fetchone()
        if row is None:
            return None
        (key_, name, path, description) = row
        return self.__create_picture(key_, name, path, description)

    def retrieve_picture_by_path(self, path):
        """Retrieve picture by path.

        :param path: the path to the picture
        :type path: str
        :return: picture.
        :rtype: PictureReference
        """
        stmt = 'SELECT id, identifier, path, description ' \
               'FROM pictures WHERE "path"=?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (path,))
        row = cursor.fetchone()
        if row is None:
            return None
        (key, name, path_, description) = row
        return self.__create_picture(key, name, path_, description)

    def retrieve_filtered_pictures(self, path: str, limit,
                                   series: [PictureSeries], tags: [Tag]):
        """Retrieve picture by path segment using wildcards.

        Example: Path: '%jpg'

        :param path: the path to the picture
        :type path: str
        :param limit: maximum number of records to retrieve
        :type limit: int
        :param series: limit result set based on given list of series
        :type series: [PictureSeries]
        :param tags: limit result set based on given list of tags
        :type tags: [Tag]
        :return: picture.
        :rtype:[PictureReference]
        """
        stmt_p = 'SELECT DISTINCT id, identifier, path, description ' \
                 'FROM pictures WHERE ' \
                 '"path" LIKE ?'
        stmt_s = 'SELECT DISTINCT id, identifier, path, description ' \
                 'FROM pictures, picture2series WHERE ' \
                 'pictures.id=picture2series.picture AND ' \
                 'picture2series.series={}'
        stmt_t = 'SELECT DISTINCT id, identifier, path, description ' \
                 'FROM pictures, picture2tag WHERE ' \
                 'pictures.id=picture2tag.picture AND picture2tag.tag={}'
        stmt = stmt_p
        for item in series:
            stmt += ' INTERSECT ' + stmt_s.format(str(item.key))
        for item in tags:
            stmt += ' INTERSECT ' + stmt_t.format(str(item.key))
        stmt += ' LIMIT ?'
        self.logger.info(stmt)
        cursor = self.conn.cursor()
        cursor.execute(stmt, (path, limit))
        records = [self.__create_picture(key, name, path_, description)
                   for (key, name, path_, description) in
                   cursor.fetchall()]
        records.sort()
        return list(records)

    def retrieve_series_by_key(self, key: int):
        """Retrieve series by key.

        :param key: the id of the series
        :type key: int
        :return: series.
        :rtype: PictureSeries
        """
        stmt = 'SELECT id, identifier, description FROM series WHERE "id"=?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (key,))
        row = cursor.fetchone()
        if row is None:
            return None
        (key_, name, description) = row
        return PictureSeries(key_, name, description)

    def retrieve_tags_for_picture(self, picture: PictureReference):
        """Retrieve all tags for given picture.

        :param picture: the picture to get the tags for
        :type picture: PictureReference
        :return: tags.
        :rtype: [Tag]
        """
        cursor = self.conn.cursor()
        stmt = 'SELECT id, identifier, description ' \
               'FROM tags WHERE id IN (SELECT tag ' \
               'FROM picture2tag WHERE picture=?)'
        cursor.execute(stmt, (picture.key,))
        records = [Tag(key, name, description)
                   for (key, name, description) in cursor.fetchall()]
        records.sort()
        return list(records)

    def retrieve_series_for_picture(self, picture: PictureReference):
        """Retrieve all series for given picture.

        :param picture: the id of the picture
        :return: series.
        :rtype: [PictureSeries]
        """
        cursor = self.conn.cursor()
        stmt = 'SELECT id, identifier, description FROM series ' \
               'WHERE id IN (SELECT ' \
               'series FROM picture2series WHERE picture=?)'
        cursor.execute(stmt, (picture.key,))
        records = [PictureSeries(key, name, description)
                   for (key, name, description) in cursor.fetchall()]
        records.sort()
        return list(records)

    def retrieve_series_by_name(self, name: str):
        """Retrieve series by name.

        :param name: the name of the tag to retrieve
        :type name: str
        :return: series or None if name is unknown.
        :rtype: PictureSeries
        """
        stmt = 'SELECT id, identifier, description ' \
               ' FROM series WHERE "identifier"=?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (name,))
        row = cursor.fetchone()
        if not row:
            return None
        (key, name, description) = row
        return PictureSeries(key, name, description)

    def retrieve_series_by_name_segment(self, name: str, limit=50):
        """Retrieve series by name segment using wildcards.

        Example: name: 'a%'

        :param name: the name of the series
        :type name: str
        :param limit: maximum number of records to retrieve
        :type limit: int
        :return: tags.
        :rtype: [Tag]
        """
        stmt = 'SELECT id, identifier, description ' \
               'FROM series WHERE "identifier"LIKE? LIMIT ?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (name, limit))
        records = [Tag(key, name_, description)
                   for (key, name_, description) in cursor.fetchall()]
        records.sort()
        return list(records)

    def retrieve_all_tags(self):
        """Get all tags from database.

        :return: tags.
        :rtype: [Tag]
        """
        cursor = self.conn.cursor()
        stmt = 'SELECT id, identifier, description FROM tags'
        cursor.execute(stmt)
        records = [Tag(key, name, description)
                   for (key, name, description) in cursor.fetchall()]
        records.sort()
        return list(records)

    def retrieve_tag_by_name(self, name: str):
        """Retrieve tag by name.

        :param name: the name of the tag to retrieve
        :type name: str
        :return: tag or None if name is unknown.
        :rtype: Tag
        """
        stmt = 'SELECT id, identifier, description ' \
               'FROM tags WHERE "identifier"=?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (name,))
        row = cursor.fetchone()
        if not row:
            return None
        (key, name, description) = row
        return Tag(key, name, description)

    def retrieve_tags_by_name_segment(self, name: str, limit=50):
        """Retrieve tags by name segment using wildcards.

        Example: name: 'a%'

        :param name: the name of the tag
        :type name: str
        :param limit: maximum number of records to retrieve
        :type limit: int
        :return: tags.
        :rtype: [Tag]
        """
        stmt = 'SELECT id, identifier, description ' \
               'FROM tags WHERE "identifier"LIKE? LIMIT ?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (name, limit))
        records = [Tag(key, name_, description)
                   for (key, name_, description) in cursor.fetchall()]
        records.sort()
        return list(records)

    def retrieve_tag_by_key(self, key: int):
        """Retrieve tag by key.

        :param key: the id of the tag
        :type key: int
        :return: tag.
        :rtype: Tag
        """
        stmt = 'SELECT id, identifier, description FROM tags WHERE "id"=?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (key,))
        row = cursor.fetchone()
        if row is None:
            return None
        (key_, name, description) = row
        return Tag(key_, name, description)

    def retrieve_all_series(self):
        """Get all series from database.

        :return: series.
        :rtype: [PictureSeries]
        """
        cursor = self.conn.cursor()
        stmt = 'SELECT id, identifier, description FROM series'
        cursor.execute(stmt)
        records = [PictureSeries(key, name, description)
                   for (key, name, description) in
                   cursor.fetchall()]
        records.sort()
        return list(records)

    def execute_sql(self, stmt, *args):
        cursor = self.conn.cursor()
        try:
            cursor.execute(stmt, *args)
            self.conn.commit()
            return True
        except sqlite3.DatabaseError as e:
            self.conn.rollback()
            messagebox.showerror(title='Database Error',
                                 message='{}'.format(e))
            return False

    def __create_picture(self, key: int, name: str,
                         path: str, description: str):
        """Create a PictureReference and retrieve tags and series."""
        picture = PictureReference(key, name, path, description)
        picture.tags = retrieve_tags_for_picture(picture)
        picture.series = retrieve_series_for_picture(picture)
        self.logger.debug('picture created: {}'.format(picture))
        return picture


# Picture

def add_picture(picture: PictureReference):
    db = get_db()
    db.add_picture(picture)


def retrieve_picture_by_key(key: int):
    global _picture_cache
    try:
        picture = _picture_cache.get(key)
    except KeyError:
        db = get_db()
        picture = db.retrieve_picture_by_key(key)
        _picture_cache.put(picture.key, picture)
    return picture


def retrieve_picture_by_path(path: str):
    global _picture_cache
    db = get_db()
    picture = db.retrieve_picture_by_path(path)
    _picture_cache.put(picture.key, picture)
    return picture


def retrieve_filtered_pictures(path: str, limit: int,
                               series: [PictureSeries], tags: [Tag]):
    global _picture_cache
    db = get_db()
    pictures = db.retrieve_filtered_pictures(path, limit, series, tags)
    for picture in pictures:
        _picture_cache.put(picture.key, picture)
    return pictures


def update_picture(picture: PictureReference):
    global _picture_cache
    db = get_db()
    db.update_picture(picture)
    _picture_cache.put(picture.key, picture)


def add_tag_to_picture(picture: PictureReference, tag: Tag):
    db = get_db()
    db.add_tag_to_picture(picture, tag)


def add_tags_to_picture(picture: PictureReference, tags: [Tag]):
    for tag in tags:
        add_tag_to_picture(picture, tag)


def remove_tag_from_picture(picture: PictureReference, tag: Tag):
    db = get_db()
    db.remove_tag_from_picture(picture, tag)


def remove_tags_from_picture(picture: PictureReference, tags: [Tag]):
    for tag in tags:
        remove_tag_from_picture(picture, tag)


def add_picture_to_series(picture: PictureReference, series: PictureSeries):
    db = get_db()
    db.add_picture_to_series(picture, series)


def add_picture_to_set_of_series(picture: PictureReference,
                                 series: [PictureSeries]):
    for item in series:
        add_picture_to_series(picture, item)


def remove_picture_from_series(picture: PictureReference,
                               series: PictureSeries):
    db = get_db()
    db.remove_picture_from_series(picture, series)


def remove_picture_from_set_of_series(picture: PictureReference,
                                      series: [PictureSeries]):
    for item in series:
        remove_picture_from_series(picture, item)


# Series

def add_series(series: PictureSeries):
    db = get_db()
    db.add_series(series)


def get_all_series():
    global _series_cache
    db = get_db()
    all_series = db.retrieve_all_series()
    for series in all_series:
        _series_cache.put(series.key, series)
    return all_series


def retrieve_series_by_key(key: int):
    global _series_cache
    try:
        series = _series_cache.get(key)
    except KeyError:
        db = get_db()
        series = db.retrieve_series_by_key(key)
        _series_cache.put(series.key, series)
    return series


def retrieve_series_by_name(name: str):
    global _series_cache
    db = get_db()
    series = db.retrieve_series_by_name(name)
    _series_cache.put(series.key, series)
    return series


def retrieve_series_by_name_segment(name: str, limit):
    global _series_cache
    db = get_db()
    filtered_series = db.retrieve_series_by_name_segment(name, limit)
    for series in filtered_series:
        _series_cache.put(series.key, series)
    return filtered_series


def retrieve_series_for_picture(picture: PictureReference):
    global _series_cache
    db = get_db()
    pic_series = db.retrieve_series_for_picture(picture)
    for series in pic_series:
        _series_cache.put(series.key, series)
    return pic_series


def update_series(series: PictureSeries):
    global _series_cache
    db = get_db()
    db.update_series(series)
    _series_cache.put(series.key, series)


# Tags

def add_tag(tag: Tag):
    db = get_db()
    db.add_tag(tag)


def get_all_tags():
    global _tag_cache
    db = get_db()
    tags = db.retrieve_all_tags()
    for tag in tags:
        _tag_cache.put(tag.key, tag)
    return tags


def retrieve_tag_by_key(key: int):
    global _tag_cache
    try:
        tag = _tag_cache.get(key)
    except KeyError:
        db = get_db()
        tag = db.retrieve_tag_by_key(key)
        _tag_cache.put(tag.key, tag)
    return tag


def retrieve_tag_by_name(name: str):
    global _tag_cache
    db = get_db()
    tag = db.retrieve_tag_by_name(name)
    _tag_cache.put(tag.key, tag)
    return tag


def retrieve_tags_by_name_segment(name: str, limit):
    global _tag_cache
    db = get_db()
    tags = db.retrieve_tags_by_name_segment(name, limit)
    for tag in tags:
        _tag_cache.put(tag.key, tag)
    return tags


def retrieve_tags_for_picture(picture: PictureReference):
    global _tag_cache
    db = get_db()
    tags = db.retrieve_tags_for_picture(picture)
    for tag in tags:
        _tag_cache.put(tag.key, tag)
    return tags


def update_tag(tag: Tag):
    global _tag_cache
    db = get_db()
    db.update_tag(tag)
    _tag_cache.put(tag.key, tag)
