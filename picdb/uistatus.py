# coding=utf-8
"""
Status bar.
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
import logging
import tkinter as tk
from tkinter import ttk
from pkgutil import get_data

import psutil

from .persistence import db_params, _TAG_CACHE, _PICTURE_CACHE, _GROUP_CACHE
from .pictureservices import number_of_pictures
from .groupservices import number_of_groups
from .tagservices import number_of_tags
from .version import long_version


class StatusPanel(ttk.Frame):
    """Present a status."""

    def __init__(self, master):
        super().__init__(master, borderwidth=2, relief=tk.GROOVE)
        self.logger = logging.getLogger('picdb.ui')
        self.version = long_version
        self.num_pics_var = tk.StringVar()
        self.num_groups_var = tk.StringVar()
        self.num_tags_var = tk.StringVar()
        self.memory_usage_var = tk.StringVar()
        self.database_var = tk.StringVar()
        self.cache_stats_tag_var = tk.StringVar()
        self.cache_stats_picture_var = tk.StringVar()
        self.cache_stats_group_var = tk.StringVar()
        self.create_widgets()
        self.report_usage()
        self.show_db()
        self.data_statistics()
        self.cache_statistics()

    def create_widgets(self):
        """Create widgets for view."""
        img = get_data('picdb', 'resources/eye.gif')
        self.logger.info('image {} loaded'.format('resources/eye.gif'))
        self.rowconfigure(0, weight=0)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=6)
        photo = tk.PhotoImage(data=img)
        image = ttk.Label(self, image=photo)
        image.photo = photo
        image.grid(row=0, column=0, rowspan=3, sticky=(tk.W, tk.N))
        ttk.Label(self, textvariable=self.num_pics_var).grid(row=0, column=1,
                                                             sticky=(
                                                                 tk.W, tk.N))
        ttk.Label(self, textvariable=self.num_groups_var).grid(row=1, column=1,
                                                               sticky=(
                                                                   tk.W, tk.N))
        ttk.Label(self, textvariable=self.num_tags_var).grid(row=2, column=1,
                                                             sticky=(
                                                                 tk.W, tk.N))
        ttk.Label(self, textvariable=self.database_var).grid(row=0, column=2,
                                                             sticky=(
                                                                 tk.W, tk.N))
        version_text = 'version: {}'.format(self.version)
        ttk.Label(self, text=version_text).grid(row=1, column=2,
                                                sticky=(tk.W, tk.N))
        ttk.Label(self, textvariable=self.memory_usage_var).grid(row=0,
                                                                 column=3,
                                                                 sticky=(
                                                                     tk.W,
                                                                     tk.N))
        ttk.Label(self,
                  text="Cache stats (hits/misses), size").grid(row=0,
                                                               column=4,
                                                               sticky=(
                                                                   tk.W,
                                                                   tk.N))
        ttk.Label(self,
                  textvariable=self.cache_stats_picture_var).grid(row=1,
                                                                  column=4,
                                                                  sticky=(
                                                                      tk.W,
                                                                      tk.N))
        ttk.Label(self,
                  textvariable=self.cache_stats_group_var).grid(row=2,
                                                                column=4,
                                                                sticky=(
                                                                    tk.W,
                                                                    tk.N))
        ttk.Label(self,
                  textvariable=self.cache_stats_tag_var).grid(row=3,
                                                              column=4,
                                                              sticky=(
                                                                  tk.W,
                                                                  tk.N))

    def _report_usage(self, mem_info=None):
        """report memory usage."""
        info = 'memory usage: {:6.3f}MB'.format(
            mem_info.rss / (1024 * 1024))
        self.memory_usage_var.set(info)

    def report_usage(self, prev_mem_info=None,
                     p=psutil.Process(os.getpid())):
        """Report memory usage."""
        # find max memory
        if p.is_running():
            mem_info = p.memory_info()
            if (mem_info != prev_mem_info and
                    (prev_mem_info is None or mem_info.rss >
                        prev_mem_info.rss)):
                prev_mem_info = mem_info
            self._report_usage(mem_info)
            self.after(500, self.report_usage,
                       prev_mem_info)  # report every 0.5s

    def show_db(self):
        """Display database info."""
        params = db_params()
        if params is None:
            self.after(500, self.show_db)
        else:
            info = 'database: {} ({}) at port {}'.format(params.name,
                                                         params.user,
                                                         params.port)
            self.database_var.set(info)

    def data_statistics(self):
        """Show statistics about data."""
        pics = 'pictures: {}'.format(number_of_pictures())
        groups = 'groups: {}'.format(number_of_groups())
        tags = 'tags: {}'.format(number_of_tags())
        self.num_pics_var.set(pics)
        self.num_groups_var.set(groups)
        self.num_tags_var.set(tags)
        self.after(5000, self.data_statistics)

    def cache_statistics(self):
        """Show cache statistics."""
        templ = '{:s}: {:d} / {}, {}'
        vars = [self.cache_stats_tag_var, self.cache_stats_picture_var,
                self.cache_stats_group_var]
        names = ['tag', 'picture', 'group']
        caches = [_TAG_CACHE, _PICTURE_CACHE, _GROUP_CACHE]
        for name, var, cache in zip(names, vars, caches):
            var.set(
                templ.format(name, cache.hits, cache.misses, cache.size))
        self.after(1000, self.cache_statistics)
