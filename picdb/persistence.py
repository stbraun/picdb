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
import sqlite3
import os
from config import get_configuration
from model import PictureReference, PictureSeries, Tag


def get_db():
    """Get connected persistence instance."""
    db = get_configuration('database')
    return Persistence(db)


class Persistence:
    """SQLite implementation of MonitorDB API."""

    def __init__(self, db):
        """Initialize persistence mechanism.

        :param db: path to database.
        :type db: str
        """
        self.logger = logging.getLogger('picdb.db')
        self.db_name = os.path.expanduser(db)
        self.logger.info(self.db_name)
        if not os.path.exists(self.db_name):
            self.conn = sqlite3.connect(self.db_name)
            self.setup_db()
        else:
            self.conn = sqlite3.connect(self.db_name)

    def close_connection(self):
        """Close database connection."""
        self.conn.close()
        self.logger.info('database connection closed.')

    def setup_db(self):
        """Setup database schema."""
        cursor = self.conn.cursor()
        # Create tables
        try:
            cursor.execute('''CREATE TABLE series ( id INTEGER PRIMARY KEY AUTOINCREMENT,
                              identifier TEXT,
                              description TEXT)''')
            cursor.execute('''CREATE TABLE tags (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              identifier TEXT,
                              description TEXT)''')
            cursor.execute('''CREATE TABLE pictures (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              identifier TEXT,
                              path TEXT,
                              description TEXT)''')
            cursor.execute('''CREATE TABLE picture2series (
                                picture INTEGER REFERENCES "pictures" ("id"),
                                series INTEGER REFERENCES "series" ("id"))''')
            cursor.execute('''CREATE TABLE picture2tag (
                                picture INTEGER REFERENCES "pictures" ("id"),
                                tag INTEGER REFERENCES "tags" ("id"))''')
        except Exception as e:
            self.logger.warning(e)

    def add_series(self, series):
        """Add a new series.

        :param series: the series to add
        :type name: PictureSeries
        """
        cursor = self.conn.cursor()
        self.logger.info("Add series to DB: {}".format(series.name))
        cursor.execute('''INSERT INTO series VALUES (?, ?, ?)''',
                       (None, series.name, series.description))
        self.conn.commit()

    def add_tag(self, tag):
        """Add a new tag.

        :param tag: tag to add
        :type name: Tag
        """
        cursor = self.conn.cursor()
        self.logger.info("Add tag to DB: {}".format(tag))
        cursor.execute('''INSERT INTO tags VALUES (?, ?, ?)''',
                       (None, tag.name, tag.description))
        self.conn.commit()

    def add_picture(self, picture):
        """Add a new picture.

        :param picture: picture to add
        :type name: PictureReference
        """
        cursor = self.conn.cursor()
        self.logger.info("Add picture to DB: {} ({})".format(picture.name, picture.path))
        cursor.execute('''INSERT INTO pictures VALUES (?, ?, ?, ?)''',
                       (None, picture.name, picture.path, picture.description))
        self.conn.commit()

    def close(self):
        """Close database."""
        self.conn.close()

    def add_tag_to_picture(self, picture, tag):
        """Add tag to a picture.

        :param picture: the picture
        :type picture: PictureReference
        :param tag: the tag
        :type tag: Tag
        """
        self.logger.info(
            "Adding tag {} to picture {}.".format(tag, picture))
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO picture2tag VALUES(?, ?)''',
                       (picture.key, tag.key))
        self.conn.commit()

    def add_picture_to_series(self, picture, series):
        """Add picture to a series.

        :param picture: the picture
        :type picture: PictureReference
        :param series: the series
        :type series: PictureSeries
        """
        self.logger.info(
            "Adding picture {} to series {}.".format(picture, series))
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO picture2series VALUES(?, ?)''',
                       (picture.id, series.id))
        self.conn.commit()

    def retrieve_picture_by_key(self, key):
        """Retrieve picture by key.

        :param key: the id of the picture
        :type key: int
        :return: picture.
        :rtype: PictureReference
        """
        stmt = 'SELECT id, identifier, path, description FROM pictures WHERE "id"=?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (key,))
        (keay_, name, path, description) = cursor.fetchall()
        return PictureReference(key_, name, path, description)

    def retrieve_picture_by_path(self, path):
        """Retrieve picture by path.

        :param path: the path to the picture
        :type path: str
        :return: picture.
        :rtype: PictureReference
        """
        stmt = 'SELECT id, identifier, path, description FROM pictures WHERE "path"=?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (path,))
        row = cursor.fetchone()
        if not row:
            return None
        (key, name, path_, description) = row
        return PictureReference(key, name, path_, description)

    def retrieve_tags_for_picture(self, picture):
        """Retrieve all tags for given picture.

        :param picture: the picture to get the tags for
        :type picture: PictureReference
        :return: tags.
        :rtype: [Tag]
        """
        cursor = self.conn.cursor()
        stmt = 'SELECT id, identifier, description FROM tags WHERE id in (SELECT tag from picture2tag WHERE picture=?)'
        cursor.execute(stmt, (picture.key,))
        records = [Tag(key, name, description) for (key, name, description) in cursor.fetchall()]
        return list(records)

    def retrieve_series_for_picture(self, picture_id):
        """Retrieve all series for given picture.

        :param picture_id: the id of the session
        :return: series.
        :rtype: [PictureSeries]
        """
        cursor = self.conn.cursor()
        stmt = 'SELECT id, identifier, description FROM series WHERE id in (SELECT ' \
               'tag from picture2series WHERE picture=?)'
        cursor.execute(stmt, (picture_id,))
        records = [PictureSeries(key, name, description) for (key, name, description) in
                   cursor.fetchall()]
        return list(records)

    def retrieve_all_tags(self):
        """Get all tags from database.

        :return: tags.
        :rtype: [Tag]
        """
        cursor = self.conn.cursor()
        stmt = 'SELECT id, identifier, description FROM tags'
        cursor.execute(stmt)
        records = [Tag(key, name, description) for (key, name, description) in cursor.fetchall()]
        return list(records)

    def retrieve_tag_by_name(self, name):
        """Retrieve tag by name.

        :param name: the name of the tag to retrieve
        :type name: str
        :return: tag or None if name is unknown.
        :rtype: Tag
        """
        stmt = 'SELECT id, identifier, description FROM tags WHERE "identifier"=?'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (name,))
        row = cursor.fetchone()
        if not row:
            return None
        (key, name, description) = row
        return Tag(key, name, description)


    def retrieve_all_series(self):
        """Get all series from database.

        :return: series.
        :rtype: list(PictureSeries)
        """
        cursor = self.conn.cursor()
        stmt = 'SELECT id, identifier, description FROM series'
        cursor.execute(stmt)
        records = [PictureSeries(key, name, description) for (key, name, description) in
                   cursor.fetchall()]
        return list(records)

