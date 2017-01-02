# coding=utf-8
"""
A simple LRU cache.
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

from collections import deque


class LRUCache:
    """LRU cache."""
    def __init__(self, max_size):
        self.max_size = max_size
        self.lru_required = self.max_size >= 0
        self.__cache = {}
        self.__usage_list = deque()
        self._misses = 0
        self._hits = 0

    def put(self, key, item):
        """Put item into __cache."""
        self.__cache[key] = item
        if self.lru_required:
            self.__update_usage(key)
            self.__keep_max_size()

    def get(self, key):
        """Try to retrieve item """
        try:
            item = self.__cache[key]
            self._hits += 1
            if self.lru_required:
                self.__update_usage(key)
            return item
        except KeyError:
            self._misses += 1
            raise

    @property
    def size(self):
        """ Get current size of cache.

        :return: current cace entries.
        :rtype: int
        """
        return len(self.__cache)

    @property
    def misses(self):
        """ Get number of cache misses.

        :return: number of misses.
         :rtype: int
        """
        return self._misses

    @property
    def hits(self):
        """ Get number of cache hits.

        :return: number of hits.
         :rtype: int
        """
        return self._hits

    def clear(self):
        """Clear cache."""
        self.__cache = {}
        self.__usage_list.clear()
        self._misses = 0
        self._hits = 0

    def __update_usage(self, key):
        """ Push key to top of cache.

        :param key: key of cache item.
        :type key: any hashable type
        """
        if key in self.__usage_list:
            self.__usage_list.remove(key)
        self.__usage_list.appendleft(key)

    def __keep_max_size(self):
        """ Keep cache size in required range. """
        while len(self.__usage_list) > self.max_size:
            key = self.__usage_list.pop()
            self.__cache.pop(key)

    def __iter__(self):
        return iter(self.__cache)
