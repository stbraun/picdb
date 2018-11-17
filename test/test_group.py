# coding=utf-8
"""Test Group."""
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

import pytest
from collections.abc import Iterable

from picdb.group import Group
from picdb.entity import Entity


class TestGroup(object):
    """Test group class."""

    def setUp(self):
        """Setup test data."""
        self.g = Group(1, 'a', 'A')
        self.p1 = Entity(None, 'p1', '')
        self.p2 = Entity(None, 'p2', '')

    def test_is_iterable(self):
        """Check that Group instances are iterable."""
        g = Group(1, 'a', 'A')
        assert isinstance(g, Iterable)

    def test_iterate_over_pictures(self):
        """Test iteration without pictures assigned."""
        g = Group(1, 'a', 'A')
        p1 = Entity(None, 'p1', '')
        p2 = Entity(None, 'p2', '')
        for _ in g:
            pytest.fail('No pictures expected.')
        assert 0 == len([p for p in g])
        g.assign_picture(p1)
        assert 1 == len([p for p in g]), 'One picture expected.'
        g.assign_picture(p2)
        assert 2 == len([p for p in g]), 'Two pictures expected.'

    def test_assign_picture(self):
        g = Group(1, 'a', 'A')
        p1 = Entity(None, 'p1', '')
        p2 = Entity(None, 'p2', '')
        g.assign_picture(p1)
        g.assign_picture(p2)
        pics = [p for p in g]
        assert 2 == len(pics)
        assert p1 in pics
        assert p2 in pics

    def test_assign_same_picture_multiple_times(self):
        g = Group(1, 'a', 'A')
        p1 = Entity(None, 'p1', '')
        g.assign_picture(p1)
        assert p1 in g
        assert 1 == len(g)
        g.assign_picture(p1)
        assert 1 == len(g)

    def test_remove_picture(self):
        """Test assigning and removing of a picture. Removing it twice shall
        be ignored."""
        g = Group(1, 'a', 'A')
        p1 = Entity(None, 'p1', '')
        g.assign_picture(p1)
        assert p1 in g
        assert 1 == len(g)
        g.remove_picture(p1)
        assert 0 == len(g)
        # ignore removing unknown picture
        g.remove_picture(p1)

    def test_contains(self):
        g = Group(1, 'a', 'A')
        p1 = Entity(None, 'p1', '')
        p2 = Entity(None, 'p2', '')
        g.assign_picture(p1)
        assert p1 in g
        assert p2 not in g
