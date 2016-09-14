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

    def add_item(self, item):
        """Add given item to tree.

        Keeps tree sorted by item names.

        :param item: item to add
        :type item: Entity
        """
        children = self.get_children(item=None)
        index = 'end'
        for idx, child in enumerate(children):
            if self._is_less(item, child):
                index = idx
                break
        self.insert('', index, item.key,
                    text=item.name, values=self._additional_values(item))

    def _is_less(self, item, key):
        """Is given item less than item by key?

        :param item: item to compare.
        :type item: Entity
        :param key: item identifier in tree.
        :type key: str
        :return: True if item is less
        :rtype: bool
        """
        raise NotImplementedError

    def _additional_values(self, item):
        """Provide a tuple with values to display in the tree."""
        raise NotImplementedError

    def selected_items(self):
        """Provide list of items selected in tree.

        :return: selected items
        :rtype: [Entity]
        """
        raise NotImplementedError


class HierarchicalTreeView(PicTreeView):
    """Tree view supporting hierarchical items."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._dnd_active = False
        self._dnd_start_item = None
        self.bind('<Button-1>', self._dnd_start)
        self.bind('<ButtonRelease-1>', self._dnd_finish)

    def _dnd_start(self, event):
        """Start possible dnd action."""
        item = self.identify_row(event.y)
        self._dnd_start_item = item
        self.bind('<Motion>', self._dnd_motion)

    def _dnd_finish(self, event):
        """Finish dnd action."""
        item = self.identify_row(event.y)
        try:
            if item != self._dnd_start_item:
                self.logger.info('Finish DND on item {}'.format(item))
                self._dnd_action(self._dnd_start_item, item)
        finally:
            self.config(cursor='')
            self._dnd_start_item = None
            self._dnd_active = False

    def _dnd_action(self, start_item, target_item):
        """Item start was dragged to item target.

        Override this method to implement the desired action.

        :param start_item: item which is dragged
        :type start_item: str
        :param target_item: item to drop on
        :type target_item: str
        """
        self.logger.info(
            'Item {} was dragged to {}'.format(start_item, target_item))

    def _dnd_motion(self, _):
        """Start dnd action."""
        self.config(cursor='exchange')
        self.unbind('<Motion>')
        self._dnd_start_active = True

    def add_item(self, item):
        """Add given item to tree.

        Keeps tree sorted by item names.

        :param item: item to add
        :type item: Entity
        """
        parent_key = ''
        if item.parent is not None:
            if not self.exists(item.parent.key):
                self.add_item(item.parent)
            parent_key = str(item.parent.key)
        children = self.get_children(
            item=item.parent.key if item.parent is not None else None)
        index = self._determine_index_for_insert(item)
        if not self.exists(item.key):
            self.insert(parent_key, index, item.key,
                        text=item.name, values=self._additional_values(item))

    def _determine_index_for_insert(self, item):
        children = self.get_children(
            item=item.parent.key if item.parent is not None else None)
        index = 'end'
        for idx, child in enumerate(children):
            if self._is_less(item, child):
                index = idx
                break
        return index

    def get_all_items(self):
        """Provide all items currently in the tree.

        :return: list of all items (keys) in the tree.
        :rtype: [int]
        """
        all_items = []
        items = list(self.get_children())
        while len(items) > 0:
            item = items.pop()
            all_items.append(int(item))
            items.extend(self.get_children(item))
        return all_items

    def _is_less(self, item, key):
        """Is given item less than item by key?

        :param item: item to compare.
        :type item: Entity
        :param key: item identifier in tree.
        :type key: str
        :return: True if item is less
        :rtype: bool
        """
        raise NotImplementedError

    def _additional_values(self, item):
        """Provide a tuple with values to display in the tree."""
        raise NotImplementedError

    def selected_items(self):
        """Provide list of items selected in tree.

        :return: selected items
        :rtype: [Entity]
        """
        raise NotImplementedError


class FilteredTreeView(ttk.Frame):
    """Abstract filter_tree class."""

    def __init__(self, master, tree_factory):
        super().__init__(master)
        self.logger = logging.getLogger('picdb.ui')
        self.EVT_ITEM_SELECTED = '<<ItemSelected>>'
        self.supported_events = set()
        self.supported_events.add(self.EVT_ITEM_SELECTED)
        self.listeners = {}
        self.filter_frame = None
        self.tree = None
        self.tree_factory = tree_factory
        self.limit_default = 1000
        self.limit_entry = None
        self._create_widgets()
        self.tree.bind('<<TreeviewSelect>>', self._item_selected)

    def _create_widgets(self):
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self._create_filter_frame()
        self.filter_frame.grid(row=0, column=0,
                               sticky=(tk.W, tk.N, tk.E, tk.S))
        self.tree = self.tree_factory(self)
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

    def add_item_to_tree(self, item):
        """Add given item to tree view.

        :param item: item to add.
        :type item: Entity
        """
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
