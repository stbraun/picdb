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
from tkinter import messagebox

import postgresql.driver.dbapi20 as dbapi

from .config import get_configuration
from .dataobjects import DTag, DPicture, DGroup

# This module global variable will hold the Persistence instance.
_db = None


class UnknownEntityException(Exception):
    pass


class DBParameters:
    """Parameters describing database."""

    def __init__(self, db_name, db_user, db_passwd, db_port):
        self.name = db_name
        self.user = db_user
        self.passwd = db_passwd
        self.port = db_port

    @classmethod
    def from_configuration(cls):
        """Create parameter instance based on configuration."""
        name = get_configuration('db_name')
        user = get_configuration('db_user')
        passwd = get_configuration('db_passwd')
        port = get_configuration('db_port')
        return DBParameters(name, user, passwd, port)


def db_params():
    """Provide database parameters.

    :return: parameters.
    :rtype: DBParameters
    """
    if _db is None:
        return None
    return _db.db_params


def create_db(db_=None):
    """Set the database to use.

    :param db_: parameters or None to use configuration.
    :type db_: DBParameters
    :return: persistence instance.
    :rtype: Persistence
    """
    global _db
    if db_ is None:
        db_ = DBParameters.from_configuration()
    _db = Persistence(db_)


def get_db():
    """Get connected persistence instance."""
    global _db
    if _db is None:
        # use configured database.
        create_db()
    return _db


