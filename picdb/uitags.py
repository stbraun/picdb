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
from tkinter import messagebox

from . import tag
from .tag import Tag
from .uimasterdata import HierarchicalTreeView, FilteredTreeView
from .selector import Selector
from .uicommon import tag_all_children
from .persistence import UnknownEntityException
from . import picture


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
        # add key bindings: use self as (tk-)tag to bind a listener also to all
        # children widgets
        tag_all_children(self, self)
        self.bind('<Meta_L>s', self._save_tag)
        self.bind('<Meta_L>n', self._add_tag)
        # finally load tags into the tree
        self.load_tags()

    def _save_tag(self, _):
        self.save_tag()
        return "break"

    def _add_tag(self, _):
        self.add_tag()
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
        self.filter_tree = TagFilteredTreeView(self.content_frame)
        self.filter_tree.grid(row=0, column=0,
                              sticky=(tk.W, tk.N, tk.E, tk.S))
        self.filter_tree.bind(self.filter_tree.EVT_ITEM_SELECTED,
                              self.item_selected)
        self.filter_tree.bind(self.filter_tree.EVT_ITEM_DELETED,
                              self._item_deleted)
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
        tag_ = Tag(None, '', '')
        self.editor.tag = tag_

    def save_tag(self):
        """Save the tag currently in editor."""
        tag_ = self.editor.tag
        if tag_ is not None:
            tag_.save()
        self.load_tags()
        self.editor.tag = tag.retrieve_tag_by_name(tag_.name)

    def item_selected(self, _):
        """An item in the tree view was selected."""
        items = self.filter_tree.selected_items()
        self.logger.info('Selected tags: {}'.format(items))
        if len(items) > 0:
            tag = items[0]
            self.editor.tag = tag

    def _item_deleted(self, _):
        """An item was deleted. Clear editor."""
        self.editor.clear()


class TagFilteredTreeView(FilteredTreeView):
    """Provide a tag tree and selection panel."""

    def __init__(self, master, **kwargs):
        self.logger = logging.getLogger('picdb.ui')
        self.name_filter_var = tk.StringVar()
        self.limit_var = tk.IntVar()
        super().__init__(master, TagTree.create_instance_change_parent,
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
        """Provide list of tags selected in tree.

        :return: selected tags
        :rtype: list(Tag)
        """
        return self.tree.selected_items()

    def add_item_to_tree(self, tag):
        """Add given tag to tree view."""
        super().add_item_to_tree(tag)

    def _retrieve_items(self):
        """Retrieve a bunch of tags from database.

        name_filter_var and limit_var are considered for retrieval.
        """
        name_filter = self.name_filter_var.get()
        limit = self.limit_var.get()
        tags = tag.retrieve_tags_by_name_segment(name_filter, limit)
        return tags


class TagTree(HierarchicalTreeView):
    """A tree handling tags."""

    def __init__(self, master, tree_only=False, **kwargs):
        self.tree_only = tree_only
        columns = () if tree_only else ('description',)
        super().__init__(master, columns=columns, **kwargs)
        if not tree_only:
            self.heading('description', text='Description')

    @classmethod
    def create_instance(cls, master, tree_only=False, **kwargs):
        """Factory method."""
        return TagTree(master, tree_only, **kwargs)

    @classmethod
    def create_instance_change_parent(cls, master, tree_only=False, **kwargs):
        """Factory method."""
        return TagTree(master, tree_only, allow_change_parent=True, **kwargs)

    def add_item(self, tag_):
        """Add given tag to tree.

        :param tag_: tag to add.
        :type tag_: Tag
        """
        super().add_item(tag_)

    def _additional_values(self, item):
        return () if self.tree_only else (item.description,)

    def selected_items(self):
        """Provide list of tags selected in tree.

        :return: selected tags
        :rtype: list(Tag)
        """
        item_ids = self.selection()
        tags = [tag.retrieve_tag_by_key(int(item_id))
                for item_id in item_ids]
        return tags

    def _is_less(self, item, key):
        return item.name < tag.retrieve_tag_by_key(int(key)).name

    def _dnd_action(self, start_item, target_item):
        """Set target_item as parent of start_item.

        :param start_item: item which is dragged
        :type start_item: str
        :param target_item: item to drop on
        :type target_item: str
        """
        try:
            start_item_ = tag.retrieve_tag_by_key(int(start_item))
            target_item_ = tag.retrieve_tag_by_key(int(target_item))
        except UnknownEntityException:
            messagebox.showwarning(
                "Invalid items for drag 'n' drop: {} --> {}".format(start_item,
                                                                    target_item))
        except ValueError:
            # This will be raised if an item was dropped outside the tree view.
            # We tolerate this as cancel dragging.
            pass
        else:
            start_item_.parent = target_item_
            index = self._determine_index_for_insert(start_item_)
            self.move(start_item, target_item, index)
            start_item_.save()

    def _delete_items(self, items):
        """Delete given tags.

        :param items: tags to delete.
        :type items: [Tag]
        """
        for tag_ in items:
            pics = picture.retrieve_pictures_by_tag(tag_)
            for pic in pics:
                pic.remove_tag(tag_)
                pic.save()
            tag_.delete()

    def _unlink_from_parent(self):
        """Unlink selected tag from parent tag."""
        tags = self.selected_items()
        for tag_ in tags:
            tag_.parent = None
            tag_.save()
            index = self._determine_index_for_insert(tag_)
            self.move(tag_.key, '', index)


class TagEditor(ttk.LabelFrame):
    """Editor for Tag objects."""

    def __init__(self, master, text='Edit tag'):
        super().__init__(master, text=text)
        self.tag_ = None
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
    def tag(self):
        if self.tag_ is not None:
            self.tag_.name = self.name_var.get()
            self.tag_.description = self.description_var.get()
        return self.tag_

    @tag.setter
    def tag(self, tag_):
        self.tag_ = tag_
        if tag_ is None:
            self.id_var.set(0)
            self.name_var.set('')
            self.description_var.set('')
        else:
            self.id_var.set(tag_.key)
            self.name_var.set(tag_.name)
            self.description_var.set(tag_.description)
        self.name_entry.focus()

    def _unlink_from_parent(self):
        """Unlink tag from parent tag."""
        if self.tag is not None:
            self.tag.parent = None
            self.tag.save()

    def clear(self):
        self.tag = None


class TagSelector(Selector):
    """Provide a selector component for tags."""

    def __init__(self, master, **kwargs):
        super().__init__(master, TagTree.create_instance,
                         TagTree.create_instance, **kwargs)

    def selected_items(self):
        """Get selected tags.

        :return: selected tags
        :rtype: [Tag]
        """
        items = self.right.get_all_items()
        tags = [tag.retrieve_tag_by_key(int(item)) for item in items]
        return tags

    def load_items(self, picture_tags):
        """Load items into selector.

        :param picture_tags: list of tags already assigned to picture.
        :type picture_tags: [Tag]
        """
        all_tags = tag.get_all_tags()
        self.init_trees(all_tags, picture_tags)
