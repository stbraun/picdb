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

from .model import PictureReference


class PicTreeView(ttk.Treeview):
    """Extended tree view."""
    def __init__(self, master, *args, **kwdargs):
        super().__init__(master, *args, **kwdargs)
        self.logger = logging.getLogger('picdb.ui')

    def clear(self):
        """Remove all items from tree."""
        items = self.get_children()
        self.logger.info('Items to delete from tree: {}'.format(items))
        if len(items) > 0:
            self.delete(*items)


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
