# coding=utf-8
"""
Tests for persistence.
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


import os
import unittest

from picdb.persistence import Persistence
from picdb.dataobjects import DTag, DGroup, DPicture


class TestPersistence(unittest.TestCase):
    """Test case for persistence."""

    def setUp(self):
        # Create test database
        pwd = os.path.dirname(__file__)
        self.DATABASE = os.path.join(pwd, "PICDB_TEST.db")
        self.db = Persistence(db=self.DATABASE)

    def tearDown(self):
        # Delete test database
        pass
        if os.path.exists(self.DATABASE):
            if self.db is not None:
                self.db.close()
            os.remove(self.DATABASE)
            pass

    def test_add_and_retrieve_tag(self):
        tag1 = DTag(None, 'Tag 1', "My first tag.", None)
        tags = self.db.retrieve_all_tags()
        self.assertEqual(0, len(tags))
        self.db.add_tag(tag1)
        tags = self.db.retrieve_all_tags()
        self.assertEqual(1, len(tags))
        tag_retrieved = tags[0]
        self.assertEqual(tag1.name, tag_retrieved.name)
        self.assertEqual(tag1.description, tag_retrieved.description)
        tag2 = DTag(None, 'Tag 2', "My second tag.", None)
        self.db.add_tag(tag2)
        tags = self.db.retrieve_all_tags()
        self.assertEqual(2, len(tags))
        tag = self.db.retrieve_tag_by_name(tag1.name)
        self.assertIsNot(None, tag)
        self.assertEqual(tag_retrieved.key, tag.key)
        self.assertEqual(tag_retrieved.name, tag.name)
        self.assertEqual(tag_retrieved.description, tag.description)

    def test_add_and_retrieve_series(self):
        series1 = DGroup(None, 'Series 1', "My first series.", None)
        series = self.db.retrieve_all_series()
        self.assertEqual(0, len(series))
        self.db.add_series(series1)
        series = self.db.retrieve_all_series()
        self.assertEqual(1, len(series))
        series_retrieved = series[0]
        self.assertEqual(series1.name, series_retrieved.name)
        self.assertEqual(series1.description, series_retrieved.description)
        series2 = DTag(None, 'Series 2', "My second series.", None)
        self.db.add_series(series2)
        series = self.db.retrieve_all_series()
        self.assertEqual(2, len(series))

    def test_add_and_retrieve_picture(self):
        picture1 = DPicture(None, 'eye', "/resources/eye.gif",
                            "My first picture.")
        picture = self.db.retrieve_picture_by_path(picture1.path)
        self.assertIs(None, picture)
        self.db.add_picture(picture1)
        picture_retrieved = self.db.retrieve_picture_by_path(picture1.path)
        self.assertIsNot(None, picture_retrieved)
        self.assertEqual(picture1.name, picture_retrieved.name)
        self.assertEqual(picture1.path, picture_retrieved.path)
        self.assertEqual(picture1.description, picture_retrieved.description)

    def test_add_tag_to_picture(self):
        path = "/resources/eye.gif"
        self.db.add_picture(DPicture(None, 'eye',
                                     "/resources/eye.gif",
                                     "My first picture."))
        picture = self.db.retrieve_picture_by_path(path)
        tag_name_1 = 'Tag 1'
        tag_name_2 = 'Tag 2'
        tag_name_3 = 'Tag 3'
        self.db.add_tag(DTag(None, tag_name_1, "My first tag.", None))
        self.db.add_tag(DTag(None, tag_name_2, "My second tag.", None))
        self.db.add_tag(DTag(None, tag_name_3, "My third tag.", None))
        tag_1 = self.db.retrieve_tag_by_name(tag_name_1)
        tag_2 = self.db.retrieve_tag_by_name(tag_name_2)
        tag_3 = self.db.retrieve_tag_by_name(tag_name_3)
        self.db.add_tag_to_picture(picture, tag_1)
        self.db.add_tag_to_picture(picture, tag_3)
        tags = self.db.retrieve_tags_for_picture(picture)
        self.assertIn(tag_1.__str__(), tags.__str__())
        self.assertIn(tag_3.__str__(), tags.__str__())
        self.assertNotIn(tag_2.__str__(), tags.__str__())

    def test_update_picture(self):
        picture1 = DPicture(None, 'eye',
                            "/resources/eye.gif", "My first picture.")
        self.db.add_picture(picture1)
        pic = self.db.retrieve_picture_by_path(picture1.path)
        new_description = 'new description'
        pic = pic._replace(description=new_description)
        self.db.update_picture(pic)
        pic2 = self.db.retrieve_picture_by_key(pic.key)
        self.assertIsNot(None, pic2)
        self.assertEqual(new_description, pic2.description)

    def test_update_series(self):
        series1 = DGroup(None, 'eyes', "My series.", None)
        self.db.add_series(series1)
        series2 = self.db.retrieve_series_by_name(series1.name)
        new_description = 'new description'
        series2 = series2._replace(description=new_description)
        self.db.update_group(series2)
        series3 = self.db.retrieve_series_by_key(series2.key)
        self.assertIsNot(None, series3)
        self.assertEqual(new_description, series3.description)

    def test_update_tag(self):
        tag1 = DTag(None, 'eyes', "My tag.", None)
        self.db.add_tag(tag1)
        tag2 = self.db.retrieve_tag_by_name(tag1.name)
        new_description = 'new description'
        tag2 = tag2._replace(description=new_description)
        self.db.update_tag(tag2)
        tag3 = self.db.retrieve_tag_by_key(tag2.key)
        self.assertIsNot(None, tag3)
        self.assertEqual(new_description, tag3.description)

    def test_retrieve_pictures_for_group(self):
        picture1 = DPicture(None, 'p1',
                            "/resources/p1.gif", "My first picture.")
        picture2 = DPicture(None, 'p2',
                            "/resources/p2.gif", "My first picture.")
        self.db.add_picture(picture1)
        self.db.add_picture(picture2)
        picture1 = self.db.retrieve_picture_by_path(picture1.path)
        picture2 = self.db.retrieve_picture_by_path(picture2.path)
        group = DGroup(None, 'grp', 'group', None)
        self.db.add_series(group)
        group = self.db.retrieve_series_by_name(group.name)
        pics = self.db.retrieve_pictures_for_group(group)
        self.assertEqual(0, len(pics))
        self.db.add_picture_to_group(picture1, group)
        pics = self.db.retrieve_pictures_for_group(group)
        self.assertEqual(1, len(pics))
        self.db.add_picture_to_group(picture2, group)
        pics = self.db.retrieve_pictures_for_group(group)
        self.assertEqual(2, len(pics))
