# coding=utf-8
"""Tests for persistence."""
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

import datetime

from picdb.persistence import create_db, DBParameters, get_db
from picdb.tag import Tag
from picdb.picture import Picture
from picdb.group import Group


# Prefixes for test data
P_TAG = 'UT_T_'
P_PIC = 'UT_P_'
P_GRP = 'UT_G_'

create_db(DBParameters('pictest', 'sb', 'sb', '5432'))


class TestPersistence(object):
    """Test case for persistence."""

    def test_add_and_retrieve_by_name_tag(self):
        tag1 = self._new_tag_t()
        assert tag1 is not None

        get_db().add_tag(tag1)
        tag2 = get_db().retrieve_tag_by_name(tag1.name)

        assert tag2 is not None
        assert tag2.key is not None
        assert tag1.name == tag2.name
        assert tag1.parent == tag2.parent

    def test_update_and_retrieve_by_key_tag(self):
        tag1 = self._new_tag_p()
        tag1.description = 'new description'
        get_db().update_tag(tag1)
        tag2 = get_db().retrieve_tag_by_key(tag1.key)
        assert tag1.description == tag2.description

    def test_add_and_retrieve_picture(self):
        pic1 = self._new_pic_t()
        assert pic1 is not None

        get_db().add_picture(pic1)
        pic2 = get_db().retrieve_picture_by_path(pic1.path)

        assert pic2 is not None
        assert pic2.key is not None
        assert pic1.path == pic2.path

    def test_update_and_retrieve_by_key_picture(self):
        pic1 = self._new_pic_p()
        pic1.description = 'new text'

        get_db().update_picture(pic1)
        pic2 = get_db().retrieve_picture_by_key(pic1.key)

        assert pic2 is not None
        assert pic1.key == pic2.key
        assert pic1.path == pic2.path

    def test_add_tag_to_picture(self):
        pass

    def test_add_and_retrieve_group(self):
        group1 = self._new_grp_t()
        assert group1 is not None
        get_db().add_group(group1)
        groups = get_db().retrieve_groups_by_name(group1.name)
        assert groups is not None
        assert len(groups) > 0
        group2 = groups[0]
        assert group2.key is not None
        assert group1.name == group2.name
        assert group1.parent == group2.parent

    def test_update_group(self):
        group1 = self._new_grp_p()
        group1.description = 'new text'
        get_db().update_group(group1)
        group2 = get_db().retrieve_group_by_key(group1.key)
        assert group1.description == group2.description

    def test_add_and_retrieve_pictures_for_group(self):
        pass

    def _uq_name(self, prefix):
        """Create a unique name with given prefix."""
        dt = datetime.datetime.now()
        return '{}{}{:06d}'.format(prefix, dt.ctime(), dt.microsecond)

    def _new_tag_t(self, description='', parent=None):
        """Create new transient tag."""
        return Tag(None, self._uq_name(P_TAG), description, parent)

    def _new_pic_t(self, description=''):
        """Create new transient picture."""
        name = self._uq_name(P_PIC)
        path = '/path/' + name
        return Picture(None, name, path, description)

    def _new_grp_t(self, description='', parent=None):
        """Create new transient group."""
        return Group(None, self._uq_name(P_GRP), description, parent)

    def _new_tag_p(self, description='', parent=None):
        """Create new persistent tag."""
        tag = self._new_tag_t()
        get_db().add_tag(tag)
        return get_db().retrieve_tag_by_name(tag.name)

    def _new_pic_p(self, description=''):
        """Create new persistent picture."""
        pic = self._new_pic_t()
        get_db().add_picture(pic)
        return get_db().retrieve_picture_by_path(pic.path)

    def _new_grp_p(self, description='', parent=None):
        """Create new persistent group."""
        grp = self._new_grp_t()
        get_db().add_group(grp)
        groups = get_db().retrieve_groups_by_name(grp.name)
        assert groups is not None
        assert len(groups) > 0
        return groups[0]
