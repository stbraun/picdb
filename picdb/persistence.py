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
from .dataobjects import DTag, DPicture, DGroup

# This module global variable will hold the expanded database name
_db_name = None


class UnknownEntityException(Exception):
    pass


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

    def __init__(self, db):
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
                           'description TEXT,'
                           'parent INTEGER REFERENCES "series" ("id"))')
            cursor.execute('CREATE TABLE tags ( '
                           'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                           'identifier TEXT UNIQUE, '
                           'description TEXT,'
                           'parent INTEGER REFERENCES "tags" ("id"))')
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

    def add_series(self, series):
        """Add a new series.

        :param series: the series to add
        :type series: Group
        """
        self.logger.debug("Add series to DB: {}".format(series.name))
        stmt = '''INSERT INTO series VALUES (?, ?, ?, ?)'''
        parent = series.parent.key if series.parent is not None else None
        self.execute_sql(stmt, (None, series.name, series.description, parent))

    def update_group(self, series):
        self.logger.debug("Update series: {}".format(series.name))
        stmt = "UPDATE series SET identifier='{}', description='{}', " \
               "parent='{}' " \
               "WHERE id={}".format(series.name,
                                    series.description, series.parent,
                                    series.key)
        self.execute_sql(stmt)

    def add_tag(self, tag):
        """Add a new tag.

        :param tag: tag to add
        :type tag: Tag
        """
        self.logger.debug("Add tag to DB: {}".format(tag))
        stmt = '''INSERT INTO tags VALUES (?, ?, ?, ?)'''
        parent = tag.parent.key if tag.parent is not None else None
        self.execute_sql(stmt, (None, tag.name, tag.description, parent))

    def update_tag(self, tag):
        self.logger.debug("Update tag: {}".format(tag.name))
        stmt = "UPDATE tags SET identifier='{}', description='{}', parent='{" \
               "}' " \
               "WHERE id={}".format(tag.name,
                                    tag.description, tag.parent, tag.key)
        self.execute_sql(stmt)

    def add_picture(self, picture):
        """Add a new picture.

        :param picture: picture to add
        :type picture: PictureReference
        """
        self.logger.debug("Add picture to DB: {} ({})".format(picture.name,
                                                              picture.path))
        stmt = '''INSERT INTO pictures VALUES (?, ?, ?, ?)'''
        self.execute_sql(stmt, (None, picture.name,
                                picture.path, picture.description))

    def update_picture(self, picture):
        self.conn.cursor()
        self.logger.debug("Update picture: {} ({})".format(picture.name,
                                                           picture.path))
        stmt = "UPDATE pictures SET identifier='{}', path='{}', " \
               "description='{}' WHERE id={}".format(picture.name,
                                                     picture.path,
                                                     picture.description,
                                                     picture.key)
        self.execute_sql(stmt)

    def add_tag_to_picture(self, picture, tag):
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

    def remove_tag_from_picture(self, picture, tag):
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

    def add_picture_to_series(self, picture, series):
        """Add picture to a series.

        :param picture: the picture
        :type picture: PictureReference
        :param series: the series
        :type series: Group
        """
        self.logger.debug(
            "Adding picture {} to series {}.".format(picture, series))
        stmt = '''INSERT INTO picture2series VALUES(?, ?)'''
        self.execute_sql(stmt, (picture.key, series.key))

    def remove_picture_from_series(self, picture, series):
        """Remove picture from a series.

        :param picture: the picture
        :type picture: PictureReference
        :param series: the series
        :type series: Group
        """
        self.logger.debug(
            "Removing picture {} from series {}.".format(picture, series))
        stmt = '''DELETE FROM picture2series WHERE picture=? AND series=?'''
        self.execute_sql(stmt, (picture.key, series.key))

    def retrieve_picture_by_key(self, key):
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
        return DPicture(*(list(row)))

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
        return DPicture(*(list(row)))

    def retrieve_filtered_pictures(self, path, limit, series, tags):
        """Retrieve picture by path segment using wildcards.

        Example: Path: '%jpg'

        :param path: the path to the picture
        :type path: str
        :param limit: maximum number of records to retrieve
        :type limit: int
        :param series: limit result set based on given list of series
        :type series: [Group]
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
        if limit is not None:
            stmt += ' LIMIT {}'.format(limit)
        self.logger.info(stmt)
        cursor = self.conn.cursor()
        cursor.execute(stmt, (path,))
        records = [DPicture(*row) for row in cursor.fetchall()]
        records.sort()
        return list(records)

    def retrieve_series_by_key(self, key):
        """Retrieve series by key.

        :param key: the id of the series
        :type key: int
        :return: series.
        :rtype: DGroup
        """
        stmt = 'SELECT id, identifier, description, parent FROM series WHERE ' \
               '' \
               '"id"=?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (key,))
        row = cursor.fetchone()
        if row is None:
            return None
        return DGroup(*(list(row)))

    def retrieve_tags_for_picture(self, picture):
        """Retrieve all tags for given picture.

        :param picture: the picture to get the tags for
        :type picture: PictureReference
        :return: tags.
        :rtype: [DTag]
        """
        cursor = self.conn.cursor()
        stmt = 'SELECT id, identifier, description, parent ' \
               'FROM tags WHERE id IN (SELECT tag ' \
               'FROM picture2tag WHERE picture=?)'
        cursor.execute(stmt, (picture.key,))
        records = [DTag(*row) for row in cursor.fetchall()]
        return list(records)

    def retrieve_pictures_for_group(self, group):
        """Retrieve pictures assigned to given group.

        :param group: given group.
        :type group: DGroup
        :return: pictures assigned to group
        :rtype: [DPicture]
        """
        cursor = self.conn.cursor()
        stmt = 'SELECT id, identifier, path, description FROM pictures ' \
               'WHERE id IN (SELECT ' \
               'picture FROM picture2series WHERE series=?)'
        cursor.execute(stmt, (group.key,))
        records = [DPicture(*row) for row in cursor.fetchall()]
        return list(records)

    def retrieve_series_for_picture(self, picture):
        """Retrieve all series for given picture.

        :param picture: the id of the picture
        :return: series.
        :rtype: [DGroup]
        """
        cursor = self.conn.cursor()
        stmt = 'SELECT id, identifier, description, parent FROM series ' \
               'WHERE id IN (SELECT ' \
               'series FROM picture2series WHERE picture=?)'
        cursor.execute(stmt, (picture.key,))
        records = [DGroup(*row) for row in cursor.fetchall()]
        return list(records)

    def retrieve_series_by_name(self, name):
        """Retrieve series by name.

        :param name: the name of the tag to retrieve
        :type name: str
        :return: series or None if name is unknown.
        :rtype: DGroup
        """
        stmt = 'SELECT id, identifier, description, parent ' \
               ' FROM series WHERE "identifier"=?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (name,))
        row = list(cursor.fetchone())
        return DGroup(*row)

    def retrieve_series_by_name_segment(self, name, limit=1000):
        """Retrieve series by name segment using wildcards.

        Example: name: 'a%'

        :param name: the name of the series
        :type name: str
        :param limit: maximum number of records to retrieve
        :type limit: int
        :return: groups.
        :rtype: [DGroup]
        """
        stmt = 'SELECT id, identifier, description, parent ' \
               'FROM series WHERE "identifier"LIKE? LIMIT ?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (name, limit))
        records = [DGroup(*row) for row in cursor.fetchall()]
        return list(records)

    def retrieve_all_tags(self):
        """Get all tags from database.

        :return: tags.
        :rtype: [DTag]
        """
        cursor = self.conn.cursor()
        stmt = 'SELECT id, identifier, description, parent FROM tags'
        cursor.execute(stmt)
        records = [DTag(*row) for row in cursor.fetchall()]
        return list(records)

    def retrieve_tag_by_name(self, name):
        """Retrieve tag by name.

        :param name: the name of the tag to retrieve
        :type name: str
        :return: tag or None if name is unknown.
        :rtype: Tag
        """
        stmt = 'SELECT id, identifier, description, parent ' \
               'FROM tags WHERE "identifier"=?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (name,))
        row = cursor.fetchone()
        if not row:
            return None
        return DTag(*(list(row)))

    def retrieve_tags_by_name_segment(self, name, limit=1000):
        """Retrieve tags by name segment using wildcards.

        Example: name: 'a%'

        :param name: the name of the tag
        :type name: str
        :param limit: maximum number of records to retrieve
        :type limit: int
        :return: tags.
        :rtype: [DTag]
        """
        stmt = 'SELECT id, identifier, description, parent ' \
               'FROM tags WHERE "identifier"LIKE? LIMIT ?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (name, limit))
        records = [DTag(*row) for row in cursor.fetchall()]
        return list(records)

    def retrieve_tag_by_key(self, key):
        """Retrieve tag by key.

        :param key: the id of the tag
        :type key: int
        :return: tag.
        :rtype: DTag
        """
        stmt = 'SELECT id, identifier, description, parent FROM tags WHERE ' \
               '"id"=?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (key,))
        row = cursor.fetchone()
        if row is None:
            return None
        return DTag(*(list(row)))

    def retrieve_all_series(self):
        """Get all series from database.

        :return: series.
        :rtype: [DGroup]
        """
        cursor = self.conn.cursor()
        stmt = 'SELECT id, identifier, description, parent FROM series'
        cursor.execute(stmt)
        records = [DGroup(*row) for row in cursor.fetchall()]
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
