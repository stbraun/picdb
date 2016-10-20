# coding=utf-8
"""
Common UI (tkinter) related stuff.
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


def all_children(wid):
    """Return all children of a widget."""
    _list = wid.winfo_children()
    for item in _list:
        if item.winfo_children():
            _list.extend(item.winfo_children())
    return _list


def tag_all_children(parent, tk_tag):
    """Add tk_tag to parent and all children widgets."""
    widgets = all_children(parent)
    widgets.append(parent)
    for widget in widgets:
        widget.bindtags((tk_tag,) + widget.bindtags())


class Observable:
    """Mix-in class providing support for tk event binding."""

    def __init__(self, super_bind, event_identifiers):
        """Initialize observable mix-in.

        :param super_bind: function to call for propagation of bind requests.
        :type super_bind: f(sequence, func, add) (tkinter bind() function)
        :param event_identifiers: sequence of event identifiers this class
        shall support.
        :type event_identifiers: [str]
        """
        super().__init__()
        self.supported_events = set(event_identifiers)
        self.listeners = {}
        self.super_bind = super_bind

    def _add_event_identifier(self, event_identifier):
        """Add another event identifier.

        :param event_identifier: event identifier.
        :type event_identifier: str
        """
        self.supported_events.add(event_identifier)

    def bind(self, sequence=None, func=None, add=None):
        """Bind to this widget at event SEQUENCE a call to function FUNC."""
        if sequence in self.supported_events:
            self.listeners[sequence] = func
        else:
            if self.super_bind is not None:
                self.super_bind(sequence, func, add)

    def unbind(self, event_identifier):
        """Unbind listener for event_identifier.

        :param event_identifier: event identifier.
        :type event_identifier: str
        """
        if event_identifier in self.listeners.keys():
            del(self.listeners[event_identifier])

    def _call_listeners(self, event_identifier, event=None):
        """Call registered listeners for event_identifier."""
        if event_identifier in self.listeners.keys():
            listener = self.listeners[event_identifier]
            listener(event)
