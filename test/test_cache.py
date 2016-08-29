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
from picdb.cache import LRUCache


class LRUCacheTest(unittest.TestCase):
    def test_put(self):
        """Just put an item."""
        cache = LRUCache(5)
        self.assertEqual(0, cache.size())
        cache.put(1, 'aaa')
        self.assertEqual(1, cache.size())

    def test_put_get(self):
        """Put an item an get it again."""
        key = 1
        item = 'aaa'
        cache = LRUCache(5)
        cache.put(key, item)
        self.assertEqual(item, cache.get(key))
        self.assertEqual(1, cache.size())

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
        self.assertEqual(max_size, cache.size())
        for i in range(max_size):
            cache.get(i)
        cache.put(max_size, str(max_size))
        self.assertEqual(max_size, cache.size())
        cache.get(max_size)
        with self.assertRaises(KeyError):
            cache.get(0)

    def test_clear_cache(self):
        """Test clearing the cache."""
        max_size = 3
        cache = LRUCache(3)
        for i in range(max_size):
            cache.put(i, str(i))
        self.assertEqual(max_size, cache.size())
        cache.clear()
        self.assertEqual(0, cache.size())




