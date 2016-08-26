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
        self.content = None
        self.logger.info("Creating Tag Management UI")
        self.content_frame = self.create_content_frame()
        self.control_frame = self.create_control_frame()
        self.refresh()

    def create_content_frame(self):
        """Create the content frame.

        :return: content frame
        :rtype: ttk.Frame
        """
        content_frame = ttk.Frame(self)
        content_frame.grid(row=0, column=0,
                           sticky=(tk.W, tk.N, tk.E, tk.S))
        content_frame.rowconfigure(0, weight=1)
        self.content = TagManagementContent(content_frame)
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
        add_button = ttk.Button(control_frame, text='add tag',
                                command=self.add_tag)
        add_button.grid(row=0, column=1, sticky=(tk.W, tk.N))
        save_button = ttk.Button(control_frame, text='save tag',
                                 command=self.save_tag)
        save_button.grid(row=0, column=2, sticky=(tk.W, tk.N))
        return control_frame

    def refresh(self):
        self.content.refresh()

    def add_tag(self):
        """Push an empty tag to editor."""
        tag = Tag(None, '', '')
        self.content.editor.tag = tag

    def save_tag(self):
        """Save the tag currently in editor."""
        tag = self.content.editor.tag
        if tag is not None:
            if tag.key is None:
                persistence.add_tag(tag)
            else:
                persistence.update_tag(tag)
        self.refresh()

    def item_selected(self, _):
        """An item in the tree view was selected."""
        selected_tag = self.content.tree.selection()
        if len(selected_tag) > 0:
            tag = persistence.retrieve_tag_by_key(selected_tag[0])
            self.content.editor.tag = tag


class TagManagementContent(ttk.Frame):
    """Manage tag master data."""

    def __init__(self, master):
        super().__init__(master)
        self.logger = logging.getLogger('picdb.ui')
        self.tree = None
        self.editor = None
        self.create_widgets()

    def create_widgets(self):
        """Create the master data UI."""
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.tree = TagTree(master=self)
        self.tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W))
        self.editor = TagEditor(self)
        self.editor.grid(row=0, column=1, sticky=(tk.N, tk.E, tk.W))

    def refresh(self):
        """Refresh tree."""
        all_tags = persistence.get_all_tags()
        self.tree.clear()
        for tag in all_tags:
            self.tree.add_tag(tag)


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
