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
from .uimasterdata import PicTreeView, FilteredTreeview
from .selector import Selector


class TagManagement(ttk.Frame):
    """Manage tag master data."""

    def __init__(self, master):
        super().__init__(master)
        self.logger = logging.getLogger('picdb.ui')
        self.logger.info("Creating Tag Management UI")
        self.content_frame = None
        self.control_frame = None
        self.filter_tree = None
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
        self.filter_tree = TagFilteredTreeview(self.content_frame)
        self.filter_tree.grid(row=0, column=0,
                              sticky=(tk.W, tk.N, tk.E, tk.S))
        self.filter_tree.bind(self.filter_tree.EVT_ITEM_SELECTED,
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
        """Load a bunch of tags from database."""
        self.filter_tree.load_items()

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
        items = self.filter_tree.selected_items()
        self.logger.info('Selected tags: {}'.format(items))
        if len(items) > 0:
            tag = items[0]
            self.editor.tag = tag


class TagFilteredTreeview(FilteredTreeview):
    """Provide a tag tree and selection panel."""
    def __init__(self, master):
        self.logger = logging.getLogger('picdb.ui')
        self.name_filter_var = tk.StringVar()
        self.limit_var = tk.IntVar()
        super().__init__(master, TagTree.create_instance)
        self.name_filter_var.set('%')
        self.name_filter_entry = None
        self.limit_var.set(self.limit_default)

    def _create_filter_frame(self):
        self.filter_frame = ttk.Frame(self)
        self.filter_frame.rowconfigure(0, weight=1)
        self.filter_frame.rowconfigure(1, weight=1)
        self.filter_frame.columnconfigure(0, weight=0)
        self.filter_frame.columnconfigure(1, weight=1)
        lbl_filter = ttk.Label(self.filter_frame, text='Filter on name')
        lbl_filter.grid(row=0, column=0, sticky=tk.E)
        self.name_filter_entry = ttk.Entry(self.filter_frame,
                                           textvariable=self.name_filter_var)
        self.name_filter_entry.grid(row=0, column=1, sticky=(tk.W, tk.E,))
        lbl_limit = ttk.Label(self.filter_frame, text='Max. number of records')
        lbl_limit.grid(row=1, column=0, sticky=tk.E)
        self.limit_entry = ttk.Entry(self.filter_frame,
                                     textvariable=self.limit_var,
                                     width=5,
                                     validate='focusout',
                                     validatecommand=self._validate_limit)
        self.limit_entry.grid(row=1, column=1, sticky=(tk.W,))

    def selected_items(self):
        """Provide list of tags selected in tree.

        :return: selected tags
        :rtype: list(Tag)
        """
        return self.tree.selected_items()

    def add_item_to_tree(self, tag: Tag):
        """Add given tag to tree view."""
        super().add_item_to_tree(tag)

    def _retrieve_items(self):
        """Retrieve a bunch of tags from database.

        name_filter_var and limit_var are considered for retrieval.
        """
        name_filter = self.name_filter_var.get()
        limit = self.limit_var.get()
        tags = persistence.retrieve_tags_by_name_segment(name_filter, limit)
        return tags


class TagTree(PicTreeView):
    """A tree handling tags."""

    def __init__(self, master, tree_only=False):
        self.tree_only = tree_only
        columns = () if tree_only else ('description',)
        super().__init__(master, columns=columns)
        if not tree_only:
            self.heading('description', text='Description')
        # self.column('#0', stretch=False)  # tree column shall not resize

    @classmethod
    def create_instance(cls, master, tree_only=False):
        """Factory method."""
        return TagTree(master, tree_only)

    def add_item(self, tag: Tag):
        """Add given tag to tree."""
        super().add_item(tag)

    def _additional_values(self, item):
        return () if self.tree_only else (item.description,)

    def selected_items(self):
        """Provide list of tags selected in tree.

        :return: selected tags
        :rtype: list(Tag)
        """
        item_ids = self.selection()
        tags = [persistence.retrieve_tag_by_key(int(item_id))
                for item_id in item_ids]
        return tags


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


class TagSelector(Selector):
    """Provide a selector component for tags."""
    def __init__(self, master, **kwargs):
        super().__init__(master, TagTree.create_instance,
                         TagTree.create_instance, **kwargs)

    def selected_items(self):
        items = self.right.get_children()
        tags = [persistence.retrieve_tag_by_key(int(item)) for item in items]
        return tags

    def load_items(self, picture_tags: [Tag]):
        all_tags = persistence.get_all_tags()
        self.init_trees(all_tags, picture_tags)
