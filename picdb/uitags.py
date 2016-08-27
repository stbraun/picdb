# coding=utf-8
"""
Tak management.
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

import logging
import tkinter as tk
from tkinter import ttk

from . import persistence
from .model import Tag
from .uimasterdata import PicTreeView


class TagManagement(ttk.Frame):
    """Manage tag master data."""

    def __init__(self, master):
        super().__init__(master)
        self.logger = logging.getLogger('picdb.ui')
        self.logger.info("Creating Tag Management UI")
        self.content_frame = None
        self.control_frame = None
        self.tag_selector = None
        self.editor = None
        self.create_widgets()

    def create_widgets(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.create_content_frame()
        self.content_frame.grid(row=0, column=0,
                                sticky=(tk.W, tk.N, tk.E, tk.S))
        self.create_control_frame()
        self.control_frame.grid(row=1, column=0,
                                sticky=(tk.W, tk.N, tk.E, tk.S))

    def create_content_frame(self):
        """Create the content frame."""
        self.content_frame = ttk.Frame(self)
        self.content_frame.rowconfigure(0, weight=1)
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(1, weight=1)
        self.tag_selector = TagSelector(self.content_frame)
        self.tag_selector.grid(row=0, column=0,
                               sticky=(tk.W, tk.N, tk.E, tk.S))
        self.tag_selector.bind(self.tag_selector.EVT_TAG_SELECTED,
                               self.item_selected)
        self.editor = TagEditor(self.content_frame)
        self.editor.grid(row=0, column=1, sticky=(tk.N, tk.E, tk.W))

    def create_control_frame(self):
        """Create the control frame."""
        self.control_frame = ttk.Frame(self, borderwidth=2, relief=tk.GROOVE)
        self.columnconfigure(0, weight=1)
        load_button = ttk.Button(self.control_frame, text='load tags',
                                 command=self.load_tags)
        load_button.grid(row=0, column=0, sticky=(tk.W, tk.N))
        add_button = ttk.Button(self.control_frame, text='add tag',
                                command=self.add_tag)
        add_button.grid(row=0, column=1, sticky=(tk.W, tk.N))
        save_button = ttk.Button(self.control_frame, text='save tag',
                                 command=self.save_tag)
        save_button.grid(row=0, column=2, sticky=(tk.W, tk.N))

    def load_tags(self):
        """Load a bunch of tags from database.
        """
        self.tag_selector.load_tags()

    def add_tag(self):
        """Push an empty tag to editor."""
        tag = Tag(None, '', '')
        self.editor.tag = tag

    def save_tag(self):
        """Save the tag currently in editor."""
        tag = self.editor.tag
        if tag is not None:
            if tag.key is None:
                persistence.add_tag(tag)
            else:
                persistence.update_tag(tag)
        self.load_tags()

    def item_selected(self, _):
        """An item in the tree view was selected."""
        items = self.tag_selector.selected_tags()
        self.logger.info('Selected tags: {}'.format(items))
        if len(items) > 0:
            tag = items[0]
            self.editor.tag = tag


class TagSelector(ttk.Frame):
    """Provide a tag tree and selection panel."""
    def __init__(self, master):
        super().__init__(master)
        self.logger = logging.getLogger('picdb.ui')
        self.EVT_TAG_SELECTED = '<<<TagSelected>>>'
        self.supported_events = {self.EVT_TAG_SELECTED}
        self.listeners = {}
        self.filter_frame = None
        self.tree = None
        self.name_filter_var = tk.StringVar()
        self.name_filter_var.set('%')
        self.name_filter_entry = None
        self.limit_var = tk.IntVar()
        self.limit_var.set(50)
        self.limit_entry = None
        self.create_widgets()

    def create_widgets(self):
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.create_filter_frame()
        self.filter_frame.grid(row=0, column=0,
                               sticky=(tk.W, tk.N, tk.E, tk.S))
        self.tree = TagTree(self)
        self.tree.bind('<<TreeviewSelect>>', self.__item_selected)
        self.tree.grid(row=1, column=0,
                       sticky=(tk.W, tk.N, tk.E, tk.S))

    def create_filter_frame(self):
        self.filter_frame = ttk.Frame(self)
        self.filter_frame.rowconfigure(0, weight=1)
        self.filter_frame.rowconfigure(1, weight=1)
        self.filter_frame.columnconfigure(0, weight=0)
        self.filter_frame.columnconfigure(1, weight=1)
        lbl_filter = ttk.Label(self.filter_frame, text='Filter on path')
        lbl_filter.grid(row=0, column=0, sticky=tk.E)
        self.name_filter_entry = ttk.Entry(self.filter_frame,
                                           textvariable=self.name_filter_var)
        self.name_filter_entry.grid(row=0, column=1, sticky=(tk.W, tk.E,))
        lbl_limit = ttk.Label(self.filter_frame, text='Max. number of records')
        lbl_limit.grid(row=1, column=0, sticky=tk.E)
        self.limit_entry = ttk.Entry(self.filter_frame,
                                     textvariable=self.limit_var,
                                     width=5)
        self.limit_entry.grid(row=1, column=1, sticky=(tk.W,))

    def selected_tags(self):
        """Provide list of tags selected in tree.

        :return: selected tags
        :rtype: list(Tag)
        """
        item_ids = self.tree.selection()
        pics = [persistence.retrieve_tag_by_key(pic_id) for pic_id in item_ids]
        self.logger.debug('Selected tags: {}'.format(pics))
        return pics

    def __item_selected(self, event):
        """An item in the tree view was selected."""
        items = self.tree.selection()
        self.logger.info('Selected tags: {}'.format(items))
        if len(items) > 0:
            if self.EVT_TAG_SELECTED in self.listeners.keys():
                listener = self.listeners[self.EVT_TAG_SELECTED]
                listener(event)

    def load_tags(self):
        """Load a bunch of tags from database.

        name_filter_var and limit_var are considered for retrieval.
        """
        self.tree.clear()
        name_filter = self.name_filter_var.get()
        limit = self.limit_var.get()
        tags = persistence.retrieve_tags_by_name_segment(name_filter, limit)
        for tag in tags:
            self.tree.add_tag(tag)

    def add_picture_to_tree(self, tag: Tag):
        """Add given tag to tree view."""
        self.tree.add_tag(tag)

    def bind(self, sequence=None, func=None, add=None):
        """Bind to this widget at event SEQUENCE a call to function FUNC."""
        if sequence in self.supported_events:
            self.logger.debug('Binding {} to {}'.format(func,
                                                        self.EVT_TAG_SELECTED))
            self.listeners[sequence] = func
        else:
            super().bind(sequence, func, add)


class TagTree(PicTreeView):
    """A tree handling tags."""

    def __init__(self, master):
        super().__init__(master, columns=('description',))
        self.heading('description', text='Description')
        self.column('#0', stretch=False)  # tree column does not resize

    def add_tag(self, tag: Tag):
        """Add given tag to tree."""
        self.insert('', 'end', tag.key,
                    text=tag.name, values=(tag.description,))


class TagEditor(ttk.LabelFrame):
    """Editor for Tag objects."""

    def __init__(self, master, text='Edit tag'):
        super().__init__(master, text=text)
        self.tag_ = None
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
    def tag(self):
        if self.tag_ is not None:
            self.tag_.name = self.name_var.get()
            self.tag_.description = self.description_var.get()
        return self.tag_

    @tag.setter
    def tag(self, tag_: Tag):
        self.tag_ = tag_
        self.id_var.set(tag_.key)
        self.name_var.set(tag_.name)
        self.description_var.set(tag_.description)
