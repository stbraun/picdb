# coding=utf-8
"""
Manage pictures via UI.
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

import os
import logging
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from PIL import Image

from .model import PictureReference
from . import persistence
from .uimasterdata import PicTreeView,  FilteredTreeview
from .uitags import TagSelector
from .uiseries import PictureSeriesSelector


class PictureManagement(ttk.Frame):
    """Provides UI for importing pictures."""

    def __init__(self, master):
        super().__init__(master, borderwidth=2, relief=tk.GROOVE)
        self.logger = logging.getLogger('picdb.ui')
        self.logger.info("Creating Picture Management UI")
        self.content_frame = None
        self.control_frame = None
        self.filter_tree = None
        self.editor = None
        self.edit_button = None
        self.view_button = None
        self.tag_selector = None
        self.series_selector = None
        self._create_widgets()

    def _create_widgets(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self._create_content_frame()
        self.content_frame.grid(row=0, column=0,
                                sticky=(tk.W, tk.N, tk.E, tk.S))
        self._create_control_frame()
        self.control_frame.grid(row=1, column=0,
                                sticky=(tk.W, tk.N, tk.E, tk.S))

    def _create_content_frame(self):
        self.content_frame = ttk.Frame(self)
        self.content_frame.rowconfigure(0, weight=1)
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(1, weight=1)
        self.filter_tree = PictureFilteredTreeview(self.content_frame)
        self.filter_tree.grid(row=0, column=0,
                              sticky=(tk.W, tk.N, tk.E, tk.S))
        self.filter_tree.bind(self.filter_tree.EVT_ITEM_SELECTED,
                              self.item_selected)
        self.editor = PictureMetadataEditor(self.content_frame)
        self.editor.grid(row=0, column=1,
                         sticky=(tk.W, tk.N, tk.E, tk.S))

    def _create_control_frame(self):
        self.control_frame = ttk.Frame(self, borderwidth=2, relief=tk.GROOVE)
        self.columnconfigure(0, weight=1)
        load_button = ttk.Button(self.control_frame, text='load pictures',
                                 command=self.load_pictures)
        load_button.grid(row=0, column=0, sticky=(tk.W, tk.N))
        add_button = ttk.Button(self.control_frame, text='add pictures',
                                command=self.import_pictures)
        add_button.grid(row=0, column=1, sticky=(tk.W, tk.N))
        self.view_button = ttk.Button(self.control_frame, text='view picture',
                                      command=self.view_picture)
        self.view_button.grid(row=0, column=3, sticky=(tk.W, tk.N))
        self.view_button.state(['disabled'])

    def load_pictures(self):
        """Load a bunch of pictures from database."""
        self.filter_tree.load_items()

    def import_pictures(self):
        """Let user select pictures and import them into database."""
        files = filedialog.askopenfilenames()
        self.logger.info('Files selected for import: {}'.format(files))
        pictures = [PictureReference(None, os.path.basename(pth), pth, None)
                    for pth in files]
        for picture in pictures:
            persistence.add_picture(picture)
            pic = persistence.retrieve_picture_by_path(picture.path)
            self.filter_tree.add_item_to_tree(pic)
            messagebox.showinfo(title='Picture Import',
                                message='{} pictures added.'.format(
                                    len(pictures)))

    def item_selected(self, _):
        """An item in the tree view was selected."""
        pics = self.filter_tree.selected_items()
        self.logger.info('Selected pictures: {}'.format(pics))
        if len(pics) > 0:
            self.view_button.state(['!disabled'])
            self.editor.load_picture(pics[0])

    def view_picture(self):
        """View selected picture."""
        pics = self.filter_tree.selected_items()
        if len(pics) > 0:
            image = Image.open(pics[0].path)
            image.show()


class PictureFilteredTreeview(FilteredTreeview):
    """Provide a picture tree and a selection panel."""

    def __init__(self, master):
        self.logger = logging.getLogger('picdb.ui')
        self.path_filter_var = tk.StringVar()
        self.limit_var = tk.IntVar()
        self.tag_selector = None
        self.series_selector = None
        super().__init__(master, PictureReferenceTree.create_instance)
        self.path_filter_var.set('%')
        self.path_filter_entry = None
        self.limit_var.set(self.limit_default)
        self.tag_selector.load_items([])
        self.series_selector.load_items([])

    def _create_widgets(self):
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self._create_filter_frame()
        self.series_selector = PictureSeriesSelector(self,
                                                     text='Select series')
        self.series_selector.grid(row=1, column=0,
                                  sticky=(tk.N, tk.S, tk.W, tk.E))
        self.tag_selector = TagSelector(self, text='Select tags')
        self.tag_selector.grid(row=2, column=0,
                               sticky=(tk.N, tk.S, tk.W, tk.E))
        self.filter_frame.grid(row=0, column=0,
                               sticky=(tk.W, tk.N, tk.E, tk.S))
        self.tree = self.tree_factory(self)
        self.tree.grid(row=0, column=1, rowspan=3,
                       sticky=(tk.W, tk.N, tk.E, tk.S))

    def _create_filter_frame(self):
        self.filter_frame = ttk.Frame(self)
        self.filter_frame.rowconfigure(0, weight=1)
        self.filter_frame.rowconfigure(1, weight=1)
        self.filter_frame.columnconfigure(0, weight=0)
        self.filter_frame.columnconfigure(1, weight=1)
        lbl_filter = ttk.Label(self.filter_frame, text='Filter on path')
        lbl_filter.grid(row=0, column=0, sticky=tk.E)
        self.path_filter_entry = ttk.Entry(self.filter_frame,
                                           textvariable=self.path_filter_var)
        self.path_filter_entry.grid(row=0, column=1, sticky=(tk.W, tk.E,))
        lbl_limit = ttk.Label(self.filter_frame, text='Max. number of records')
        lbl_limit.grid(row=1, column=0, sticky=tk.E)
        self.limit_entry = ttk.Entry(self.filter_frame,
                                     textvariable=self.limit_var,
                                     width=5,
                                     validate='focusout',
                                     validatecommand=self._validate_limit)
        self.limit_entry.grid(row=1, column=1, sticky=(tk.W,))

    def selected_items(self):
        """Provide list of pictures selected in tree.

        :return: selected pictures
        :rtype: list(PictureReference)
        """
        return self.tree.selected_items()

    def add_item_to_tree(self, picture: PictureReference):
        """Add given picture to tree view."""
        super().add_item_to_tree(picture)

    def _retrieve_items(self):
        """Retrieve a bunch of pictures from database.

        name_filter_var and limit_var are considered for retrieval.
        """
        name_filter = self.path_filter_var.get()
        limit = self.limit_var.get()
        series = self.series_selector.selected_items()
        tags = self.tag_selector.selected_items()
        pics = persistence.retrieve_filtered_pictures(name_filter,
                                                      limit,
                                                      series, tags)
        return pics


class PictureReferenceTree(PicTreeView):
    """A tree handling pictures."""

    def __init__(self, master, tree_only=False):
        self.tree_only = tree_only
        columns = () if tree_only else ('path', 'description')
        super().__init__(master, columns=columns)
        if not tree_only:
            self.heading('path', text='Path')
            self.heading('description', text='Description')
        self.column('#0', stretch=False)  # tree column shall not resize

    @classmethod
    def create_instance(cls, master, tree_only=False):
        """Factory method."""
        return PictureReferenceTree(master, tree_only)

    def _additional_values(self, item):
        return () if self.tree_only else (item.path, item.description)

    def selected_items(self):
        """Provide list of pictures selected in tree.

        :return: selected pictures
        :rtype: list(PictureReference)
        """
        item_ids = self.selection()
        pics = [persistence.retrieve_picture_by_key(int(pic_id))
                for pic_id in item_ids]
        return pics


class PictureReferenceEditor(ttk.LabelFrame):
    """Editor for PictureReference objects."""

    def __init__(self, master, text='Edit picture reference'):
        super().__init__(master, text=text)
        self.picture_ = None
        self.id_var = tk.IntVar()
        self.name_var = tk.StringVar()
        self.path_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        self.rowconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text='id').grid(row=0, column=0, sticky=tk.E)
        ttk.Label(self, text='name').grid(row=1, column=0, sticky=tk.E)
        ttk.Label(self, text='path').grid(row=2, column=0, sticky=tk.E)
        ttk.Label(self, text='description').grid(row=3, column=0, sticky=tk.E)
        ttk.Entry(self, textvariable=self.id_var,
                  state='readonly').grid(row=0, column=1, sticky=tk.W)
        ttk.Entry(self, textvariable=self.name_var).grid(row=1, column=1,
                                                         sticky=(tk.E, tk.W))
        ttk.Entry(self, textvariable=self.path_var).grid(row=2, column=1,
                                                         sticky=(tk.E, tk.W))
        ttk.Entry(self,
                  textvariable=self.description_var).grid(row=3,
                                                          column=1,
                                                          sticky=(tk.E, tk.W))

    @property
    def picture(self):
        if self.picture_ is not None:
            self.picture_.id = self.id_var.get()
            self.picture_.name = self.name_var.get()
            self.picture_.path = self.path_var.get()
            self.picture_.description = self.description_var.get()
        return self.picture_

    @picture.setter
    def picture(self, pic: PictureReference):
        self.picture_ = pic
        self.id_var.set(pic.key)
        self.name_var.set(pic.name)
        self.path_var.set(pic.path)
        self.description_var.set(pic.description)


class PictureMetadataEditor(ttk.Frame):
    """Editor component for picture meta data."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.content_frame = None
        self.control_frame = None
        self.tag_selector = None
        self.series_selector = None
        self.editor = None
        self.save_button = None
        self.picture = None
        self._create_widgets()

    def _create_widgets(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self._create_content(self)
        self.content_frame.grid(row=0, column=0,
                                sticky=(tk.W, tk.N, tk.E, tk.S))
        self._create_control_frame(self)
        self.control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

    def _create_content(self, master):
        self.content_frame = ttk.Frame(master)
        self.content_frame.rowconfigure(0, weight=0)
        self.content_frame.rowconfigure(1, weight=1)
        self.content_frame.rowconfigure(2, weight=1)
        self.content_frame.columnconfigure(0, weight=1)
        self.editor = PictureReferenceEditor(self.content_frame)
        self.editor.grid(row=0, column=0, sticky=(tk.N, tk.E, tk.W))
        self.series_selector = PictureSeriesSelector(self.content_frame,
                                                     text='Assign series')
        self.series_selector.grid(row=1, column=0,
                                  sticky=(tk.W, tk.N, tk.E, tk.S))
        self.tag_selector = TagSelector(self.content_frame, text='Assign tags')
        self.tag_selector.grid(row=2, column=0,
                               sticky=(tk.W, tk.N, tk.E, tk.S))

    def _create_control_frame(self, master):
        self.control_frame = ttk.Frame(master)
        self.columnconfigure(0, weight=1)
        self.save_button = ttk.Button(self.control_frame, text='save',
                                      command=self._save)
        self.save_button.grid(row=0, column=0)
        cancel_button = ttk.Button(self.control_frame, text='close',
                                   command=self._close)
        cancel_button.grid(row=0, column=1)

    def _save(self):
        """Save current picture."""
        self.picture = self.editor.picture
        persistence.update_picture(self.picture)
        self._update_tags()
        self._update_series()

    def _update_tags(self):
        """Remove and add tags according to changes made during editing."""
        pic_tags = set(self.picture.tags)
        edt_tags = set(self.tag_selector.selected_items())
        tags_to_add = edt_tags.difference(pic_tags)
        tags_to_remove = pic_tags.difference(edt_tags)
        persistence.add_tags_to_picture(self.picture, tags_to_add)
        persistence.remove_tags_from_picture(self.picture, tags_to_remove)
        self.picture.tags = edt_tags

    def _update_series(self):
        """Remove and add series according to changes made during editing."""
        pic_series = set(self.picture.series)
        edt_series = set(self.series_selector.selected_items())
        series_to_add = edt_series.difference(pic_series)
        series_to_remove = pic_series.difference(edt_series)
        persistence.add_picture_to_set_of_series(self.picture, series_to_add)
        persistence.remove_picture_from_set_of_series(self.picture,
                                                      series_to_remove)
        self.picture.series = edt_series

    def _close(self):
        """Close editor."""
        self.master.destroy()

    def load_picture(self, picture: PictureReference):
        """Load picture into editor."""
        self.picture = picture
        self.editor.picture = picture
        self.tag_selector.load_items(picture.tags)
        self.series_selector.load_items(picture.series)
