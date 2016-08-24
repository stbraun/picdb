# coding=utf-8
"""
Application entry for PicDB.
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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import tkinter as tk
from tkinter import ttk
import logging
from log import initialize_logger
from uimain import StatusPanel
from uipictures import PictureImporter
from uiseries import SeriesManagement
from uitags import TagManagement


class Application(ttk.Frame):
    """Mind Monitor Frontend"""

    def __init__(self, master):
        super().__init__(master, padding="3 5 3 5", width=400, height=300)
        self.logger = logging.getLogger('picdb.ui')
        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.create_widgets()

    def create_widgets(self):
        """Build UI."""
        notebook = ttk.Notebook(self)
        notebook.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        search_frame = ttk.Frame(notebook)
        import_frame = PictureImporter(notebook)
        series_frame = SeriesManagement(notebook)
        tags_frame = TagManagement(notebook)
        notebook.add(search_frame, text='search database')
        notebook.add(import_frame, text='import pictures')
        notebook.add(series_frame, text='manage series')
        notebook.add(tags_frame, text='manage tags')

        status_panel = StatusPanel(self)
        status_panel.grid(row=1, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        ttk.Button(self, text='Quit',
                   command=self.quit).grid(row=2, column=0,
                                           sticky=(tk.N, tk.S))
        self.rowconfigure(0, weight=1, minsize=400)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.columnconfigure(0, weight=1, minsize=600)

if __name__ == '__main__':
    initialize_logger()
    root = tk.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.geometry('1000x600+200+100')
    APP = Application(root)
    APP.master.title('PicDB')
    APP.mainloop()

