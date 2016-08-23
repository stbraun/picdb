# coding=utf-8
"""
The UI for master data management of groups and tags.
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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import tkinter as tk
from tkinter import ttk
import logging
from persistence import get_db


class SeriesManagement(ttk.Frame):
    """Manage picture series master data."""

    def __init__(self, master):
        super().__init__(master)
        self.logger = logging.getLogger('picdb.ui')
        self.series_list_box = None
        self.series_names = self.get_series_names()
        self.series_names_var = tk.StringVar(value=self.series_names)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.create_widgets()

    def create_widgets(self):
        """Create the master data UI."""
        self.logger.info("Creating SeriesManagement UI")
        self.series_list_box = tk.Listbox(master=self,
                                          listvariable=self.series_names_var)
        self.series_list_box.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W))

    def get_series_names(self):
        db = get_db()
        series = db.retrieve_all_series()
        self.logger.info('{} series loaded'.format(len(series)))
        return series
