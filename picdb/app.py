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

import sys
import functools

import argparse
import logging
import tkinter as tk
from tkinter import ttk
import os

from .log import initialize_logger
from .uistatus import StatusPanel
from .uipictures import PictureManagement
from .uigroups import GroupManagement
from .uitags import TagManagement
from .persistence import create_db, DBParameters
from .config import get_configuration


class Application(ttk.Frame):
    """PicDB Frontend"""

    def __init__(self, master):
        super().__init__(master, padding="3 5 3 5", width=400, height=300)
        self.logger = logging.getLogger('picdb.ui')
        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.create_widgets()

    def set_title(self, title):
        """ Set application title.

        :param title: title to set
        :type title: str
        """
        self.master.title = title

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
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description='Assign tags to pictures and pictures to groups.')
    parser.add_argument('--db', action='store', dest='db',
                        default=get_configuration('db.name'),
                        help='Name of database to use. Overrides '
                             'configuration file.')
    parser.add_argument('--user', action='store', dest='user',
                        default=get_configuration('db.user'),
                        help='Database user. Overrides '
                             'configuration file.')
    parser.add_argument('--passwd', action='store', dest='passwd',
                        default=get_configuration('db.passwd'),
                        help='Password of database user. Overrides '
                             'configuration file.')
    parser.add_argument('--port', action='store', dest='port',
                        default=get_configuration('db.port'),
                        help='Port of database to use. Overrides '
                             'configuration file.')
    parser.add_argument('--title', action='store', dest='title',
                        default='PicDB',
                        help='Window title.')
    parser.add_argument('--geometry', action='store', dest='geometry',
                        default=get_configuration('ui.geometry'),
                        help='Window geometry, e.g. "2200x1000+100+100".')
    arguments = parser.parse_args(args)
    return arguments


def create_db_by_arguments(args):
    """ Create a database instance based on the given arguments.

    :param args: args.db, args.user, args.passwd, args.port
    :type args: argParse.Namespace
    """
    create_db(DBParameters(args.db, args.user, args.passwd, args.port))


def setup():
    """Check for configuration and log folder.

    Create it if it does not exist yet.
    """
    app_folder = os.path.expanduser('~/.picdb')
    if not os.path.exists(app_folder):
        os.mkdir(app_folder)


def traceit(output_file, frame, event, arg):
    """Trace function."""
    fname = frame.f_code.co_filename
    if 'picdb/picdb' in fname and event in ('call', 'return'):
        template = '{evt} {file} {func} {line} {res!s}\n'
        record = template.format(evt=event, file=fname,
                                 func=frame.f_code.co_name,
                                 line=frame.f_lineno,
                                 res=arg)
        output_file.write(record)
        output_file.flush()
    return functools.partial(traceit, output_file)


def main(args, root):
    """Start application. """
    create_db_by_arguments(args)
    root.geometry(args.geometry)
    app = Application(root)
    app.set_title(args.title)
    app.mainloop()


def start_application(argv):
    """ Entry point of the application.

    :param argv: command line arguments
    :type argv: [str]
    """
    setup()
    initialize_logger()
    root = tk.Tk()
    root.title = '-- libraries --'
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    # no tear-off menus
    root.option_add('*tearoff', False)
    args = _parse_arguments(argv)
    if get_configuration('trace.activate', default=False):
        with open(get_configuration('trace.trace_file',
                                    default='/tmp/picdb.trace'),
                  'w') as trace_file:
            sys.settrace(functools.partial(traceit, trace_file))
            try:
                main(args, root)
            finally:
                sys.settrace(None)
    else:
        main(args, root)
