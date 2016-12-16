# coding=utf-8
"""
Test Group.
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

from picdb.group import Group
from picdb.entity import Entity


class GroupTest(unittest.TestCase):
    def setUp(self):
        self.g = Group(1, 'a', 'A')
        self.p1 = Entity(None, 'p1', '')
        self.p2 = Entity(None, 'p2', '')

    def test_is_iterable(self):
        """Check that Group instances are iterable."""
        self.assertIsInstance(self.g, collections.Iterable)

    def test_iterate_over_pictures(self):
        """Test iteration without pictures assigned."""
        for p in self.g:
            self.fail('No pictures expected.')
        self.assertEqual(0, len([p for p in self.g]))
        self.g.assign_picture(self.p1)
        self.assertEqual(1, len([p for p in self.g]), 'One picture expected.')
        self.g.assign_picture(self.p2)
        self.assertEqual(2, len([p for p in self.g]), 'Two pictures expected.')

    def test_assign_picture(self):
        self.g.assign_picture(self.p1)
        self.g.assign_picture(self.p2)
        pics = [p for p in self.g]
        self.assertEqual(2, len(pics))
        self.assertTrue(self.p1 in pics)
        self.assertTrue(self.p2 in pics)

    def test_assign_same_picture_multiple_times(self):
        self.g.assign_picture(self.p1)
        self.assertTrue(self.p1 in self.g)
        self.assertEqual(1, len(self.g))
        self.g.assign_picture(self.p1)
        self.assertEqual(1, len(self.g))

    def test_remove_picture(self):
        """Test assigning and removing of a picture. Removing it twice shall
        be ignored."""
        self.g.assign_picture(self.p1)
        self.assertTrue(self.p1 in self.g)
        self.assertEqual(1, len(self.g))
        self.g.remove_picture(self.p1)
        self.assertEqual(0, len(self.g))
        # ignore removing unknown picture
        self.g.remove_picture(self.p1)

    def test_contains(self):
        self.g.assign_picture(self.p1)
        self.assertTrue(self.p1 in self.g)
        self.assertFalse(self.p2 in self.g)
