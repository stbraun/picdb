# coding=utf-8
"""
Application entry for PicDB.
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

import argparse
import logging
import tkinter as tk
from tkinter import ttk

from .log import initialize_logger
from .uistatus import StatusPanel
from .uipictures import PictureManagement
from .uigroups import GroupManagement
from .uitags import TagManagement
from .persistence import set_db
from .config import get_configuration


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
        import_frame = PictureManagement(notebook)
        series_frame = GroupManagement(notebook)
        tags_frame = TagManagement(notebook)
        notebook.add(import_frame, text='manage pictures')
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


def _parse_arguments(args):
    """Parse command line arguments.

    :param args: given arguments, e.g. sys.argc[1:]
    :type args: [str]
    :return: configuration namespace
    :rtype: {<key>:<value>}
    """
    parser = argparse.ArgumentParser(
        description='Assign tags to pictures and pictures to groups.')
    parser.add_argument('--db', action='store', dest='db',
                        default=get_configuration('database'),
                        help='Path to database to use. Overrides '
                             'configuration file.')
    parser.add_argument('--title', action='store', dest='title',
                        default='PicDB',
                        help='Window title.')
    parser.add_argument('--geometry', action='store', dest='geometry',
                        default=get_configuration('geometry'),
                        help='Window geometry, e.g. "2200x1000+100+100".')
    arguments = parser.parse_args(args)
    return arguments


def start_application(argv):
    initialize_logger()
    root = tk.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    # no tear-off menus
    root.option_add('*tearoff', False)
    args = _parse_arguments(argv)
    set_db(args.db)
    root.geometry(args.geometry)
    app = Application(root)
    app.master.title(args.title)
    app.mainloop()
