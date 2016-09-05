# coding=utf-8
"""
A component for moving items between two tree views.
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

import tkinter as tk
from tkinter import ttk
import logging

from .model import Entity


class Selector(ttk.LabelFrame):
    """A component for moving items between two tree views."""
    def __init__(self, master, tree_factory_left,
                 tree_factory_right, **kwargs):
        super().__init__(master, **kwargs)
        self.logger = logging.getLogger('picdb.ui')
        self.tree_factory_left = tree_factory_left
        self.tree_factory_right = tree_factory_right
        self.left = None
        self.right = None
        self.control_frame = None
        self.add_button = None
        self.remove_button = None
        self._create_widgets()

    def _create_widgets(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)
        self.left = self.tree_factory_left(self, tree_only=True)
        self.left.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.right = self.tree_factory_right(self, tree_only=True)
        self.right.grid(row=0, column=2, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.control_frame = self._create_control_frame()
        self.control_frame.grid(row=0, column=1)

    def _create_control_frame(self):
        frame = ttk.Frame(self)
        self.add_button = ttk.Button(frame, text='>',
                                     command=self._add_item,
                                     width=1)
        self.add_button.grid(row=0, column=0)
        self.remove_button = ttk.Button(frame, text='<',
                                        command=self._remove_item,
                                        width=1)
        self.remove_button.grid(row=1, column=0)
        return frame

    def _add_item(self):
        items = self.left.selected_items()
        self.logger.info('add item: {}'.format(items))
        for item in items:
            self.left.delete(item.key)
            self.right.add_item(item)

    def _remove_item(self):
        items = self.right.selected_items()
        self.logger.info('remove item: {}'.format(items))
        for item in items:
            self.right.delete(item.key)
            self.left.add_item(item)

    def init_trees(self, all_entities, right_entities):
        """Write given entities into left tree."""
        left_entities = list(set(all_entities).difference(set(right_entities)))
        self.clear()
        left_entities.sort()
        right_entities = list(right_entities)
        right_entities.sort()
        for entity in left_entities:
            self.left.add_item(entity)
        for entity in right_entities:
            self.right.add_item(entity)

    def clear(self):
        """Clear selector."""
        self.left.clear()
        self.right.clear()

    def selected_items(self):
        """Return the selected items."""
        raise NotImplementedError

    def load_items(self, items):
        """Load initial items into tree views.

        :param items: entities to display in right tree.
        :type items: [Entity]
        """
        raise NotImplementedError
