# coding=utf-8
"""Test Picture class."""
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

from collections.abc import Iterable

from picdb.tag import Tag
from picdb.picture import Picture


class TestPicture(object):
    """Test Picture class."""

    def setUp(self):
        """Setup test data."""
        pic1 = Picture(1, 'pic1', '/com/stbraun/pic1.jpg', 'Picture 1')
        pic2 = Picture(2, 'pic2', '/com/stbraun/pic2.jpg', 'Picture 2')
        tag1 = Tag(1, 'tag1', 'Tag 1', None)
        tag2 = Tag(2, 'tag2', 'Tag 2', None)

    def test_is_iterable(self):
        """Instances of Picture shall be iterable."""
        pic1 = Picture(1, 'pic1', '/com/stbraun/pic1.jpg', 'Picture 1')
        assert isinstance(pic1, Iterable)

    def test_assign_tag(self):
        """Test assigning a tag."""
        pic1 = Picture(1, 'pic1', '/com/stbraun/pic1.jpg', 'Picture 1')
        tag1 = Tag(1, 'tag1', 'Tag 1', None)
        tag2 = Tag(2, 'tag2', 'Tag 2', None)
        assert 0 == len(pic1), 'No tags assigned.'
        pic1.assign_tag(tag1)
        assert 1 == len(pic1), 'One tags assigned.'
        assert tag1 in pic1
        pic1.assign_tag(tag2)
        assert 2 == len(pic1), 'Two tags assigned.'
        assert tag2 in pic1

    def test_assign_same_tag_multiple_times(self):
        """Test assigning same tag multiple times."""
        pic1 = Picture(1, 'pic1', '/com/stbraun/pic1.jpg', 'Picture 1')
        tag1 = Tag(1, 'tag1', 'Tag 1', None)
        pic1.assign_tag(tag1)
        assert 1 == len(pic1), 'One tags assigned.'
        # assign same tag again.
        pic1.assign_tag(tag1)
        assert 1 == len(pic1), 'One tags assigned.'

    def test_remove_tag(self):
        """Remove tag from picture."""
        pic1 = Picture(1, 'pic1', '/com/stbraun/pic1.jpg', 'Picture 1')
        tag1 = Tag(1, 'tag1', 'Tag 1', None)
        tag2 = Tag(2, 'tag2', 'Tag 2', None)
        pic1.assign_tag(tag1)
        pic1.assign_tag(tag2)
        assert 2 == len(pic1), 'Two tags assigned.'
        assert tag1 in pic1
        assert tag2 in pic1
        pic1.remove_tag(tag1)
        assert 1 == len(pic1), 'One tags left.'
        assert tag1 not in pic1
        assert tag2 in pic1

    def test_contains(self):
        """Check if tag is assigned to picture."""
        pic1 = Picture(1, 'pic1', '/com/stbraun/pic1.jpg', 'Picture 1')
        tag1 = Tag(1, 'tag1', 'Tag 1', None)
        tag2 = Tag(2, 'tag2', 'Tag 2', None)
        pic1.assign_tag(tag1)
        assert tag1 in pic1
        assert tag2 not in pic1

    def assign_tags(self):
        """Test setting of tags vector."""
        pic1 = Picture(1, 'pic1', '/com/stbraun/pic1.jpg', 'Picture 1')
        tag1 = Tag(1, 'tag1', 'Tag 1', None)
        tag2 = Tag(2, 'tag2', 'Tag 2', None)
        tags = [tag1, tag2]
        pic1.tags = tags
        assert 2 == len(pic1), 'Two tags assigned.'
        pic1.tags = []
        assert 0 == len(pic1), 'No tags assigned.'
        pic1.tags = (tag1, )
        assert 1 == len(pic1), 'One tags assigned.'
        pic1.tags = None
        assert 0 == len(pic1), 'No tags assigned.'
