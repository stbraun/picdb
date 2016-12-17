# coding=utf-8
"""
Test Picture class.
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

import unittest
import collections

from picdb.tag import Tag
from picdb.picture import Picture


class PictureTest(unittest.TestCase):
    """Test Picture class."""
    def setUp(self):
        self.pic1 = Picture(1, 'pic1', '/com/stbraun/pic1.jpg', 'Picture 1')
        self.pic2 = Picture(2, 'pic2', '/com/stbraun/pic2.jpg', 'Picture 2')
        self.tag1 = Tag(1, 'tag1', 'Tag 1', None)
        self.tag2 = Tag(2, 'tag2', 'Tag 2', None)

    def test_is_iterable(self):
        """Instances of Picture shall be iterable."""
        self.assertIsInstance(self.pic1, collections.Iterable)

    def test_assign_tag(self):
        """Test assigning a tag."""
        self.assertEqual(0, len(self.pic1), 'No tags assigned.')
        self.pic1.assign_tag(self.tag1)
        self.assertEqual(1, len(self.pic1), 'One tags assigned.')
        self.assertTrue(self.tag1 in self.pic1)
        self.pic1.assign_tag(self.tag2)
        self.assertEqual(2, len(self.pic1), 'Two tags assigned.')
        self.assertTrue(self.tag2 in self.pic1)

    def test_assign_same_tag_multiple_times(self):
        """Test assigning same tag multiple times."""
        self.assertEqual(0, len(self.pic1), 'No tags assigned.')
        self.pic1.assign_tag(self.tag1)
        self.assertEqual(1, len(self.pic1), 'One tags assigned.')
        # assign same tag again.
        self.pic1.assign_tag(self.tag1)
        self.assertEqual(1, len(self.pic1), 'One tags assigned.')

    def test_remove_tag(self):
        """Remove tag from picture."""
        self.pic1.assign_tag(self.tag1)
        self.pic1.assign_tag(self.tag2)
        self.assertEqual(2, len(self.pic1), 'Two tags assigned.')
        self.assertTrue(self.tag1 in self.pic1)
        self.assertTrue(self.tag2 in self.pic1)
        self.pic1.remove_tag(self.tag1)
        self.assertEqual(1, len(self.pic1), 'One tags left.')
        self.assertFalse(self.tag1 in self.pic1)
        self.assertTrue(self.tag2 in self.pic1)

    def test_contains(self):
        """Check if tag is assigned to picture."""
        self.pic1.assign_tag(self.tag1)
        self.assertTrue(self.tag1 in self.pic1)
        self.assertFalse(self.tag2 in self.pic1)

    def assign_tags(self):
        """Test setting of tags vector."""
        tags = [self.tag1, self.tag2]
        self.pic1.tags = tags
        self.assertEqual(2, len(self.pic1), 'Two tags assigned.')
        self.pic1.tags = []
        self.assertEqual(0, len(self.pic1), 'No tags assigned.')
        self.pic1.tags = (self.tag1, )
        self.assertEqual(1, len(self.pic1), 'One tags assigned.')
        self.pic1.tags = None
        self.assertEqual(0, len(self.pic1), 'No tags assigned.')
