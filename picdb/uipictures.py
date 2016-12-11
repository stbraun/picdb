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

import logging
import os
import tkinter as tk
import webbrowser
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

from PIL import Image, ImageTk

from .commons import get_resource_path
from .group import retrieve_groups_for_picture
from .persistence import DuplicateException
from .picture import Picture, add_picture, retrieve_picture_by_path, \
    retrieve_filtered_pictures, retrieve_picture_by_key
from .uicommon import tag_all_children, Observable
from .uigroups import GroupSelector
from .uimasterdata import PicTreeView, FilteredTreeView
from .uitags import TagSelector


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
        self.tag_selector = None
        self.series_selector = None
        # canvas will hold the preview image.
        self.canvas = None
        # width and height will change when resizing the window.
        self._canvas_width = 800
        self._canvas_height = 1000
        # Currently edited picture
        self.current_picture = None
        # Currently displayed image. Only required to hold a reference to
        # the object.
        self.image = None
        # The tag assigned to the image currently displayed in canvas.
        self.image_tag = '__image__'
        self._create_widgets()
        # Bind listener for resize events to adapt image size for preview.
        self.canvas.bind("<Configure>", self._fit_image)
        # add key bindings: use self as (tk-)tag to bind a listener also to all
        # children widgets
        tag_all_children(self, self)
        self.bind('<Meta_L>r', self._reset)
        # bind listener for save event
        self.editor.bind(self.editor.EVT_ITEM_SAVED, self._refresh_saved_item)

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
        self.content_frame.columnconfigure(2, weight=4)
        self.filter_tree = PictureFilteredTreeView(self.content_frame)
        self.filter_tree.grid(row=0, column=0,
                              sticky=(tk.W, tk.N, tk.E, tk.S))
        self.filter_tree.bind(self.filter_tree.EVT_ITEM_SELECTED,
                              self.item_selected)
        self.filter_tree.bind(self.filter_tree.EVT_ITEM_DELETED,
                              self._item_deleted)
        self.editor = PictureMetadataEditor(self.content_frame)
        self.editor.grid(row=0, column=1,
                         sticky=(tk.W, tk.N, tk.E, tk.S))
        self.canvas = tk.Canvas(self.content_frame, width=self._canvas_width,
                                height=self._canvas_height)
        self.canvas.grid(row=0, column=2, sticky=(tk.W, tk.N, tk.E, tk.S))

    def _create_control_frame(self):
        self.control_frame = ttk.Frame(self, borderwidth=2, relief=tk.GROOVE)
        self.columnconfigure(0, weight=1)
        load_button = ttk.Button(self.control_frame, text='load pictures',
                                 command=self.load_pictures)
        load_button.grid(row=0, column=0, sticky=(tk.W, tk.N))
        add_button = ttk.Button(self.control_frame, text='import pictures',
                                command=self.import_pictures)
        add_button.grid(row=0, column=1, sticky=(tk.W, tk.N))
        rst_text = 'reset selection [CMD-R]'
        clear_button = ttk.Button(self.control_frame, text=rst_text,
                                  command=self._reset)
        clear_button.grid(row=0, column=2, sticky=(tk.W, tk.N))

    def load_pictures(self):
        """Load a bunch of pictures from database."""
        self.clear()
        self.filter_tree.load_items()

    def import_pictures(self):
        """Let user select pictures and import them into database."""
        files = filedialog.askopenfilenames()
        self.logger.info('Files selected for import: {}'.format(files))
        pictures = [Picture(None, os.path.basename(pth), pth, None)
                    for pth in files]
        import_counter = 0
        duplicate_counter = 0
        for pic in pictures:
            try:
                add_picture(pic)
            except DuplicateException:
                duplicate_counter += 1
                self.logger.warning(
                    'Duplicate picture not imported: {}'.format(pic))
            else:
                pic_ = retrieve_picture_by_path(pic.path)
                self.filter_tree.add_item_to_tree(pic_)
                import_counter += 1
        msg_tmpl = '{} pictures added.\n{} duplicates.'
        messagebox.showinfo(title='Picture Import',
                            message=msg_tmpl.format(
                                import_counter if import_counter > 0 else 'No',
                                duplicate_counter if duplicate_counter > 0
                                else 'No'))

    def item_selected(self, _):
        """An item in the tree view was selected."""
        pics = self.filter_tree.selected_items()
        if len(pics) == 1:
            self.current_picture = pics[0]
            self.editor.load_picture(self.current_picture)
            self._display_picture()
        else:
            self.clear()
            self.current_picture = None
            self.editor.load_picture_set(pics)

    def _item_deleted(self, _):
        """An item in the tree view was deleted."""
        self.clear()

    def _refresh_saved_item(self, _=None):
        """Item in editor was saved. Refresh tree view."""
        pic = self.editor.picture
        self.filter_tree.refresh_item_in_tree(pic)

    def _display_picture(self):
        """Display current picture in canvas."""
        if self.current_picture is not None:
            try:
                img = Image.open(self.current_picture.path)
            except FileNotFoundError:
                placeholder = get_resource_path('picdb',
                                                'resources/not_found.png')
                img = Image.open(placeholder)
            except (OSError, ValueError):
                placeholder = get_resource_path('picdb',
                                                'resources/not_supported.png')
                img = Image.open(placeholder)
            img.thumbnail(
                (self._canvas_width - 2, self._canvas_height - 2),
                Image.ANTIALIAS)
            self.image = ImageTk.PhotoImage(img)
            self.canvas.delete(self.image_tag)  # delete old picture if any
            self.canvas.create_image(1, 1, anchor=tk.NW,
                                     state=tk.NORMAL,
                                     image=self.image,
                                     tags=self.image_tag)

    def _fit_image(self, event=None, _last=[None] * 2):
        """Fit image inside application window on resize."""
        if event is not None and event.widget is self.canvas and (
                    _last[0] != event.width or _last[1] != event.height):
            # size changed; update image
            self.logger.info(
                'Resize event on canvas: ({}, {})'.format(event.width,
                                                          event.height))
            _last[:] = event.width, event.height
            self._canvas_width = event.width
            self._canvas_height = event.height
            self.after(1, self._display_picture)

    def _reset(self, _=None):
        """Reset all."""
        self.clear()
        self.filter_tree.clear_selection()
        return "break"

    def clear(self):
        """Clear editor and preview."""
        self.editor.clear()
        self.canvas.delete(self.image_tag)


