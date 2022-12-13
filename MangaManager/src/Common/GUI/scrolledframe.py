# Extracted from: https://github.com/alejandroautalan/pygubu/tree/master/pygubu

# encoding: utf8
from __future__ import annotations

import platform
import tkinter as tk
import tkinter.ttk as ttk

CONFIGURE = '<Configure>'


def bindings(widget, seq):
    return [x for x in widget.bind(seq).splitlines() if x.strip()]


def _funcid(binding):
    return binding.split()[1][3:]


def remove_binding(widget, seq, index=None, funcid=None):
    b = bindings(widget, seq)

    if index is not None:
        try:
            binding = b[index]
            widget.unbind(seq, _funcid(binding))
            b.remove(binding)
        except IndexError:
            return

    elif funcid:
        binding = None
        for x in b:
            if _funcid(x) == funcid:
                binding = x
                b.remove(binding)
                widget.unbind(seq, funcid)
                break
        if not binding:
            return
    else:
        raise ValueError('No index or function id defined.')

    for x in b:
        widget.bind(seq, '+' + x, 1)


class ApplicationLevelBindManager(object):
    # Mouse wheel support
    mw_active_area = None
    mw_initialized = False

    @staticmethod
    def on_mousewheel(event):
        if ApplicationLevelBindManager.mw_active_area:
            ApplicationLevelBindManager.mw_active_area.on_mousewheel(event)

    @staticmethod
    def mousewheel_bind(widget):
        ApplicationLevelBindManager.mw_active_area = widget

    @staticmethod
    def mousewheel_unbind():
        ApplicationLevelBindManager.mw_active_area = None

    @staticmethod
    def init_mousewheel_binding(master):
        if not ApplicationLevelBindManager.mw_initialized:
            _os = platform.system()
            if _os in ('Linux', 'OpenBSD', 'FreeBSD'):
                master.bind_all(
                    '<4>', ApplicationLevelBindManager.on_mousewheel, add='+')
                master.bind_all(
                    '<5>', ApplicationLevelBindManager.on_mousewheel, add='+')
            else:
                # Windows and MacOS
                master.bind_all(
                    "<MouseWheel>",
                    ApplicationLevelBindManager.on_mousewheel,
                    add='+')
            ApplicationLevelBindManager.mw_initialized = True

    @staticmethod
    def make_onmousewheel_cb(widget, orient, factor=1):
        """Create a callback to manage mousewheel events
        orient: string (posible values: ('x', 'y'))
        widget: widget that implement tk xview and yview methods
        """
        _os = platform.system()
        view_command = getattr(widget, orient + 'view')
        if _os in ('Linux', 'OpenBSD', 'FreeBSD'):
            def on_mousewheel(event):
                if event.num == 4:
                    view_command('scroll', (-1) * factor, 'units')
                elif event.num == 5:
                    view_command('scroll', factor, 'units')

        elif _os == 'Windows':
            def on_mousewheel(event):
                view_command('scroll', (-1) *
                             int((event.delta / 120) * factor), 'units')

        elif _os == 'Darwin':
            def on_mousewheel(event):
                view_command('scroll', event.delta, 'units')
        else:
            # FIXME: unknown platform scroll method
            def on_mousewheel(*_):
                pass

        return on_mousewheel


