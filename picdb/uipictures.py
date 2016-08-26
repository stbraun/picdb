# coding=utf-8
"""
Import pictures via UI.
"""
# Copyright (c) 2016 Stefan Braun
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
# AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
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
from .uimasterdata import PictureReferenceEditor, PictureReferenceTree


class PictureImporter(ttk.Frame):

    """Provides UI for importing pictures."""

    def __init__(self, master):
        super().__init__(master, borderwidth=2, relief=tk.GROOVE)
        self.logger = logging.getLogger('picdb.ui')
        self.content_frame = None
        self.control_frame = None
        self.tree = None
        self.path_filter_var = tk.StringVar()
        self.path_filter_var.set('%')
        self.path_filter_entry = None
        self.limit_var = tk.IntVar()
        self.limit_var.set(50)
        self.limit_entry = None
        self.editor = None
        self.create_widgets()

    def create_widgets(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.create_content_frame()
        self.create_control_frame()

    def create_content_frame(self):
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=0, column=0,
                                sticky=(tk.W, tk.N, tk.E, tk.S))
        self.content_frame.rowconfigure(1, weight=0)
        self.content_frame.rowconfigure(2, weight=1)
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(1, weight=0)
        self.path_filter_entry = ttk.Entry(self.content_frame,
                                           textvariable=self.path_filter_var)
        self.path_filter_entry.grid(row=0, column=0, sticky=(tk.N, ))
        self.limit_entry = ttk.Entry(self.content_frame,
                                     textvariable=self.limit_var)
        self.limit_entry.grid(row=1, column=0, sticky=(tk.N, ))
        self.tree = PictureReferenceTree(self.content_frame)
        self.tree.bind('<<TreeviewSelect>>', self.item_selected)
        self.tree.grid(row=2, column=0,
                       sticky=(tk.W, tk.N, tk.E, tk.S))
        self.editor = PictureReferenceEditor(self.content_frame)
        self.editor.grid(row=2, column=1, sticky=(tk.N, tk.E, tk.W))

    def create_control_frame(self):
        self.control_frame = ttk.Frame(self, borderwidth=2, relief=tk.GROOVE)
        self.control_frame.grid(row=1, column=0,
                                sticky=(tk.W, tk.N, tk.E, tk.S))
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

        filter_path_var and limit_var are considered for retrieval.
        """
        self.tree.clear()
        db = get_db()
        path_filter = self.path_filter_var.get()
        limit = self.limit_var.get()
        pictures = db.retrieve_pictures_by_path_segment(path_filter, limit)
        for picture in pictures:
            self.tree.add_picture(picture)

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
            self.tree.add_picture(pic)
        messagebox.showinfo(title='Picture Import',
                            message='{} pictures imported.'.format(len(pictures)))

    def save_picture(self):
        """Save the picture currently in editor."""
        pic = self.editor.picture
        if pic is not None:
            db = get_db()
            db.update_picture(pic)

    def item_selected(self, _):
        """An item in the tree view was selected."""
        pics = self.tree.selection()
        self.logger.info('Selected pictures: {}'.format(pics))
        if len(pics) > 0:
            db = get_db()
            pic = db.retrieve_picture_by_key(pics[0])
            self.logger.info('Pic: {}'.format(pic))
            self.editor.picture = pic

    def view_picture(self):
        """View selected picture."""
        pics = self.tree.selection()
        if len(pics) > 0:
            db = get_db()
            pic = db.retrieve_picture_by_key(pics[0])
            image = Image.open(pic.path)
            image.show()
