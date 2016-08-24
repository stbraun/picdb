# coding=utf-8
"""
Series management.
"""
# Copyright (c) 2016 Stefan Braun
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
# AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import tkinter as tk
from tkinter import ttk
import logging
import persistence
from model import PictureSeries
from uimasterdata import PicTreeView


class SeriesManagement(ttk.Frame):
    """Manage picture series master data."""

    def __init__(self, master):
        super().__init__(master)
        self.logger = logging.getLogger('picdb.ui')
        self.content = None
        self.content_frame = self.create_content_frame()
        self.control_frame = self.create_control_frame()
        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        """Create the master data UI."""
        self.create_content_frame()
        self.create_control_frame()

    def create_content_frame(self):
        """Create the content frame.

        :return: content frame
        :rtype: ttk.Frame
        """
        content_frame = ttk.Frame(self)
        content_frame.grid(row=0, column=0,
                           sticky=(tk.W, tk.N, tk.E, tk.S))
        content_frame.rowconfigure(0, weight=1)
        self.content = SeriesManagementContent(content_frame)
        self.content.grid(row=0, column=0, sticky=(tk.N, tk.E, tk.S, tk.W))
        self.content.tree.bind('<<TreeviewSelect>>', self.item_selected)
        return content_frame

    def create_control_frame(self):
        """Create the control frame.

        :return: control frame
        :rtype: ttk.Frame
        """
        control_frame = ttk.Frame(self, borderwidth=2, relief=tk.GROOVE)
        control_frame.grid(row=1, column=0,
                           sticky=(tk.W, tk.N, tk.E, tk.S))
        self.columnconfigure(0, weight=1)
        refresh_button = ttk.Button(control_frame, text='refresh',
                                    command=self.refresh)
        refresh_button.grid(row=0, column=0, sticky=(tk.W, tk.N))
        save_button = ttk.Button(control_frame, text='save series',
                                 command=self.save_series)
        save_button.grid(row=0, column=1, sticky=(tk.W, tk.N))
        return control_frame

    def refresh(self):
        self.content.refresh()

    def save_series(self):
        """Save the series currently in editor."""
        series = self.content.editor.series
        if series is not None:
            persistence.update_series(series)

    def item_selected(self, _):
        """An item in the tree view was selected."""
        selected_series = self.content.tree.selection()
        if len(selected_series) > 0:
            series = persistence.retrieve_series_by_key(selected_series[0])
            self.content.editor.series = series


class SeriesManagementContent(ttk.Frame):
    """Manage picture series master data."""

    def __init__(self, master):
        super().__init__(master)
        self.logger = logging.getLogger('picdb.ui')
        self.tree = None
        self.editor = None
        self.create_widgets()

    def create_widgets(self):
        """Create the master data UI."""
        self.logger.info("Creating SeriesManagement UI")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.tree = PictureSeriesTree(master=self)
        self.tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W))

        self.editor = PictureSeriesEditor(self)
        self.editor.grid(row=0, column=1, sticky=(tk.N, tk.E, tk.W))

    def refresh(self):
        """Refresh tree."""
        all_series = persistence.get_all_series()
        self.tree.clear()
        for series in all_series:
            self.tree.add_series(series)


class PictureSeriesTree(PicTreeView):
    """A tree handling picture series."""
    def __init__(self, master):
        super().__init__(master, columns=('description', ))
        self.heading('description', text='Description')
        self.column('#0', stretch=False)  # tree column does not resize

    def add_series(self, series: PictureSeries):
        """Add given series to tree."""
        self.insert('', 'end', series.key,
                    text=series.name, values=(series.description,))


class PictureSeriesEditor(ttk.LabelFrame):
    """Editor for PictureSeries objects."""
    def __init__(self, master, text='Edit series'):
        super().__init__(master, text=text)
        self.series_ = None
        self.id_var = tk.IntVar()
        self.name_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        self.rowconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text='id').grid(row=0, column=0, sticky=tk.E)
        ttk.Label(self, text='name').grid(row=1, column=0, sticky=tk.E)
        ttk.Label(self, text='description').grid(row=2, column=0, sticky=tk.E)
        ttk.Entry(self, textvariable=self.id_var,
                  state='readonly').grid(row=0, column=1, sticky=tk.W)
        ttk.Entry(self, textvariable=self.name_var).grid(row=1, column=1,
                                                         sticky=(tk.E, tk.W))
        ttk.Entry(self,
                  textvariable=self.description_var).grid(row=2,
                                                          column=1,
                                                          sticky=(tk.E, tk.W))

    @property
    def series(self):
        if self.series_ is not None:
            self.series_.id = self.id_var.get()
            self.series_.name = self.name_var.get()
            self.series_.description = self.description_var.get()
        return self.series_

    @series.setter
    def series(self, series_: PictureSeries):
        self.series_ = series_
        self.id_var.set(series_.key)
        self.name_var.set(series_.name)
        self.description_var.set(series_.description)
