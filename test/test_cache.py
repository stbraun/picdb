# coding=utf-8
"""
Test LRUCache
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
from hypothesis import given, example, settings
import hypothesis.strategies as st

from picdb.cache import LRUCache


class LRUCacheTest(unittest.TestCase):
    def test_put(self):
        """Just put an item."""
        cache = LRUCache(5)
        self.assertEqual(0, cache.size)
        cache.put(1, 'aaa')
        self.assertEqual(1, cache.size)

    def test_put_get(self):
        """Put an item an get it again."""
        key = 1
        item = 'aaa'
        cache = LRUCache(5)
        cache.put(key, item)
        self.assertEqual(item, cache.get(key))
        self.assertEqual(1, cache.size)

    def test_not_in_cache(self):
        """Try to get an item which is not in cache."""
        cache = LRUCache(5)
        cache.put(1, 'aaa')
        with self.assertRaises(KeyError):
            cache.get(2)

    def test_lru_behavior(self):
        """Put more than max_size items and check if the least recently used
        was dropped."""
        max_size = 3
        cache = LRUCache(max_size)
        for i in range(max_size):
            cache.put(i, str(i))
        self.assertEqual(max_size, cache.size)
        for i in range(max_size):
            cache.get(i)
        cache.put(max_size, str(max_size))
        self.assertEqual(max_size, cache.size)
        cache.get(max_size)
        with self.assertRaises(KeyError):
            cache.get(0)

    def test_clear_cache(self):
        """Test clearing the cache."""
        max_size = 3
        cache = LRUCache(3)
        for i in range(max_size):
            cache.put(i, str(i))
        self.assertEqual(max_size, cache.size)
        cache.clear()
        self.assertEqual(0, cache.size)

    def test_statistics(self):
        """Test hits and _misses."""
        max_size = 3
        cache = LRUCache(max_size)
        for i in range(max_size):
            cache.put(i, str(i))
        self.assertEqual(0, cache.hits)
        self.assertEqual(0, cache.misses)
        cache.get(0)
        self.assertEqual(1, cache.hits)
        self.assertEqual(0, cache.misses)
        self.assertRaises(KeyError, cache.get, (42,))
        self.assertEqual(1, cache.hits)
        self.assertEqual(1, cache.misses)


# Some additional property based testing

@given(key=st.one_of(st.integers(), st.text(), st.booleans()),
       value=st.one_of(st.integers(), st.text(), st.binary(), st.booleans(),
                       st.floats(allow_nan=False, allow_infinity=False)))
@settings(max_examples=500)
def test_adding_i_s(key, value):
    cache = LRUCache(3)
    assert cache.size == 0
    assert cache.hits == 0
    cache.put(key, value)
    assert cache.size == 1
    assert cache.get(key) == value
    assert cache.misses == 0
    assert cache.hits == 1


def test_multiple():
    max_size = 5
    cache = LRUCache(max_size)

    @given(key=st.integers(min_value=-3, max_value=3), value=st.text())
    @settings(max_examples=500)
    @example(key=-42, value=5)
    @example(key=(-42, 13), value=5)
    def test_add_one(key, value):
        initial_size = cache.size
        initial_misses = cache.misses
        initial_hits = cache.hits
        try:
            cache.get(key)
        except KeyError:
            expected_size = initial_size + 1 if initial_size < max_size else \
                max_size
            assert cache.misses == initial_misses + 1
            assert cache.hits == initial_hits
        else:
            expected_size = initial_size
            assert cache.hits == initial_hits + 1
            assert cache.misses == initial_misses
        cache.put(key, value)
        assert cache.size == expected_size
        assert cache.size >= initial_size

    test_add_one()
    assert cache.size > 0
    cache.clear()
    assert cache.size == 0
    assert cache.misses == 0
    assert cache.hits == 0
