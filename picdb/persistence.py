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

from postgresql.exceptions import UniqueError
import postgresql.driver.dbapi20 as dbapi

from .config import get_configuration
from .cache import LRUCache
from .group import Group
from .picture import Picture
from .tag import Tag

_tag_cache = LRUCache(2000)
_picture_cache = LRUCache(20000)
_group_cache = LRUCache(2000)

# This module global variable will hold the Persistence instance.
_db = None


class UnknownEntityException(Exception):
    """Raised if requested entity does not exist."""
    pass


class DuplicateException(Exception):
    """Raised if duplicate objects shall be persisted."""

    def __init__(self, duplicate, caused_by=None):
        """Initialize exception.

        :param duplicate: duplicate item.
        :param caused_by: the exception causing this one.
        """
        self.duplicate = duplicate
        self.caused_by = caused_by


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

    def execute_sql(self, stmt_, *args):
        """Execute the given SQL statement with arguments."""
        try:
            stmt = self.conn.prepare(stmt_)
            stmt(*args)
            self.conn.commit()
            return True
        except UniqueError as u:
            self.conn.rollback()
            self.logger.debug('duplicate: {}'.format(stmt))
            raise u
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror(title='Database Error',
                                 message='{}'.format(e))
            return False

    # -------- group related

    def add_group(self, group):
        """Add a new group.

        :param group: the group to add
        :type group: Group
        """
        self.logger.debug("Add group to DB: {}".format(group.name))
        stmt = '''INSERT INTO groups (identifier, description, parent)
        VALUES ($1, $2, $3)'''
        parent = group.parent.key if group.parent is not None else None
        try:
            self.execute_sql(stmt, group.name, group.description, parent)
        except UniqueError as u:
            raise DuplicateException(group, u)

    def update_group(self, series):
        """Update group record."""
        self.logger.debug("Update series: {}".format(series.name))
        stmt = "UPDATE groups SET identifier=$1, description=$2, " \
               "parent=$3 " \
               "WHERE id=$4"
        self.execute_sql(stmt, series.name,
                         series.description,
                         series.parent.key if series.parent is not None else
                         None,
                         series.key)

    def delete_group(self, group_):
        """Delete group and picture assignments."""
        stmt_pics = """DELETE FROM picture2group WHERE "group"=$1"""
        stmt_grp = "DELETE FROM groups WHERE id=$1"
        self.execute_sql(stmt_pics, group_.key)
        self.execute_sql(stmt_grp, group_.key)

    def add_picture_to_group(self, picture, group_):
        """Add picture to a group.

        :param picture: the picture
        :type picture: Picture
        :param group_: the group
        :type group_: Group
        """
        self.logger.debug(
            "Adding picture {} to group_ {}.".format(picture, group_))
        stmt = '''INSERT INTO picture2group VALUES($1, $2)'''
        self.execute_sql(stmt, picture.key, group_.key)

    def remove_picture_from_group(self, picture, group):
        """Remove picture from a series.

        :param picture: the picture
        :type picture: Picture
        :param group: the group
        :type group: Group
        """
        self.logger.debug(
            "Removing picture {} from series {}.".format(picture, group))
        stmt = '''DELETE FROM picture2group WHERE picture=$1 AND "group"=$2'''
        self.execute_sql(stmt, picture.key, group.key)

    def retrieve_group_by_key(self, key):
        """Retrieve series by key.

        :param key: the id of the series
        :type key: int
        :return: group.
        :rtype: Group
        """
        if key in _group_cache:
            return _group_cache.get(key)
        self.logger.debug("retrieve_group_by_key({})".format(key))
        stmt = 'SELECT id, identifier, description, parent  ' \
               'FROM groups WHERE "id"=$1'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(key)
        if result is None:
            return None
        row = result[0]
        return self._create_group(*(list(row)))

    def retrieve_groups_by_name(self, name):
        """Retrieve groups by name.

        :param name: the name of the group
        :type name: str
        :return: groups.
        :rtype: [Group]
        """
        self.logger.debug("retrieve_groups_by_name({})".format(name))
        stmt = 'SELECT id, identifier, description, parent ' \
               'FROM groups WHERE "identifier"=$1'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(name)
        records = [self._create_group(*row) for row in result]
        return list(records)

    def retrieve_groups_by_name_segment(self, name):
        """Retrieve groups by name segment using wildcards.

        Example: name: 'a%'

        :param name: the name of the series
        :type name: str
        :return: groups.
        :rtype: [Group]
        """
        self.logger.debug("retrieve_groups_by_name_segment({})".format(name))
        stmt = 'SELECT id, identifier, description, parent ' \
               'FROM groups WHERE "identifier"LIKE $1'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(name)
        records = [self._create_group(*row) for row in result]
        return list(records)

    def retrieve_all_groups(self):
        """Get all groups from database.

        :return: groups.
        :rtype: [Group]
        """
        self.logger.debug("retrieve_all_groups()")
        stmt = 'SELECT id, identifier, description, parent FROM groups'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_()
        records = [self._create_group(*row) for row in result]
        return list(records)

    def retrieve_pictures_for_group(self, group_):
        """Retrieve pictures assigned to given group.

        :param group_: given group.
        :type group_: Group
        :return: pictures assigned to group
        :rtype: [Picture]
        """
        self.logger.debug("retrieve_pictures_for_group({})".format(group_))
        stmt = 'SELECT id, identifier, path, description FROM pictures ' \
               'WHERE id IN (SELECT ' \
               'picture FROM picture2group WHERE "group"=$1)'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(group_.key)
        records = [self._create_picture(*row) for row in result]
        return list(records)

    def retrieve_groups_for_picture(self, picture):
        """Retrieve all groups for given picture.

        :param picture: the id of the picture
        :return: groups.
        :rtype: [Group]
        """
        self.logger.debug("retrieve_groups_for_picture({})".format(picture))
        stmt = 'SELECT id, identifier, description, parent FROM groups ' \
               'WHERE id IN (SELECT ' \
               '"group" FROM picture2group WHERE picture=$1)'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(picture.key)
        records = [self._create_group(*row) for row in result]
        return list(records)

    def number_of_groups(self):
        """Provide number of groups currently in database."""
        self.logger.debug("number_of_groups()")
        stmt = 'SELECT count(*) FROM groups'
        return self.conn.query.first(stmt)

    def _create_group(self, key, identifier, description, parent_id):
        """Create a Group instance from raw database record info.

        Creates parent object if required.
        """
        try:
            return _group_cache.get(key)
        except KeyError:
            self.logger.debug(
                "_create_group({}, {}, ...)".format(key, identifier))
            if parent_id is not None:
                parent = self.retrieve_group_by_key(parent_id)
            else:
                parent = None
            group = Group(key, identifier, description, parent=parent)
            pictures = self.retrieve_pictures_for_group(group)
            group.pictures = pictures
            _group_cache.put(key, group)
            return group

    # ------ picture related

    def add_picture(self, picture):
        """Add a new picture.

        :param picture: picture to add
        :type picture: Picture
        """
        self.logger.debug("add_picture({})".format(picture))
        stmt = "INSERT INTO pictures (identifier, path, description) VALUES " \
               "($1, $2, $3)"
        try:
            self.execute_sql(stmt, picture.name,
                             picture.path, picture.description)
        except UniqueError as u:
            raise DuplicateException(picture, u)

    def update_picture(self, picture):
        """Update picture record."""
        self.logger.debug("update_picture({})".format(picture))
        stmt = "UPDATE pictures SET identifier=$1, path=$2, " \
               "description=$3 WHERE id=$4"
        self.execute_sql(stmt, picture.name,
                         picture.path,
                         picture.description,
                         picture.key)

    def delete_picture(self, picture):
        """Delete given picture. Does also remove tag assignments."""
        self.logger.debug("delete_picture({})".format(picture))
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
            "add_tag_to_picture({!r}, {!r})".format(picture, tag))
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
            "remove_tag_from_picture({!r}, {!r})".format(picture, tag))
        stmt = '''DELETE FROM picture2tag WHERE picture=$1 AND tag=$2'''
        self.execute_sql(stmt, picture.key, tag.key)

    def retrieve_picture_by_key(self, key):
        """Retrieve picture by key.

        :param key: the id of the picture
        :type key: int
        :return: picture.
        :rtype: Picture
        """
        if key in _picture_cache:
            return _picture_cache.get(key)
        self.logger.debug("retrieve_picture_by_key({!r})".format(key))
        stmt = 'SELECT id, identifier, path, description ' \
               'FROM pictures WHERE "id"=$1'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(key)
        if result is None:
            return None
        row = result[0]
        return self._create_picture(*(list(row)))

    def retrieve_picture_by_path(self, path):
        """Retrieve picture by path.

        :param path: the path to the picture
        :type path: str
        :return: picture.
        :rtype: Picture
        """
        self.logger.debug('retrieve_picture_by_path({!r})'.format(path))
        stmt = 'SELECT id, identifier, path, description ' \
               'FROM pictures WHERE "path"=$1'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(path)
        if result is None:
            return None
        row = result[0]
        return self._create_picture(*(list(row)))

    def retrieve_filtered_pictures(self, path, limit, groups, tags):
        """Retrieve picture by path segment using wildcards.

        Example: Path: '%jpg'

        :param path: the path to the picture
        :type path: str
        :param limit: maximum number of records to retrieve
        :type limit: int
        :param groups: limit result set based on given list of groups
        :type groups: [Group]
        :param tags: limit result set based on given list of tags
        :type tags: [Tag]
        :return: pictures matching given path.
        :rtype: [Picture]
        """
        self.logger.debug(
            "retrieve_filtered_pictures({!r}, {!r}, ...)".format(path, limit))
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
        for item in groups:
            stmt += ' INTERSECT ' + stmt_s.format(str(item.key))
        for item in tags:
            stmt += ' INTERSECT ' + stmt_t.format(str(item.key))
        if limit is not None:
            stmt += ' LIMIT {}'.format(limit)
        self.logger.debug(stmt)
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(path)
        records = [self._create_picture(*row) for row in result]
        records.sort()
        return list(records)

    def retrieve_tags_for_picture(self, picture):
        """Retrieve all tags for given picture.

        :param picture: the picture to get the tags for
        :type picture: Picture
        :return: tags.
        :rtype: [Tag]
        """
        self.logger.debug("retrieve_tags_for_picture({!r})".format(picture))
        stmt = 'SELECT id, identifier, description, parent ' \
               'FROM tags WHERE id IN (SELECT tag ' \
               'FROM picture2tag WHERE picture=$1)'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(picture.key)
        records = [self._create_tag(*row) for row in result]
        return list(records)

    def retrieve_pictures_by_tag(self, tag_):
        """Retrieve pictures which have tag assigned.

        :param tag_: pictures shall have assigned this tag
        :type tag_: Tag
        :return: pictures with tag
        :rtype: [Picture]
        """
        self.logger.debug("retrieve_pictures_by_tag({!r})".format(tag_))
        stmt = 'SELECT id, identifier, path, description FROM pictures ' \
               'WHERE id IN (SELECT ' \
               'picture FROM picture2tag WHERE tag=$1)'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(tag_.key)
        records = [self._create_picture(*row) for row in result]
        return list(records)

    def number_of_pictures(self):
        """Provide number of pictures currently in database."""
        self.logger.debug('number_of_pictures()')
        stmt = 'SELECT count(*) FROM pictures'
        return self.conn.query.first(stmt)

    def _create_picture(self, key, identifier, path, description):
        """Create a Picture instance from raw database record info.

        Creates parent object if required.
        """
        try:
            return _picture_cache.get(key)
        except KeyError:
            self.logger.debug(
                "_create_picture({!r}, {!r}, ...)".format(key, identifier))
            picture = Picture(key, identifier, path, description)
            tags = self.retrieve_tags_for_picture(picture)
            picture.tags = tags
            _picture_cache.put(key, picture)
            return picture

    # ------ tag related

    def add_tag(self, tag):
        """Add a new tag.

        :param tag: tag to add
        :type tag: Tag
        """
        self.logger.debug("add_tag({})".format(tag))
        stmt = "INSERT INTO tags(identifier, description, parent) VALUES (" \
               "$1, $2, $3)"
        parent = tag.parent.key if tag.parent is not None else None
        try:
            self.execute_sql(stmt, tag.name, tag.description, parent)
        except UniqueError as u:
            raise DuplicateException(tag, u)

    def update_tag(self, tag):
        """Update tag record."""
        self.logger.debug("update_tag({!r})".format(tag))
        stmt = "UPDATE tags SET identifier=$1, description=$2, parent=$3 " \
               "WHERE id=$4"
        self.execute_sql(stmt, tag.name,
                         tag.description,
                         tag.parent.key if tag.parent is not None
                         else None,
                         tag.key)

    def delete_tag(self, tag_):
        """Delete given tag and all its assignments."""
        self.logger.debug("delete_tag({!r})".format(tag_))
        stmt = "DELETE FROM tags WHERE id=$1"
        self.execute_sql(stmt, tag_.key)

    def number_of_tags(self):
        """Provide number of tags currently in database."""
        self.logger.debug("number_of_tags()")
        stmt = 'SELECT count(*) FROM tags'
        return self.conn.query.first(stmt)

    def retrieve_all_tags(self):
        """Get all tags from database.

        :return: tags.
        :rtype: [Tag]
        """
        self.logger.debug("retrieve_all_tags()")
        stmt = 'SELECT id, identifier, description, parent FROM tags'
        stmt_ = self.conn.prepare(stmt)
        records = [self._create_tag(*row) for row in stmt_()]
        return list(records)

    def retrieve_tag_by_name(self, name):
        """Retrieve tag by name.

        :param name: the name of the tag to retrieve
        :type name: str
        :return: tag or None if name is unknown.
        :rtype: Tag
        """
        self.logger.debug("retrieve_tag_by_name({!r})".format(name))
        stmt = 'SELECT id, identifier, description, parent ' \
               'FROM tags WHERE "identifier"=$1'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(name)
        if result is None:
            return None
        return self._create_tag(*(list(result[0])))

    def retrieve_tags_by_name_segment(self, name):
        """Retrieve tags by name segment using wildcards.

        Example: name: 'a%'

        :param name: the name of the tag
        :type name: str
        :param limit: maximum number of records to retrieve
        :type limit: int
        :return: tags.
        :rtype: [Tag]
        """
        self.logger.debug("retrieve_tags_by_name_segment({!r})".format(name))
        stmt = 'SELECT id, identifier, description, parent ' \
               'FROM tags WHERE "identifier"LIKE $1'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(name)
        records = [self._create_tag(*row) for row in result]
        return list(records)

    def retrieve_tag_by_key(self, key):
        """Retrieve tag by key.

        :param key: the id of the tag
        :type key: int
        :return: tag.
        :rtype: Tag
        """
        if key in _tag_cache:
            return _tag_cache.get(key)
        self.logger.debug("retrieve_tag_by_key({!r})".format(key))
        stmt = 'SELECT id, identifier, description, parent FROM tags WHERE ' \
               '"id"=$1'
        stmt_ = self.conn.prepare(stmt)
        result = stmt_(key)
        if result is None:
            return None
        row = result[0]
        return self._create_tag(*(list(row)))

    def _create_tag(self, key, identifier, description, parent_id):
        """Create a Tag instance from raw database record info.

        Creates parent object if required.
        """
        try:
            return _tag_cache.get(key)
        except KeyError:
            self.logger.debug(
                "_create_tag({!r}, {!r}), ...".format(key, identifier))
            if parent_id is not None:
                parent = self.retrieve_tag_by_key(parent_id)
            else:
                parent = None
            tag = Tag(key, identifier, description, parent=parent)
            _tag_cache.put(key, tag)
            return tag
