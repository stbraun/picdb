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

from .config import get_configuration
from .model import PictureReference, PictureSeries, Tag


db_name = None


def get_db():
    """Get connected persistence instance."""
    db = get_configuration('database')
    return Persistence(db)


class Persistence:
    """SQLite implementation of MonitorDB API."""

    def __init__(self, db: str):
        """Initialize persistence mechanism.

        :param db: path to database.
        :type db: str
        """
        global db_name
        self.logger = logging.getLogger('picdb.db')
        self.determine_db_name(db)
        if not os.path.exists(self.db_name):
            self.conn = sqlite3.connect(self.db_name)
            self.setup_db()
        else:
            self.conn = sqlite3.connect(self.db_name)

    def determine_db_name(self, db):
        global db_name
        if db_name is None:
            self.db_name = os.path.expanduser(db)
            self.logger.info('DB name: {}'.format(self.db_name))
            db_name = self.db_name
        else:
            self.db_name = db_name

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
        :type name: PictureSeries
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
        :type name: Tag
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
        :type name: PictureReference
        """
        self.logger.debug("Add picture to DB: {} ({})".format(picture.name,
                                                             picture.path))
        stmt = '''INSERT INTO pictures VALUES (?, ?, ?, ?)'''
        self.execute_sql(stmt, (None, picture.name,
                                picture.path, picture.description))

    def update_picture(self, picture: PictureReference):
        cursor = self.conn.cursor()
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
        self.execute_sql(stmt, (picture.id, series.id))

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
        return PictureReference(key_, name, path, description)

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
        return PictureReference(key, name, path_, description)

    def retrieve_pictures_by_path_segment(self, path: str, limit=50):
        """Retrieve picture by path segment using wildcards.

        Example: Path: '%jpg'

        :param path: the path to the picture
        :type path: str
        :param limit: maximum number of records to retrieve
        :type limit: int
        :return: picture.
        :rtype: list(PictureReference)
        """
        stmt = 'SELECT id, identifier, path, description ' \
               'FROM pictures WHERE "path"like? LIMIT ?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (path, limit))
        records = [PictureReference(key, name, path_, description)
                   for (key, name, path_, description) in
                   cursor.fetchall()]
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
               'FROM tags WHERE id in (SELECT tag ' \
               'FROM picture2tag WHERE picture=?)'
        cursor.execute(stmt, (picture.key,))
        records = [Tag(key, name, description)
                   for (key, name, description) in cursor.fetchall()]
        return list(records)

    def retrieve_series_for_picture(self, picture: PictureReference):
        """Retrieve all series for given picture.

        :param picture: the id of the picture
        :return: series.
        :rtype: [PictureSeries]
        """
        cursor = self.conn.cursor()
        stmt = 'SELECT id, identifier, description FROM series ' \
               'WHERE id in (SELECT ' \
               'tag from picture2series WHERE picture=?)'
        cursor.execute(stmt, (picture.key,))
        records = [PictureSeries(key, name, description)
                   for (key, name, description) in cursor.fetchall()]
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
        :rtype: list(Tag)
        """
        stmt = 'SELECT id, identifier, description ' \
               'FROM series WHERE "identifier"like? LIMIT ?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (name, limit))
        records = [Tag(key, name_, description)
                   for (key, name_, description) in cursor.fetchall()]
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
        :rtype: list(Tag)
        """
        stmt = 'SELECT id, identifier, description ' \
               'FROM tags WHERE "identifier"like? LIMIT ?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (name, limit))
        records = [Tag(key, name_, description)
                   for (key, name_, description) in cursor.fetchall()]
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
        :rtype: list(PictureSeries)
        """
        cursor = self.conn.cursor()
        stmt = 'SELECT id, identifier, description FROM series'
        cursor.execute(stmt)
        records = [PictureSeries(key, name, description)
                   for (key, name, description) in
                   cursor.fetchall()]
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


def add_series(series: PictureSeries):
    db = get_db()
    db.add_series(series)


def get_all_series():
    db = get_db()
    return db.retrieve_all_series()


def retrieve_series_by_key(key: int):
    db = get_db()
    return db.retrieve_series_by_key(key)


def retrieve_series_by_name_segment(name: str, limit):
    db = get_db()
    return db.retrieve_series_by_name_segment(name, limit)


def update_series(series: PictureSeries):
    db = get_db()
    db.update_series(series)


def add_tag(tag: Tag):
    db = get_db()
    db.add_tag(tag)


def get_all_tags():
    db = get_db()
    return db.retrieve_all_tags()


def retrieve_tag_by_key(key: int):
    db = get_db()
    return db.retrieve_tag_by_key(key)


def retrieve_tags_by_name_segment(name: str, limit):
    db = get_db()
    return db.retrieve_tags_by_name_segment(name, limit)


def update_tag(tag: Tag):
    db = get_db()
    db.update_tag(tag)