class Persistence:
    """Implementation of persistence."""

    def __init__(self, db):
        """Initialize persistence mechanism.

        :param db: database parameters.
        :type db: DBParameters
        """
        self.logger = logging.getLogger('picdb.db')
        self.db_params = db
        self.conn = None
        self.connect()

    def connect(self):
        """Connect to database."""
        self.logger.debug('connecting to database ...')
        db = self.db_params
        self.conn = dbapi.connect(user=db.user, database=db.name, port=db.port,
                                  password=db.passwd)

    def close(self):
        """Close database."""
        self.conn.close()
        self.logger.debug('database connection closed.')

    def add_group(self, group):
        """Add a new series.

        :param group: the series to add
        :type group: Group
        """
        self.logger.debug("Add group to DB: {}".format(group.name))
        stmt = '''INSERT INTO groups (identifier, description, parent)
        VALUES ($1, $2, $3)'''
        parent = group.parent.key if group.parent is not None else None
        self.execute_sql(stmt, group.name, group.description, parent)

    def update_group(self, series):
        self.logger.debug("Update series: {}".format(series.name))
        stmt = "UPDATE groups SET identifier=$1, description=$2, " \
               "parent=$3 " \
               "WHERE id=$4"
        self.execute_sql(stmt, series.name,
                         series.description,
                         series.parent.key if series.parent is not
                         None else None,
                         series.key)

    def delete_group(self, group_):
        """Delete group and picture assignments."""
        stmt_pics = """DELETE FROM picture2group WHERE "group"=$1"""
        stmt_grp = "DELETE FROM groups WHERE id=$1"
        self.execute_sql(stmt_pics, group_.key)
        self.execute_sql(stmt_grp, group_.key)

    def add_tag(self, tag):
        """Add a new tag.

        :param tag: tag to add
        :type tag: Tag
        """
        self.logger.debug("Add tag to DB: {}".format(tag))
        stmt = "INSERT INTO tags(identifier, description, parent) VALUES (" \
               "$1, $2, $3)"
        parent = tag.parent.key if tag.parent is not None else None
        self.execute_sql(stmt, tag.name, tag.description, parent)

    def update_tag(self, tag):
        self.logger.debug("Update tag: {}".format(tag.name))
        stmt = "UPDATE tags SET identifier=$1, description=$2, parent=$3 " \
               "WHERE id=$4"
        self.execute_sql(stmt, tag.name,
                         tag.description,
                         tag.parent.key if tag.parent is not None
                         else None,
                         tag.key)

    def delete_tag(self, tag_):
        """Delete given tag and all its assignments."""
        stmt = "DELETE FROM tags WHERE id=$1"
        self.execute_sql(stmt, tag_.key)

    def add_picture(self, picture):
        """Add a new picture.

        :param picture: picture to add
        :type picture: Picture
        """
        self.logger.debug("Add picture to DB: {} ({})".format(picture.name,
                                                              picture.path))
        stmt = "INSERT INTO pictures (identifier, path, description) VALUES " \
               "($1, $2, $3)"
        self.execute_sql(stmt, picture.name,
                         picture.path, picture.description)

    def update_picture(self, picture):
        self.logger.debug("Update picture: {} ({})".format(picture.name,
                                                           picture.path))
        stmt = "UPDATE pictures SET identifier=$1, path=$2, " \
               "description=$3 WHERE id=$4"
        self.execute_sql(stmt, picture.name,
                         picture.path,
                         picture.description,
                         picture.key)

    def delete_picture(self, picture):
        """Delete given picture. Does also remove tag assignments."""
        stmt_tags = "DELETE FROM picture2tag WHERE picture=$1"
        stmt_pic = "DELETE FROM pictures WHERE id=$1"
        self.execute_sql(stmt_tags, picture.key)
        self.execute_sql(stmt_pic, picture.key)

    def add_tag_to_picture(self, picture, tag):
        """Add tag to a picture.

        :param picture: the picture
        :type picture: Picture
        :param tag: the tag
        :type tag: Tag
        """
        self.logger.debug(
            "Adding tag {} to picture {}.".format(tag, picture))
        stmt = '''INSERT INTO picture2tag VALUES($1, $2)'''
        self.execute_sql(stmt, picture.key, tag.key)

    def remove_tag_from_picture(self, picture, tag):
        """Remove tag from given picture.

        :param picture: the picture
        :type picture: Picture
        :param tag: the tag
        :type tag: Tag
        """
        self.logger.debug(
            "Removing tag {} from picture {}.".format(tag, picture))
        stmt = '''DELETE FROM picture2tag WHERE picture=$1 AND tag=$2'''
        self.execute_sql(stmt, picture.key, tag.key)

    def add_picture_to_group(self, picture, group_):
        """Add picture to a group.

        :param picture: the picture
        :type picture: Picture
        :param group_: the series
        :type group_: Group
        """
        self.logger.debug(
            "Adding picture {} to group_ {}.".format(picture, group_))
        stmt = '''INSERT INTO picture2group VALUES($1, $2)'''
        self.execute_sql(stmt, picture.key, group_.key)

    def remove_picture_from_series(self, picture, series):
        """Remove picture from a series.

        :param picture: the picture
        :type picture: Picture
        :param series: the series
        :type series: Group
        """
        self.logger.debug(
            "Removing picture {} from series {}.".format(picture, series))
        stmt = '''DELETE FROM picture2group WHERE picture=$1 AND "group"=$2'''
        self.execute_sql(stmt, picture.key, series.key)

    def retrieve_picture_by_key(self, key):
        """Retrieve picture by key.

        :param key: the id of the picture
        :type key: int
        :return: picture.
        :rtype: Picture
        """
        stmt = 'SELECT id, identifier, path, description ' \
               'FROM pictures WHERE "id"=$1'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(key)
        if result is None:
            return None
        row = result[0]
        return DPicture(*(list(row)))

    def retrieve_picture_by_path(self, path):
        """Retrieve picture by path.

        :param path: the path to the picture
        :type path: str
        :return: picture.
        :rtype: Picture
        """
        stmt = 'SELECT id, identifier, path, description ' \
               'FROM pictures WHERE "path"=$1'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(path)
        if result is None:
            return None
        row = result[0]
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
        :return: pictures matching given path.
        :rtype: [Picture]
        """
        stmt_p = 'SELECT DISTINCT id, identifier, path, description ' \
                 'FROM pictures WHERE ' \
                 '"path" LIKE $1'
        stmt_s = 'SELECT DISTINCT id, identifier, path, description ' \
                 'FROM pictures, picture2group WHERE ' \
                 'pictures.id=picture2group.picture AND ' \
                 'picture2group.group={}'
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
        self.logger.debug(stmt)
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(path)
        records = [DPicture(*row) for row in result]
        records.sort()
        return list(records)

    def retrieve_series_by_key(self, key):
        """Retrieve series by key.

        :param key: the id of the series
        :type key: int
        :return: series.
        :rtype: DGroup
        """
        stmt = 'SELECT id, identifier, description, parent  ' \
               'FROM groups WHERE "id"=$1'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(key)
        if result is None:
            return None
        row = result[0]
        return DGroup(*(list(row)))

    def retrieve_tags_for_picture(self, picture):
        """Retrieve all tags for given picture.

        :param picture: the picture to get the tags for
        :type picture: Picture
        :return: tags.
        :rtype: [DTag]
        """
        stmt = 'SELECT id, identifier, description, parent ' \
               'FROM tags WHERE id IN (SELECT tag ' \
               'FROM picture2tag WHERE picture=$1)'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(picture.key)
        records = [DTag(*row) for row in result]
        return list(records)

    def retrieve_pictures_by_tag(self, tag_):
        """Retrieve pictures which have tag assigned.

        :param tag_: pictures shall have assigned this tag
        :type tag_: Tag
        :return: pictures with tag
        :rtype: [DPicture]
        """
        stmt = 'SELECT id, identifier, path, description FROM pictures ' \
               'WHERE id IN (SELECT ' \
               'picture FROM picture2tag WHERE tag=$1)'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(tag_.key)
        records = [DPicture(*row) for row in result]
        return list(records)

    def retrieve_pictures_for_group(self, group_):
        """Retrieve pictures assigned to given group.

        :param group_: given group.
        :type group_: DGroup
        :return: pictures assigned to group
        :rtype: [DPicture]
        """
        stmt = 'SELECT id, identifier, path, description FROM pictures ' \
               'WHERE id IN (SELECT ' \
               'picture FROM picture2group WHERE "group"=$1)'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(group_.key)
        records = [DPicture(*row) for row in result]
        return list(records)

    def retrieve_series_for_picture(self, picture):
        """Retrieve all series for given picture.

        :param picture: the id of the picture
        :return: series.
        :rtype: [DGroup]
        """
        stmt = 'SELECT id, identifier, description, parent FROM groups ' \
               'WHERE id IN (SELECT ' \
               '"group" FROM picture2group WHERE picture=$1)'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(picture.key)
        records = [DGroup(*row) for row in result]
        return list(records)

    def retrieve_series_by_name(self, name):
        """Retrieve series by name.

        :param name: the name of the tag to retrieve
        :type name: str
        :return: series or None if name is unknown.
        :rtype: DGroup
        """
        stmt = 'SELECT id, identifier, description, parent ' \
               ' FROM groups WHERE "identifier"=$1'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(name)
        row = list(result[0])
        return DGroup(*row)

    def retrieve_series_by_name_segment(self, name):
        """Retrieve series by name segment using wildcards.

        Example: name: 'a%'

        :param name: the name of the series
        :type name: str
        :return: groups.
        :rtype: [DGroup]
        """
        stmt = 'SELECT id, identifier, description, parent ' \
               'FROM groups WHERE "identifier"LIKE $1'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(name)
        records = [DGroup(*row) for row in result]
        return list(records)

    def retrieve_all_tags(self):
        """Get all tags from database.

        :return: tags.
        :rtype: [DTag]
        """
        stmt = 'SELECT id, identifier, description, parent FROM tags'
        stmt_ = self.conn.prepare(stmt)
        records = [DTag(*row) for row in stmt_()]
        return list(records)

    def retrieve_tag_by_name(self, name):
        """Retrieve tag by name.

        :param name: the name of the tag to retrieve
        :type name: str
        :return: tag or None if name is unknown.
        :rtype: Tag
        """
        stmt = 'SELECT id, identifier, description, parent ' \
               'FROM tags WHERE "identifier"=$1'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(name)
        if result is None:
            return None
        return DTag(*(list(result[0])))

    def retrieve_tags_by_name_segment(self, name):
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
               'FROM tags WHERE "identifier"LIKE $1'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(name)
        records = [DTag(*row) for row in result]
        return list(records)

    def retrieve_tag_by_key(self, key):
        """Retrieve tag by key.

        :param key: the id of the tag
        :type key: int
        :return: tag.
        :rtype: DTag
        """
        stmt = 'SELECT id, identifier, description, parent FROM tags WHERE ' \
               '"id"=$1'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(key)
        if result is None:
            return None
        row = result[0]
        return DTag(*(list(row)))

    def retrieve_all_series(self):
        """Get all series from database.

        :return: series.
        :rtype: [DGroup]
        """
        stmt = 'SELECT id, identifier, description, parent FROM groups'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_()
        records = [DGroup(*row) for row in result]
        return list(records)

    def number_of_pictures(self):
        """Provide number of pictures currently in database."""
        stmt = 'SELECT count(*) FROM pictures'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_()
        return result[0][0]

    def number_of_groups(self):
        """Provide number of groups currently in database."""
        stmt = 'SELECT count(*) FROM groups'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_()
        return result[0][0]

    def number_of_tags(self):
        """Provide number of tags currently in database."""
        stmt = 'SELECT count(*) FROM tags'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_()
        return result[0][0]

    def execute_sql(self, stmt_, *args):
        try:
            stmt = self.conn.prepare(stmt_)
            stmt(*args)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror(title='Database Error',
                                 message='{}'.format(e))
            return False
