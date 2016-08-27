# coding=utf-8
"""
Import pictures via UI.
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
from .persistence import get_db
from .uimasterdata import PicTreeView


class PictureImporter(ttk.Frame):
    """Provides UI for importing pictures."""

    def __init__(self, master):
        super().__init__(master, borderwidth=2, relief=tk.GROOVE)
        self.logger = logging.getLogger('picdb.ui')
        self.content_frame = None
        self.control_frame = None
        self.pic_selector = None
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
        self.content_frame = ttk.Frame(self)
        self.content_frame.rowconfigure(0, weight=1)
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(1, weight=1)
        self.pic_selector = PictureSelector(self.content_frame)
        self.pic_selector.grid(row=0, column=0,
                               sticky=(tk.W, tk.N, tk.E, tk.S))
        self.pic_selector.bind(self.pic_selector.EVT_PICTURE_SELECTED,
                               self.item_selected)
        self.editor = PictureReferenceEditor(self.content_frame)
        self.editor.grid(row=0, column=1, sticky=(tk.N, tk.E, tk.W))

    def create_control_frame(self):
        self.control_frame = ttk.Frame(self, borderwidth=2, relief=tk.GROOVE)
        self.columnconfigure(0, weight=1)
        load_button = ttk.Button(self.control_frame, text='load pictures',
                                 command=self.load_pictures)
        load_button.grid(row=0, column=0, sticky=(tk.W, tk.N))
        add_button = ttk.Button(self.control_frame, text='add pictures',
                                command=self.add_pictures)
        add_button.grid(row=0, column=1, sticky=(tk.W, tk.N))
        save_button = ttk.Button(self.control_frame, text='save picture',
                                 command=self.save_picture)
        save_button.grid(row=0, column=2, sticky=(tk.W, tk.N))
        view_button = ttk.Button(self.control_frame, text='view picture',
                                 command=self.view_picture)
        view_button.grid(row=0, column=3, sticky=(tk.W, tk.N))

    def load_pictures(self):
        """Load a bunch of pictures from database.
        """
        self.pic_selector.load_pictures()

    def add_pictures(self):
        """Let user select pictures and import them into database."""
        files = filedialog.askopenfilenames()
        self.logger.info('Files selected for import: {}'.format(files))
        pictures = [PictureReference(None, os.path.basename(pth), pth, None)
                    for pth in files]
        db = get_db()
        for picture in pictures:
            db.add_picture(picture)
            pic = db.retrieve_picture_by_path(picture.path)
            self.pic_selector.add_picture_to_tree(pic)
        messagebox.showinfo(title='Picture Import',
                            message='{} pictures added.'.format(len(pictures)))

    def save_picture(self):
        """Save the picture currently in editor."""
        pic = self.editor.picture
        if pic is not None:
            db = get_db()
            db.update_picture(pic)

    def item_selected(self, _):
        """An item in the tree view was selected."""
        pics = self.pic_selector.selected_pictures()
        self.logger.info('Selected pictures: {}'.format(pics))
        if len(pics) > 0:
            pic = pics[0]
            self.logger.info('Pic: {}'.format(pic))
            self.editor.picture = pic

    def view_picture(self):
        """View selected picture."""
        pics = self.pic_selector.selected_pictures()
        if len(pics) > 0:
            image = Image.open(pics[0].path)
            image.show()


class PictureSelector(ttk.Frame):
    """Provide a picture tree and a slection panel."""

    def __init__(self, master):
        super().__init__(master)
        self.logger = logging.getLogger('picdb.ui')
        self.EVT_PICTURE_SELECTED = '<<<PictureSelected>>>'
        self.supported_events = {self.EVT_PICTURE_SELECTED}
        self.listeners = {}
        self.filter_frame = None
        self.tree = None
        self.path_filter_var = tk.StringVar()
        self.path_filter_var.set('%')
        self.path_filter_entry = None
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
        self.tree = PictureReferenceTree(self)
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
        self.path_filter_entry = ttk.Entry(self.filter_frame,
                                           textvariable=self.path_filter_var)
        self.path_filter_entry.grid(row=0, column=1, sticky=(tk.W, tk.E,))
        lbl_limit = ttk.Label(self.filter_frame, text='Max. number of records')
        lbl_limit.grid(row=1, column=0, sticky=tk.E)
        self.limit_entry = ttk.Entry(self.filter_frame,
                                     textvariable=self.limit_var,
                                     width=5)
        self.limit_entry.grid(row=1, column=1, sticky=(tk.W,))

    def selected_pictures(self):
        """Provide list of pictures selected in tree.

        :return: selected pictures
        :rtype: list(PictureReference)
        """
        pic_ids = self.tree.selection()
        db = get_db()
        pics = [db.retrieve_picture_by_key(pic_id) for pic_id in pic_ids]
        self.logger.info('Selected pictures: {}'.format(pics))
        return pics

    def __item_selected(self, event):
        """An item in the tree view was selected."""
        pics = self.tree.selection()
        self.logger.info('Selected pictures: {}'.format(pics))
        if len(pics) > 0:
            db = get_db()
            pic = db.retrieve_picture_by_key(pics[0])
            self.logger.info('Pic: {}'.format(pic))
            if self.EVT_PICTURE_SELECTED in self.listeners.keys():
                listener = self.listeners[self.EVT_PICTURE_SELECTED]
                listener(event)

    def load_pictures(self):
        """Load a bunch of pictures from database.

        filter_path_var and limit_var are considered for retrieval.
        """
        self.tree.clear()
        db = get_db()
        path_filter = self.path_filter_var.get()
        limit = self.limit_var.get()
        pictures = db.retrieve_pictures_by_path_segment(path_filter, limit)
        for picture in pictures:
            self.tree.add_picture(picture)

    def add_picture_to_tree(self, picture: PictureReference):
        """Add given picture to tree view."""
        self.tree.add_picture(picture)

    def bind(self, sequence=None, func=None, add=None):
        """Bind to this widget at event SEQUENCE a call to function FUNC."""
        if sequence in self.supported_events:
            self.logger.info('Binding {} to {}'.format(func,
                                                       self.EVT_PICTURE_SELECTED))
            self.listeners[sequence] = func
        else:
            super().bind(sequence, func, add)


class PictureReferenceTree(PicTreeView):
    """A tree handling pictures."""

    def __init__(self, master):
        super().__init__(master, columns=('path', 'description'))
        self.heading('path', text='Path')
        self.heading('description', text='Description')
        self.column('#0', stretch=False)  # tree column does not resize

    def add_picture(self, picture: PictureReference):
        """Add given picture to tree."""
        self.insert('', 'end', picture.key,
                    text=picture.name,
                    values=(picture.path, picture.description))


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
