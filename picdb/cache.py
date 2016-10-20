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


class LRUCache:
    """LRU cache."""
    def __init__(self, max_size):
        self.max_size = max_size
        self.__cache = {}
        self.__usage_list = []
        self._misses = 0
        self._hits = 0

    def put(self, key, item):
        """Put item into __cache."""
        self.__cache[key] = item
        self.__update_usage(key)

    def get(self, key):
        """Try to retrieve item """
        try:
            item = self.__cache[key]
            self._hits += 1
            self.__update_usage(key)
            return item
        except KeyError:
            self._misses += 1
            raise

    @property
    def size(self):
        return len(self.__usage_list)

    @property
    def misses(self):
        return self._misses

    @property
    def hits(self):
        return self._hits

    def clear(self):
        """Clear cache."""
        self.__cache = {}
        self.__usage_list = []
        self._misses = 0
        self._hits = 0

    def __update_usage(self, key):
        if key in self.__usage_list:
            self.__usage_list.remove(key)
        self.__usage_list.insert(0, key)
        self.__keep_max_size()

    def __keep_max_size(self):
        while len(self.__usage_list) > self.max_size:
            key = self.__usage_list.pop()
            self.__cache.pop(key)