# noinspection PyUnresolvedReferences
class ScrolledFrame(ttk.Frame):
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'
    BOTH = 'both'

    _framecls = ttk.Frame
    _sbarcls = ttk.Scrollbar

    # noinspection PyMissingConstructor
    def __init__(self, master=None, **kw):
        self.scrolltype = kw.pop('scrolltype', self.VERTICAL)
        self.usemousewheel = tk.getboolean(kw.pop('usemousewheel', False))
        self._bindingids = []

        self._framecls.__init__(self, master, **kw)

        self._container = self._framecls(self, width=200, height=200)
        self._clipper = self._framecls(self._container, width=200, height=200)
        self.innerframe = self._framecls(self._clipper)
        self.vsb = self._sbarcls(self._container)
        self.hsb = self._sbarcls(self._container, orient="horizontal")

        # variables
        self.hsbOn = 0
        self.vsbOn = 0
        self.hsbNeeded = 0
        self.vsbNeeded = 0
        self._jfraction = 0.05
        self._scrollTimer = None
        self._scrollRecurse = 0
        self._startX = 0
        self._start_y = 0

        # configure scroll
        self.hsb.set(0.0, 1.0)
        self.vsb.set(0.0, 1.0)
        self.vsb.config(command=self.yview)
        self.hsb.config(command=self.xview)

        # grid
        self._container.pack(expand=True, fill='both')
        self._clipper.grid(row=0, column=0, sticky=tk.NSEW)

        self._container.rowconfigure(0, weight=1)
        self._container.columnconfigure(0, weight=1)

        # Whenever the clipping window or scrolled frame change size,
        # update the scrollbars.
        self.innerframe.bind(CONFIGURE, self._reposition)
        self._clipper.bind(CONFIGURE, self._reposition)
        self.bind(CONFIGURE, self._reposition)
        self._configure_mousewheel()

    # Set timer to call real reposition method, so that it is not
    # called multiple times when many things are reconfigured at the
    # same time.
    def reposition(self):
        if self._scrollTimer is None:
            self._scrollTimer = self.after_idle(self._scrollBothNow)

    # Called when the user clicks in the horizontal scrollbar.
    # Calculates new position of frame then calls reposition() to
    # update the frame and the scrollbar.
    def xview(self, mode=None, value=None, units=None):
        if isinstance(value, str):
            value = float(value)
        if mode is None:
            return self.hsb.get()
        elif mode == 'moveto':
            frame_width = self.innerframe.winfo_reqwidth()
            self._startX = value * float(frame_width)
        else:  # mode == 'scroll'
            clipper_width = self._clipper.winfo_width()
            if units == 'units':
                jump = int(clipper_width * self._jfraction)
            else:
                jump = clipper_width
            self._startX = self._startX + value * jump

        self.reposition()

    # Called when the user clicks in the vertical scrollbar.
    # Calculates new position of frame then calls reposition() to
    # update the frame and the scrollbar.
    def yview(self, mode=None, value=None, units=None):

        if isinstance(value, str):
            value = float(value)
        if mode is None:
            return self.vsb.get()
        elif mode == 'moveto':
            frame_height = self.innerframe.winfo_reqheight()
            self._start_y = value * float(frame_height)
        else:  # mode == 'scroll'
            clipper_height = self._clipper.winfo_height()
            if units == 'units':
                jump = int(clipper_height * self._jfraction)
            else:
                jump = clipper_height
            self._start_y = self._start_y + value * jump

        self.reposition()

    def _reposition(self, *_):
        self.reposition()

    def _getxview(self):

        # Horizontal dimension.
        clipper_width = self._clipper.winfo_width()
        frame_width = self.innerframe.winfo_reqwidth()
        if frame_width <= clipper_width:
            # The scrolled frame is smaller than the clipping window.

            self._startX = 0
            end_scrollX_x = 1.0
            # use expand by default
            relwidth = 1
        else:
            # The scrolled frame is larger than the clipping window.
            # use expand by default
            if self._startX + clipper_width > frame_width:
                self._startX = frame_width - clipper_width
                end_scrollX_x = 1.0
            else:
                if self._startX < 0:
                    self._startX = 0
                end_scrollX_x = (self._startX + clipper_width) / float(frame_width)
            relwidth = ''

        # Position frame relative to clipper.
        self.innerframe.place(x=-self._startX, relwidth=relwidth)
        return (self._startX / float(frame_width), end_scrollX_x)

    def _getyview(self):

        # Vertical dimension.
        clipper_height = self._clipper.winfo_height()
        frame_height = self.innerframe.winfo_reqheight()
        if frame_height <= clipper_height:
            # The scrolled frame is smaller than the clipping window.

            self._start_y = 0
            end_scroll_y = 1.0
            # use expand by default
            relheight = 1
        else:
            # The scrolled frame is larger than the clipping window.
            # use expand by default
            if self._start_y + clipper_height > frame_height:
                self._start_y = frame_height - clipper_height
                end_scroll_y = 1.0
            else:
                if self._start_y < 0:
                    self._start_y = 0
                end_scroll_y = (self._start_y + clipper_height) / float(frame_height)
            relheight = ''

        # Position frame relative to clipper.
        self.innerframe.place(y=-self._start_y, relheight=relheight)
        return (self._start_y / float(frame_height), end_scroll_y)

    # According to the relative geometries of the frame and the
    # clipper, reposition the frame within the clipper and reset the
    # scrollbars.
    def _scrollBothNow(self):
        self._scrollTimer = None

        # Call update_idletasks to make sure that the containing frame
        # has been resized before we attempt to set the scrollbars.
        # Otherwise the scrollbars may be mapped/unmapped continuously.
        self._scrollRecurse = self._scrollRecurse + 1
        self.update_idletasks()
        self._scrollRecurse = self._scrollRecurse - 1
        if self._scrollRecurse != 0:
            return

        xview = self._getxview()
        yview = self._getyview()
        self.hsb.set(xview[0], xview[1])
        self.vsb.set(yview[0], yview[1])

        require_hsb = self.scrolltype in (self.BOTH, self.HORIZONTAL)
        self.hsbNeeded = (xview != (0.0, 1.0)) and require_hsb
        require_vsb = self.scrolltype in (self.BOTH, self.VERTICAL)
        self.vsbNeeded = (yview != (0.0, 1.0)) and require_vsb

        # If both horizontal and vertical scrollmodes are dynamic and
        # currently only one scrollbar is mapped and both should be
        # toggled, then unmap the mapped scrollbar.  This prevents a
        # continuous mapping and unmapping of the scrollbars.
        if (self.hsbNeeded != self.hsbOn and
                self.vsbNeeded != self.vsbOn and
                self.vsbOn != self.hsbOn):
            if self.hsbOn:
                self._toggleHorizScrollbar()
            else:
                self._toggleVertScrollbar()
            return

        if self.hsbNeeded != self.hsbOn:
            self._toggleHorizScrollbar()

        if self.vsbNeeded != self.vsbOn:
            self._toggleVertScrollbar()

    def _toggleHorizScrollbar(self):

        self.hsbOn = not self.hsbOn

        if self.hsbOn:
            self.hsb.grid(row=1, column=0, sticky=tk.EW)
        else:
            self.hsb.grid_forget()

    def _toggleVertScrollbar(self):

        self.vsbOn = not self.vsbOn

        if self.vsbOn:
            self.vsb.grid(row=0, column=1, sticky=tk.NS)
        else:
            self.vsb.grid_forget()

    def configure(self, cnf=None, **kw):
        # noinspection PyProtectedMember
        args = tk._cnfmerge((cnf, kw))
        key = 'usemousewheel'
        if key in args:
            self.usemousewheel = tk.getboolean(args[key])
            del args[key]
            self._configure_mousewheel()
        self._framecls.configure(self, args)

    config = configure

    def cget(self, key):
        option = 'usemousewheel'
        if key == option:
            return self.usemousewheel
        return self._framecls.cget(self, key)

    __getitem__ = cget

    def _configure_mousewheel(self):
        if self.usemousewheel:
            ApplicationLevelBindManager.init_mousewheel_binding(self)

            if self.hsb and not hasattr(self.hsb, 'on_mousewheel'):
                self.hsb.on_mousewheel = ApplicationLevelBindManager.make_onmousewheel_cb(
                    self, 'x', 2)
            if self.vsb and not hasattr(self.vsb, 'on_mousewheel'):
                self.vsb.on_mousewheel = ApplicationLevelBindManager.make_onmousewheel_cb(
                    self, 'y', 2)

            main_sb = self.vsb or self.hsb
            if main_sb:
                self.on_mousewheel = main_sb.on_mousewheel
                bid = self.bind(
                    '<Enter>',
                    lambda event: ApplicationLevelBindManager.mousewheel_bind(self),
                    add='+')
                self._bindingids.append((self, bid))
                bid = self.bind('<Leave>',
                                lambda event: ApplicationLevelBindManager.mousewheel_unbind(),
                                add='+')
                self._bindingids.append((self, bid))
            for s in (self.vsb, self.hsb):
                if s:
                    bid = s.bind(
                        '<Enter>',
                        lambda event,
                               scrollbar=s: ApplicationLevelBindManager.mousewheel_bind(scrollbar),
                        add='+')
                    self._bindingids.append((s, bid))
                    if s != main_sb:
                        bid = s.bind(
                            '<Leave>',
                            lambda event: ApplicationLevelBindManager.mousewheel_unbind(),
                            add='+')
                        self._bindingids.append((s, bid))
        else:
            for widget, bid in self._bindingids:
                remove_binding(widget, bid)