class PictureFilteredTreeView(FilteredTreeView):
    """Provide a picture tree and a selection panel."""

    def __init__(self, master):
        self.logger = logging.getLogger('picdb.ui')
        self.path_filter_var = tk.StringVar()
        self.limit_var = tk.IntVar()
        self.tag_selector = None
        self.series_selector = None
        super().__init__(master, PictureReferenceTree.create_instance)
        self._set_default_path_filter()
        self.path_filter_entry = None
        self.limit_var.set(self.limit_default)
        # initialize selectors
        self.tag_selector.load_items([])
        self.series_selector.load_items([])
        # Bind listener for visibility change of frame
        self.bind("<Visibility>", self._visibility_changed)

    def _create_widgets(self):
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self._create_filter_frame()
        self.series_selector = GroupSelector(self,
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

    def _set_default_path_filter(self):
        self.path_filter_var.set('%')

    def selected_items(self):
        """Provide list of pictures selected in tree.

        :return: selected pictures
        :rtype: list(Picture)
        """
        return self.tree.selected_items()

    def add_item_to_tree(self, picture_):
        """Add given picture to tree view."""
        super().add_item_to_tree(picture_)

    def _retrieve_items(self):
        """Retrieve a bunch of pictures from database.

        name_filter_var and limit_var are considered for retrieval.
        """
        name_filter = self.path_filter_var.get()
        limit = self.limit_var.get()
        series = self.series_selector.selected_items()
        tags = self.tag_selector.selected_items()
        pics = retrieve_filtered_pictures(name_filter, limit, series, tags)
        return pics

    def _visibility_changed(self, event):
        """Listener is called if visibility of widget changes."""
        self.logger.info(
            'Visibility of PictureFilteredTreeView frame changed: {}'.format(
                event.state))
        self.tag_selector.load_items(self.tag_selector.selected_items())
        self.series_selector.load_items(self.series_selector.selected_items())

    def clear_selection(self):
        """Clear current selection and reset filters to default."""
        self._set_default_path_filter()
        self.limit_var.set(self.limit_default)
        self.tag_selector.load_items([])
        self.series_selector.load_items([])
        self.tree.clear()

    def refresh_item_in_tree(self, pic):
        """Refresh representation of given picture in tree view."""
        self.tree.refresh_item(pic)


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
        external_viewer_cmd = self._show_selected_pic_in_external_viewer
        self.menu.add_command(label='Show in external viewer',
                              command=external_viewer_cmd)

    @classmethod
    def create_instance(cls, master, tree_only=False):
        """Factory method."""
        return PictureReferenceTree(master, tree_only)

    def _additional_values(self, item):
        return () if self.tree_only else (item.path, item.description)

    def selected_items(self):
        """Provide list of pictures selected in tree.

        :return: selected pictures
        :rtype: list(Picture)
        """
        item_ids = self.selection()
        pics = [retrieve_picture_by_key(int(pic_id))
                for pic_id in item_ids]
        return pics

    def _is_less(self, item, key):
        return item < retrieve_picture_by_key(int(key))

    def refresh_item(self, pic):
        """Refresh item in tree view with data from pic."""
        self.delete(pic.key)
        self.add_item(pic)

    def _delete_items(self, items):
        """Delete given pictures.

        :param items: items to delete.
        :type items: [Picture]
        """
        for pic in items:
            groups = retrieve_groups_for_picture(pic)
            for group_ in groups:
                group_.remove_picture(pic)
                group_.save()
            pic.delete()

    def _show_selected_pic_in_external_viewer(self):
        """Show selected pictures in external viewer."""
        pics = self.selected_items()
        for pic in pics:
            webbrowser.open('file://' + pic.path)


class PictureReferenceEditor(ttk.LabelFrame):
    """Editor for Picture objects."""

    def __init__(self, master, text='Edit picture reference'):
        super().__init__(master, text=text)
        self.picture_ = None
        self.id_var = tk.IntVar()
        self.name_var = tk.StringVar()
        self.path_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        """Create widgets for view."""
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
        """Update picture from editor fields and return it."""
        if self.picture_ is not None:
            self.picture_.id = self.id_var.get()
            self.picture_.name = self.name_var.get()
            self.picture_.path = self.path_var.get()
            self.picture_.description = self.description_var.get()
        return self.picture_

    @picture.setter
    def picture(self, pic):
        """Put picture into editor. Fill attribute values into editor
        fields."""
        self.picture_ = pic
        self.id_var.set(pic.key)
        self.name_var.set(pic.name)
        self.path_var.set(pic.path)
        self.description_var.set(pic.description)

    def clear(self):
        """Clear entries and remove reference to picture."""
        self.id_var.set('')
        self.name_var.set('')
        self.path_var.set('')
        self.description_var.set('')
        self.picture_ = None


class PictureMetadataEditor(ttk.Frame, Observable):
    """Editor component for picture meta data."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.EVT_ITEM_SAVED = '<<ItemSaved>>'
        Observable.__init__(self, super().bind, {self.EVT_ITEM_SAVED})
        self.master = master
        self.content_frame = None
        self.control_frame = None
        self.tag_selector = None
        self.grp_selector = None
        self.editor = None
        self.save_button = None
        self.picture = None
        self.picture_set = None
        self._create_widgets()
        # add key bindings: use self as (tk-)tag to bind a listener also to all
        # children widgets
        tag_all_children(self, self)
        self.bind('<Meta_L>s', self._save_picture)
        # bind to assignment events to auto-save
        self.tag_selector.bind(self.tag_selector.EVT_ITEM_ASSIGNED,
                               self._save_picture)
        self.tag_selector.bind(self.tag_selector.EVT_ITEM_UNASSIGNED,
                               self._save_picture)
        self.grp_selector.bind(self.grp_selector.EVT_ITEM_ASSIGNED,
                               self._save_picture)
        self.grp_selector.bind(self.grp_selector.EVT_ITEM_UNASSIGNED,
                               self._save_picture)

    def is_mass_assignment(self):
        """Determine if multiple pictures shall be processed.

        :return: True if multiple pictures shall be processed.
        :rtype: bool
        """
        return self.picture is None and self.picture_set is not None

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
        left_tree_options = {'open_items': True}
        self.grp_selector = GroupSelector(self.content_frame,
                                          left_tree_options=left_tree_options,
                                          text='Assign series')
        self.grp_selector.grid(row=1, column=0,
                               sticky=(tk.W, tk.N, tk.E, tk.S))
        self.tag_selector = TagSelector(self.content_frame,
                                        left_tree_options=left_tree_options,
                                        text='Assign tags')
        self.tag_selector.grid(row=2, column=0,
                               sticky=(tk.W, tk.N, tk.E, tk.S))

    def bind(self, sequence=None, func=None, add=None):
        """Bind event handlers."""
        Observable.bind(self, sequence, func, add)

    def _create_control_frame(self, master):
        self.control_frame = ttk.Frame(master)
        self.columnconfigure(0, weight=1)
        self.save_button = ttk.Button(self.control_frame, text='save',
                                      command=self._save)
        self.save_button.grid(row=0, column=0)

    def _save_picture(self, _):
        self._save()
        return "break"

    def _save(self):
        """Save current picture or picture set."""
        if self.is_mass_assignment():
            tags = self.tag_selector.selected_items()
            groups = self.grp_selector.selected_items()
            for pic in self.picture_set:
                for tag in tags:
                    pic.assign_tag(tag)
                for group_ in groups:
                    group_.assign_picture(pic)
                pic.save()
            for group_ in groups:
                group_.save()
        else:
            self.picture = self.editor.picture
            self._update_series()
            tags = self.tag_selector.selected_items()
            self.picture.tags = tags
            self.picture.save()
            self._call_listeners(self.EVT_ITEM_SAVED, None)

    def _update_series(self):
        """Remove or add picture from groups according to changes made
        during editing."""
        saved_groups = set(retrieve_groups_for_picture(self.picture))
        edt_groups = set(self.grp_selector.selected_items())
        groups_to_add = edt_groups.difference(saved_groups)
        groups_to_remove = saved_groups.difference(edt_groups)
        for grp in groups_to_add:
            grp.assign_picture(self.picture)
            grp.save()
        for grp in groups_to_remove:
            grp.remove_picture(self.picture)
            grp.save()

    def load_picture(self, picture_):
        """Load picture into editor.

        :param picture_: the picture to process.
        :type picture_: Picture
        """
        self.picture = picture_
        self.picture_set = None
        self.editor.picture = picture_
        self.tag_selector.load_items(picture_.tags)
        # Retrieve groups the picture is currently assigned to.
        self.grp_selector.load_items(
            retrieve_groups_for_picture(picture_))

    def load_picture_set(self, pictures):
        """Load picture set into editor.

        :param pictures: picture set to process
        :type pictures: [Picture]
        """
        self.picture_set = pictures
        self.picture = None
        self.tag_selector.load_items([])
        self.grp_selector.load_items([])

    def clear(self):
        """Clear the editor."""
        self.editor.clear()
        self.picture = None
        self.grp_selector.clear()
        self.tag_selector.clear()
