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

import logging
import tkinter as tk
from tkinter import ttk
from .model import Entity


class PicTreeView(ttk.Treeview):
    """Extended tree view."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.logger = logging.getLogger('picdb.ui')

    @classmethod
    def create_instance(cls, master):
        """Factory method."""
        return PicTreeView(master)

    def clear(self):
        """Remove all items from tree."""
        items = self.get_children()
        if len(items) > 0:
            self.delete(*items)

    def add_item(self, item: Entity):
        """Add given item to tree."""
        self.insert('', 'end', item.key,
                    text=item.name, values=(item.description,))

    def selected_items(self):
        """Provide list of items selected in tree.

        :return: selected items
        :rtype: [Entity]
        """
        raise NotImplementedError


class FilteredTreeview(ttk.Frame):
    """Abstract filter_tree class."""
    def __init__(self, master, tree_factory):
        super().__init__(master)
        self.logger = logging.getLogger('picdb.ui')
        self.EVT_ITEM_SELECTED = '<<<ItemSelected>>>'
        self.supported_events = {self.EVT_ITEM_SELECTED}
        self.listeners = {}
        self.filter_frame = None
        self.tree = None
        self.tree_factory = tree_factory
        self.limit_default = 50
        self.limit_entry = None
        self._create_widgets()

    def _create_widgets(self):
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self._create_filter_frame()
        self.filter_frame.grid(row=0, column=0,
                               sticky=(tk.W, tk.N, tk.E, tk.S))
        self.tree = self.tree_factory(self)
        self.tree.bind('<<TreeviewSelect>>', self._item_selected)
        self.tree.grid(row=1, column=0,
                       sticky=(tk.W, tk.N, tk.E, tk.S))

    def _create_filter_frame(self):
        """Provide a frame for selection of filter criteria."""
        raise NotImplementedError('Please override this method.')

    def selected_items(self):
        """Provide list of items selected in tree.

        :return: selected items
        :rtype: list(Entity)
        """
        raise NotImplementedError('Please override this method.')

    def add_item_to_tree(self, item: Entity):
        """Add given tag to tree view."""
        self.tree.add_item(item)

    def bind(self, sequence=None, func=None, add=None):
        """Bind to this widget at event SEQUENCE a call to function FUNC."""
        if sequence in self.supported_events:
            self.listeners[sequence] = func
        else:
            super().bind(sequence, func, add)

    def load_items(self):
        """Load a bunch of items from database."""
        self.tree.clear()
        items = self._retrieve_items()
        for item in items:
            self.tree.add_item(item)

    def _retrieve_items(self):
        """Retrieve items to load into tree view.

        :return: select items
        :rtype: list[Entity]
        """
        raise NotImplementedError('Please override this method.')

    def _item_selected(self, event):
        """An item in the tree view was selected."""
        items = self.tree.selection()
        if len(items) > 0:
            if self.EVT_ITEM_SELECTED in self.listeners.keys():
                listener = self.listeners[self.EVT_ITEM_SELECTED]
                listener(event)

    def _validate_limit(self):
        """Validator for limit entry."""
        x = self.limit_entry.get()
        self.logger.info("limit = {}".format(x))
        try:
            int(x)
        except ValueError:
            self.limit_entry.delete(0, len(x))
            self.limit_entry.insert(0, str(self.limit_default))
        return True
