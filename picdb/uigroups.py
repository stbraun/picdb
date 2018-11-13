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
from tkinter import messagebox
from tkinter import ttk

from .groupservices import retrieve_groups_by_name, delete_group, \
    retrieve_groups_by_name_segment, retrieve_group_by_key, get_all_groups, \
    save_group as save_group_, create_group
from .persistence import UnknownEntityException
from .selector import Selector
from .uicommon import tag_all_children
from .uimasterdata import HierarchicalTreeView, FilteredTreeView


class GroupManagement(ttk.Frame):
    """Manage picture groups master data."""

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
        """Create the widgets for the view."""
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
        self.filter_tree.bind(self.filter_tree.EVT_ITEM_DELETED,
                              self._item_deleted)
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
        load_button = ttk.Button(self.control_frame, text='load groups',
                                 command=self.load_groups)
        load_button.grid(row=0, column=0, sticky=(tk.W, tk.N))
        add_button = ttk.Button(self.control_frame, text='add group',
                                command=self.add_group)
        add_button.grid(row=0, column=1, sticky=(tk.W, tk.N))
        save_button = ttk.Button(self.control_frame, text='save group',
                                 command=self.save_group)
        save_button.grid(row=0, column=2, sticky=(tk.W, tk.N))

    def load_groups(self):
        """Load a bunch of groups from database."""
        self.filter_tree.load_items()

    def add_group(self):
        """Push an empty group to editor."""
        group_ = create_group(None, '', '')
        self.editor.group = group_

    def save_group(self):
        """Save the group currently in editor."""
        group_ = self.editor.group
        if group_ is not None:
            save_group_(group_)
        self.load_groups()  # refresh tree
        groups = retrieve_groups_by_name(group_.name)
        for grp in groups:
            if self.editor.group.parent == grp.parent:
                self.editor.group = grp
                break

    def item_selected(self, _):
        """An item in the tree view was selected."""
        items = self.filter_tree.selected_items()
        if items:
            group_ = items[0]
            # This loads the pictures for this group. Just to be sure that save
            # will work.
            # As soon as we can edit the pictures of a group here we will need
            # this call anyway.
            pics = group_.pictures
            self.logger.debug('Pictures of group %s: %s.', group_.name,
                              str(pics))
            self.editor.group = group_

    def _item_deleted(self, _):
        """An item was deleted. Clear editor."""
        self.editor.clear()


class GroupFilteredTreeView(FilteredTreeView):
    """Provide a group tree and selection panel."""

    def __init__(self, master, **kwargs):
        self.logger = logging.getLogger('picdb.ui')
        self.name_filter_var = tk.StringVar()
        self.limit_var = tk.IntVar()
        super().__init__(master, GroupTree.create_instance_change_parent,
                         **kwargs)
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

    def _retrieve_items(self):
        """Retrieve a bunch of groups from database.

        name_filter_var and limit_var are considered for retrieval.

        :return: groups as selected by filter criteria.
        :rtype: [Group]
        """
        name_filter = self.name_filter_var.get()
        limit = self.limit_var.get()
        groups = retrieve_groups_by_name_segment(name_filter, limit)
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

    @classmethod
    def create_instance_change_parent(cls, master, tree_only=False, **kwargs):
        """Factory method."""
        return GroupTree(master, tree_only, allow_change_parent=True, **kwargs)

    def _additional_values(self, item):
        return () if self.tree_only else (item.description,)

    def selected_items(self):
        """Provide list of groups selected in tree.

        :return: selected group
        :rtype: [Group]
        """
        item_ids = self.selection()
        groups = [retrieve_group_by_key(int(item_id))
                  for item_id in item_ids]
        return groups

    def _is_less(self, item, key):
        return item.name < retrieve_group_by_key(int(key)).name

    def _dnd_action(self, start_item, target_item):
        """Set target_item as parent of start_item.

        :param start_item: item which is dragged
        :type start_item: str
        :param target_item: item to drop on
        :type target_item: str
        """
        try:
            start_item_ = retrieve_group_by_key(int(start_item))
            target_item_ = retrieve_group_by_key(int(target_item))
        except UnknownEntityException:
            msg_tmpl = "Invalid items for drag 'n' drop: {} --> {}"
            messagebox.showwarning(
                msg_tmpl.format(start_item, target_item))
        except ValueError:
            # This will be raised if an item was dropped outside the tree view.
            # We tolerate this as cancel dragging.
            pass
        else:
            start_item_.parent = target_item_
            index = self._determine_index_for_insert(start_item_)
            self.move(start_item, target_item, index)
            save_group_(start_item_)

    def _delete_items(self, items):
        """Delete given groups.

        :param items: groups to delete.
        :type items: [Group]
        """
        for group_ in items:
            delete_group(group_)

    def _unlink_from_parent(self):
        """Unlink selected groups from parent group."""
        groups = self.selected_items()
        for group_ in groups:
            group_.parent = None
            save_group_(group_)
            index = self._determine_index_for_insert(group_)
            self.move(group_.key, '', index)


class GroupEditor(ttk.LabelFrame):
    """Editor for Group objects."""

    def __init__(self, master, text='Edit group'):
        super().__init__(master, text=text)
        self.group_ = None
        self.id_var = tk.IntVar()
        self.name_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.name_entry = None
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the view."""
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

    @property
    def group(self):
        """Update group with values from editor and return it."""
        if self.group_ is not None:
            self.group_.name = self.name_var.get()
            self.group_.description = self.description_var.get()
        return self.group_

    @group.setter
    def group(self, group_):
        """Put group attributes into editor or create a new group object if
        group_ is None."""
        self.group_ = group_
        if group_ is None:
            self.id_var.set(0)
            self.name_var.set('')
            self.description_var.set('')
        else:
            self.id_var.set(group_.key)
            self.name_var.set(group_.name)
            self.description_var.set(group_.description)
        self.name_entry.focus()

    def clear(self):
        """Remove group from editor."""
        self.group_ = None


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
        groups = [retrieve_group_by_key(int(item))
                  for item in items]
        return groups

    def load_items(self, picture_groups):
        """Load items into selector.

        :param picture_groups: list of groups already assigned to picture.
        :type picture_groups: [Group]
        """
        groups = get_all_groups()
        self.init_trees(groups, picture_groups)
