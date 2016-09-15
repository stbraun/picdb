# coding=utf-8
"""
Series management.
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

import logging
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from . import group
from .group import Group
from .uimasterdata import HierarchicalTreeView, FilteredTreeView
from .selector import Selector
from .uicommon import tag_all_children
from .persistence import UnknownEntityException


class GroupManagement(ttk.Frame):
    """Manage picture series master data."""

    def __init__(self, master):
        super().__init__(master)
        self.logger = logging.getLogger('picdb.ui')
        self.logger.info("Creating GroupManagement UI")
        self.content_frame = None
        self.control_frame = None
        self.filter_tree = None
        self.editor = None
        self.create_widgets()
        self.bind('<Meta_L>s', self._save_group)
        self.bind('<Meta_L>n', self._add_group)
        # add key bindings: use self as (tk-)tag to bind a listener also to all
        # children widgets
        tag_all_children(self, self)
        self.bind('<Meta_L>s', self._save_group)
        self.bind('<Meta_L>n', self._add_group)
        # finally load tags into the tree
        self.load_groups()

    def _save_group(self, _):
        self.save_group()
        return "break"

    def _add_group(self, _):
        self.add_group()
        return "break"

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
        self.filter_tree = GroupFilteredTreeView(self.content_frame)
        self.filter_tree.grid(row=0, column=0,
                              sticky=(tk.W, tk.N, tk.E, tk.S))
        self.filter_tree.bind(self.filter_tree.EVT_ITEM_SELECTED,
                              self.item_selected)
        self.editor = GroupEditor(self.content_frame)
        self.editor.grid(row=0, column=1, sticky=(tk.N, tk.E, tk.W))

    def create_control_frame(self):
        """Create the control frame.

        :return: control frame
        :rtype: ttk.Frame
        """
        self.control_frame = ttk.Frame(self, borderwidth=2, relief=tk.GROOVE)
        self.control_frame.grid(row=1, column=0,
                                sticky=(tk.W, tk.N, tk.E, tk.S))
        self.columnconfigure(0, weight=1)
        load_button = ttk.Button(self.control_frame, text='load series',
                                 command=self.load_groups)
        load_button.grid(row=0, column=0, sticky=(tk.W, tk.N))
        add_button = ttk.Button(self.control_frame, text='add series',
                                command=self.add_group)
        add_button.grid(row=0, column=1, sticky=(tk.W, tk.N))
        save_button = ttk.Button(self.control_frame, text='save series',
                                 command=self.save_group)
        save_button.grid(row=0, column=2, sticky=(tk.W, tk.N))

    def load_groups(self):
        """Load a bunch of groups from database."""
        self.filter_tree.load_items()

    def add_group(self):
        """Push an empty group to editor."""
        group_ = Group(None, '', '', None)
        self.editor.group = group_

    def save_group(self):
        """Save the group currently in editor."""
        group_ = self.editor.group
        if group_ is not None:
            group_.save()
        self.load_groups()
        self.editor.group = group.retrieve_series_by_name(group_.name)

    def item_selected(self, _):
        """An item in the tree view was selected."""
        items = self.filter_tree.selected_items()
        if len(items) > 0:
            group_ = items[0]
            # This loads the pictures for this group. Just to be sure that save
            # will work.
            # As soon as we can edit the pictures of a group here we will need
            # this cll anyway.
            _ = group_.pictures
            self.editor.group = group_


class GroupFilteredTreeView(FilteredTreeView):
    """Provide a group tree and selection panel."""

    def __init__(self, master):
        self.logger = logging.getLogger('picdb.ui')
        self.name_filter_var = tk.StringVar()
        self.limit_var = tk.IntVar()
        super().__init__(master, GroupTree.create_instance)
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
        """Provide list of groups selected in tree.

        :return: selected groups
        :rtype: [Group]
        """
        return self.tree.selected_items()

    def add_item_to_tree(self, group_):
        """Add given group to tree view.

        :param group_: group to add.
        :type group_: Group
        """
        super().add_item_to_tree(group_)

    def _retrieve_items(self):
        """Retrieve a bunch of groups from database.

        name_filter_var and limit_var are considered for retrieval.

        :return: groups as selected by filter criteria.
        :rtype: [Group]
        """
        name_filter = self.name_filter_var.get()
        limit = self.limit_var.get()
        groups = group.retrieve_series_by_name_segment(name_filter,
                                                       limit)
        return groups


class GroupTree(HierarchicalTreeView):
    """A tree handling picture groups."""

    def __init__(self, master, tree_only=False, **kwargs):
        self.tree_only = tree_only
        columns = () if tree_only else ('description',)
        super().__init__(master, columns=columns, **kwargs)
        if not tree_only:
            self.heading('description', text='Description')

    @classmethod
    def create_instance(cls, master, tree_only=False, **kwargs):
        """Factory method."""
        return GroupTree(master, tree_only, **kwargs)

    def add_item(self, group_):
        """Add given group to tree.

        :param group_: group to add
        :type group_: Group
        """
        super().add_item(group_)

    def _additional_values(self, item):
        return () if self.tree_only else (item.description,)

    def selected_items(self):
        """Provide list of groups selected in tree.

        :return: selected group
        :rtype: [Group]
        """
        item_ids = self.selection()
        series = [group.retrieve_series_by_key(int(item_id))
                  for item_id in item_ids]
        return series

    def _is_less(self, item, key):
        return item.name < group.retrieve_series_by_key(int(key)).name

    def _dnd_action(self, start_item, target_item):
        """Set target_item as parent of start_item.

        :param start_item: item which is dragged
        :type start_item: str
        :param target_item: item to drop on
        :type target_item: str
        """
        try:
            start_item_ = group.retrieve_series_by_key(int(start_item))
            target_item_ = group.retrieve_series_by_key(int(target_item))
        except UnknownEntityException:
            messagebox.showwarning(
                "Invalid items for drag 'n' drop: {} --> {}".format(start_item,
                                                                    target_item))
        else:
            start_item_.parent = target_item_
            index = self._determine_index_for_insert(start_item_)
            self.move(start_item, target_item, index)
            start_item_.save()

    def _delete_items(self, items):
        """Delete given groups.

        :param items: groups to delete.
        :type items: [Group]
        """
        for group_ in items:
            group_.delete()


class GroupEditor(ttk.LabelFrame):
    """Editor for Group objects."""

    def __init__(self, master, text='Edit series'):
        super().__init__(master, text=text)
        self.group_ = None
        self.id_var = tk.IntVar()
        self.name_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.name_entry = None
        self.create_widgets()

    def create_widgets(self):
        self.rowconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text='id').grid(row=0, column=0, sticky=tk.E)
        ttk.Label(self, text='name').grid(row=1, column=0, sticky=tk.E)
        ttk.Label(self, text='description').grid(row=2, column=0, sticky=tk.E)
        ttk.Entry(self, textvariable=self.id_var,
                  state='readonly').grid(row=0, column=1, sticky=tk.W)
        self.name_entry = ttk.Entry(self, textvariable=self.name_var)
        self.name_entry.grid(row=1, column=1, sticky=(tk.E, tk.W))
        ttk.Entry(self,
                  textvariable=self.description_var).grid(row=2,
                                                          column=1,
                                                          sticky=(tk.E, tk.W))
        ttk.Button(self, text='Unlink from parent',
                   command=self._unlink_from_parent).grid(row=3, column=1,
                                                          sticky=tk.W)

    @property
    def group(self):
        if self.group_ is not None:
            self.group_.name = self.name_var.get()
            self.group_.description = self.description_var.get()
        return self.group_

    @group.setter
    def group(self, group_):
        self.group_ = group_
        self.id_var.set(group_.key)
        self.name_var.set(group_.name)
        self.description_var.set(group_.description)
        self.name_entry.focus()

    def _unlink_from_parent(self):
        """Unlink group from parent group."""
        if self.group is not None:
            self.group.parent = None


class GroupSelector(Selector):
    """Provide a selector component for groups."""

    def __init__(self, master, **kwargs):
        super().__init__(master, GroupTree.create_instance,
                         GroupTree.create_instance,
                         **kwargs)

    def selected_items(self):
        """Get selected groups.

        :return: selected groups
        :rtype: [Group]
        """
        items = self.right.get_all_items()
        groups = [group.retrieve_series_by_key(int(item))
                  for item in items]
        return groups

    def load_items(self, picture_groups):
        """Load items into selector.

        :param picture_groups: list of groups already assigned to picture.
        :type picture_groups: [Group]
        """
        groups = group.get_all_series()
        self.init_trees(groups, picture_groups)
