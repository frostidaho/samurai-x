# Copyright (c) 2008, samurai-x.org
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the samurai-x.org nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY SAMURAI-X.ORG ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL SAMURAI-X.ORG  BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import pyglet
from pyglet.window.xlib import xlib 

import weakref

import samuraix
from samuraix.sxctypes import *
from samuraix.rect import Rect
from samuraix import xhelpers
from samuraix.titlebar import TitleBar
from samuraix.simplewindow import SimpleWindow
from samuraix.drawcontext import DrawContext

from samuraix.xconstants import BUTTONMASK, MOUSEMASK, CLEANMASK

import logging
log = logging.getLogger(__name__)


NET_WM_STATE_REMOVE = 0
NET_WM_STATE_ADD = 1
NET_WM_STATE_TOGGLE = 2


class Client(pyglet.event.EventDispatcher):

    all_clients = []
    window_2_client_map = weakref.WeakValueDictionary()

    all_frames = []
    window_2_frame_map = weakref.WeakValueDictionary()

    @classmethod 
    def get_by_window(cls, window):
        return cls.window_2_client_map.get(window)

    @classmethod
    def get_by_frame(cls, window):
        return cls.window_2_frame_map.get(window)

    def __init__(self, screen, window, wa):
        self.screen = screen
        self.window = window
        self.geom = Rect(wa.x, wa.y, wa.width, wa.height)
        self.floating_geom = self.geom.copy()       
        self.maxed_geom = self.geom.copy()
        self.old_border = wa.border_width
        self.desktop = None
        self.border_width = 1
        self.title = None

        self.maximised = False
        self.minimised = False
        self.shaded = False
        self.sticky = False
        self.skip_taskbar = False
        #self.decorated = True

        self.resizing = False

        self.config = samuraix.config['client']

        self.configure_window()
        self.update_title()
        self.update_size_hints()
        self.update_wm_hints()
        self.check_ewmh()

        log.info("new client with %s %s" % (self.window, self.geom))

        self.all_clients.append(self)
        self.window_2_client_map[self.window] = self

        self.frame_context = None
        frame_geom = self.geom.copy()
        frame_geom.height += 15
        frame_geom.width += 2
        self.frame = SimpleWindow(self.screen, self.geom, 1)
        xlib.XReparentWindow(samuraix.display, self.window, self.frame.window, 1, 15)
        xlib.XMapWindow(samuraix.display, self.frame.window)

        self.draw_frame()

        self.all_frames.append(self.frame)
        self.window_2_frame_map[self.frame.window] = self

        xlib.XSelectInput(samuraix.display, self.frame.window, 
                            xlib.StructureNotifyMask | 
                            xlib.PropertyChangeMask | 
                            xlib.EnterWindowMask)

        self.decorations = [] #[TitleBar(self)]
        self.update_decorations()

    def __str__(self):
        return "<Client window=%s geom=%s title='%s'>" % (self.window, self.geom, self.title)

    def configure_window(self):
        ce = xlib.XConfigureEvent()
        ce.type = xlib.ConfigureNotify
        ce.display = samuraix.display
        ce.event = self.window
        ce.window = self.window
        ce.x = self.geom.x
        ce.y = self.geom.y
        ce.width = self.geom.width
        ce.height = self.geom.height
        ce.border_width = self.border_width
        ce.above = xlib.None_
        ce.override_redirect = False
        return xlib.XSendEvent(samuraix.display, self.window, False, 
                xlib.StructureNotifyMask, cast(byref(ce), POINTER(xlib.XEvent)))

    def check_ewmh(self):
        format = c_int()
        real = xlib.Atom()
        data = c_uchar_p()
        n = c_ulong()
        extra = c_ulong()

        #if (xlib.XGetWindowProperty(samuraix.display, self.window, samuraix.atoms['_NET_WM_STATE'],
        #    0, LONG_NAN, False, xatom.XA_ATOM, byref(real), byref(format), byref(n),
        #    byref(extra), byref(data)) == xlib.Success):
        #    state = cast(data, xlib.Atom_p)       

    def process_property_notify(self, ev):
        log.debug('prop change for client %s' % client)
        if ev.atom == xatom.XA_WM_TRANSIENT_FOR:
            trans = xlib.Window()
            xlib.XGetTransientForHint(samuraix.display, self.window, byref(trans))
            # needs rearrange
        elif ev.atom == xatom.XA_WM_NORMAL_HINTS:
            self.update_size_hints()
        elif ev.atom == xatom.XA_WM_HINTS:
            self.update_wm_hints()
        elif ev.atom == xatom.XA_WM_NAME or ev.atom == samuraix.atoms['_NET_WM_NAME']:
            self.update_title()

    def update_title(self):
        title = xhelpers.get_text_property(self.window, samuraix.atoms['_NET_WM_NAME'])
        if not title:
            title = xhelpers.get_text_property(self.window, samuraix.atoms['WM_NAME'])
        if title != self.title:
            self.title = title
            self.dispatch_event('on_title_changed')
        log.debug("title of %s is now %s" % (self, self.title))

    def update_size_hints(self):
        msize = c_long()
        size = xlib.XSizeHints()

        if not xlib.XGetWMNormalHints(samuraix.display, self.window, byref(size), byref(msize)):
            return 0

        if size.flags & xlib.PBaseSize:
            self.base_width = size.base_width
            self.base_height = size.base_height
        elif size.flags & xlib.PMinSize:
            self.base_width = size.min_width
            self.base_height = size.min_height
        else:
            self.base_width = 0 
            self.base_height = 0 

        if size.flags & xlib.PResizeInc:
            self.inc_width = size.width_inc
            self.inc_height = size.height_inc
        else:
            self.inc_width = 0
            self.inc_height = 0 

        if size.flags & xlib.PMaxSize:
            self.max_width = size.max_width
            self.max_height = size.max_height
        else:
            self.max_width = 0 
            self.max_height = 0

        if size.flags & xlib.PMinSize:
            self.min_width = size.min_width
            self.min_height = size.min_height
        elif size.flags & xlib.PBaseSize:
            self.min_width = size.base_width
            self.min_height = size.base_height
        else:
            self.min_width = 0 
            self.min_height = 0

        if size.flags & xlib.PAspect:
            self.min_aspect_x = size.min_aspect.x
            self.min_aspect_y = size.min_aspect.y
            self.max_aspect_x = size.max_aspect.x
            self.max_aspect_y = size.max_aspect.y
        else:
            self.min_aspect_x = 0
            self.min_aspect_y = 0
            self.max_aspect_x = 0
            self.max_aspect_y = 0

        return size.flags

    def update_wm_hints(self):
        wmhp = xlib.XGetWMHints(samuraix.display, self.window)
        if wmhp:
            wmh = wmhp[0]
            self.urgent = wmh.flags & xlib.XUrgencyHint
            if self.urgent: # and its not the focused window...
                pass
                # meant to invalidate that cache and draw titlebar
            if wmh.flags & xlib.StateHint and wmh.initial_state == xlib.WithdrawnState:
                self.border_width = 0
                self.skip = True
            xlib.XFree(wmhp)

    def process_ewmh_state_atom(self, client, state, set):
        def handle_prop(prop, cb=None):
            if set == NET_WM_STATE_ADD:
                r = True
            elif set == NET_WM_STATE_REMOVE:
                r = False
            elif set == NET_WM_STATE_TOGGLE:
                r = not getattr(self, prop)

            if cb is not None:
                if r != getattr(self, prop):
                    cb()
            else:
                setattr(self, prop, r)
        
        if state == samuraix.atoms['_NET_WM_STATE_STICKY']:
            sticky = handle_prop('sticky', self.toggle_sticky)
        elif state == samuraix.atoms['_NET_WM_STATE_SKIP_TASKBAR']:
            skip_taskbar = handle_prop('skip_taskbar')
        elif state == samuraix.atoms['_NET_WM_STATE_FULLSCREEN']:
            fullscreen = handle_prop('fullscreen', self.toggle_fullscreen)

    def update_decorations(self):
        for decoration in self.decorations:
            decoration.update_geometry()

    def resize(self, geometry, hints=False):
        if geometry.width <= 0 or geometry.height <= 0:
            log.debug('not resizing - too small')
            return False

        if (geometry.x != self.geom.x or
            geometry.y != self.geom.y or
            geometry.width != self.geom.width or
            geometry.height != self.geom.height):

            wc = xlib.XWindowChanges()
            self.geom.x = wc.x = geometry.x
            self.geom.y = wc.y = geometry.y
            self.geom.width = wc.width = geometry.width
            self.geom.height = wc.height = geometry.height
            wc.border_width = self.border_width

            xlib.XConfigureWindow(samuraix.display, self.frame.window,
                xlib.CWX | xlib.CWY | xlib.CWWidth | xlib.CWHeight | xlib.CWBorderWidth,
                byref(wc))

            self.frame_context = None
            self.draw_frame()

            wc.x = 1
            wc.y = 15
            wc.width = self.geom.width - 2
            wc.height = self.geom.height - 15
            wc.border_width = 0 

            xlib.XConfigureWindow(samuraix.display, self.window,
                xlib.CWX | xlib.CWY | xlib.CWWidth | xlib.CWHeight | xlib.CWBorderWidth,
                byref(wc))
            self.configure_window()
    
            if not self.resizing:
                self.update_decorations()

    def draw_frame(self):
        if self.frame_context is None:
            self.frame_context = DrawContext(self.screen, 
                    self.geom.width, self.geom.height, self.frame.drawable)

        self.frame_context.fill((0.0, 0.0, 1.0))
        self.frame.refresh_drawable()

    def focus(self):
        log.debug('focusing %s' % self)
        xlib.XSetInputFocus(samuraix.display, self.window, xlib.RevertToPointerRoot, 
                            xlib.CurrentTime)
        self.bring_to_front()
        self.grab_buttons()
        if self.screen.focused_client is not None:
            self.screen.focused_client.dispatch_event('on_blur')
        self.screen.focused_client = self
        self.dispatch_event('on_focus')

    def bring_to_front(self):
        log.debug('stacking %s' % self)
        xlib.XRaiseWindow(samuraix.display, self.window)
        for decoration in self.decorations:
            decoration.bring_to_front()      

    def maximise(self):
        self.maximised = True
        self.resize(self.screen.workspace_geom)

    def unmaximise(self):
        self.maximised = False
        self.resize(self.floating_geom)

    def toggle_maximise(self):
        if self.maximised:
            self.unmaximise()
        else:
            self.maximise()

    def toggle_sticky(self):
        pass
    
    def toggle_fullscreen(self):
        pass

    def remove(self):
        log.debug('removing %s' % self)

        try:
            self.all_clients.remove(self)
            del self.window_2_client_map[self.window]
        except (ValueError, KeyError):
            log.warn('remove bug')

        wc = xlib.XWindowChanges()

        wc.border_width = self.old_border
        
        xlib.XGrabServer(samuraix.display)
        xlib.XConfigureWindow(samuraix.display, self.window, xlib.CWBorderWidth, byref(wc))
        xlib.XUngrabButton(samuraix.display, xlib.AnyButton, xlib.AnyModifier, self.window)
        xhelpers.set_window_state(self.window, xlib.WithdrawnState)
        xlib.XSync(samuraix.display, False)
        xlib.XUngrabServer(samuraix.display)

        self.dispatch_event('on_removed')

        for decoration in self.decorations:
            decoration.remove()
        
    def on_button_press(self, ev):
        modifiers = CLEANMASK(ev.state)
        log.debug("client %s button_press %s %s" % (self, ev.button, modifiers))
        try:
            func = self.config['buttons'][(ev.button, modifiers)]
        except KeyError:
            log.debug("no callback found for event")
        else:
            func(self)

    def grab_buttons(self):
        log.debug("grab_buttons %s %s" % (self, self.window))

        xlib.XGrabButton(samuraix.display, xlib.Button1, 
            xlib.NoSymbol,
            self.window, False, BUTTONMASK, xlib.GrabModeSync, xlib.GrabModeAsync, 
            xlib.None_, xlib.None_)
        xlib.XGrabButton(samuraix.display, xlib.Button1, 
            xlib.NoSymbol | xlib.LockMask,
            self.window, False, BUTTONMASK, xlib.GrabModeSync, xlib.GrabModeAsync, 
            xlib.None_, xlib.None_)
        xlib.XGrabButton(samuraix.display, xlib.Button1, 
            xlib.NoSymbol | xlib.NumLockMask,
            self.window, False, BUTTONMASK, xlib.GrabModeSync, xlib.GrabModeAsync, 
            xlib.None_, xlib.None_)
        xlib.XGrabButton(samuraix.display, xlib.Button1, 
            xlib.NoSymbol | xlib.NumLockMask | xlib.LockMask,
            self.window, False, BUTTONMASK, xlib.GrabModeSync, xlib.GrabModeAsync, 
            xlib.None_, xlib.None_)
        
        for button, modifiers in self.config['buttons'].iterkeys():
            xlib.XGrabButton(samuraix.display, button, 
                modifiers, 
                self.window, False, BUTTONMASK, xlib.GrabModeAsync, xlib.GrabModeSync,
                xlib.None_, xlib.None_)
            xlib.XGrabButton(samuraix.display, button, 
                modifiers | xlib.LockMask, 
                self.window, False, BUTTONMASK, xlib.GrabModeAsync, xlib.GrabModeSync,
                xlib.None_, xlib.None_)
            xlib.XGrabButton(samuraix.display, button, 
                modifiers | xlib.NumLockMask, 
                self.window, False, BUTTONMASK, xlib.GrabModeAsync, xlib.GrabModeSync,
                xlib.None_, xlib.None_)
            xlib.XGrabButton(samuraix.display, button, 
                modifiers | xlib.NumLockMask | xlib.LockMask, 
                self.window, False, BUTTONMASK, xlib.GrabModeAsync, xlib.GrabModeSync,
                xlib.None_, xlib.None_)
                
        self.screen.ungrab_buttons()

    def mousemove(self):
        if self.maximised:
            self.unmaximise()
            self.resize(self.floating_geom)

        root = self.screen.root_window
        if (xlib.XGrabPointer(samuraix.display, 
                root, 
                False, MOUSEMASK, xlib.GrabModeAsync, xlib.GrabModeAsync,
                root,
                samuraix.cursors['move'], xlib.CurrentTime) != xlib.GrabSuccess):
            return 

        dummy = xlib.Window()
        x = c_int()
        y = c_int()
        di = c_int()
        dui = c_uint()

        xlib.XQueryPointer(samuraix.display, root, byref(dummy), byref(dummy),
            byref(x), byref(y), byref(di), byref(di), byref(dui))

        x = x.value
        y = y.value

        ev = xlib.XEvent()

        ox = self.geom.x
        oy = self.geom.y

        geom = self.geom.copy()

        while True:
            
            xlib.XMaskEvent(samuraix.display, 
                MOUSEMASK | 
                xlib.ExposureMask | 
                xlib.SubstructureRedirectMask, byref(ev))

            if ev.type == xlib.ButtonRelease:
                xlib.XUngrabPointer(samuraix.display, xlib.CurrentTime)
                break
            elif ev.type == xlib.MotionNotify:
                geom.x = ox + (ev.xmotion.x - x)
                geom.y = oy + (ev.xmotion.y - y)
                self.resize(geom)
            else:
                samuraix.app.handle_event(ev)

        self.floating_geom = self.geom.copy()

    def mouseresize(self):
        if self.maximised:
            self.maximised = False

        self.resizing = True

        ocx = self.geom.x
        ocy = self.geom.y

        root = xlib.XRootWindow(samuraix.display, self.screen.num)

        dummy = xlib.Window()
        x = c_int()
        y = c_int()
        di = c_int()
        dui = c_uint()

        xlib.XQueryPointer(samuraix.display, root, byref(dummy), byref(dummy),
            byref(x), byref(y), byref(di), byref(di), byref(dui))

        omx = x.value
        omy = y.value

        if (xlib.XGrabPointer(samuraix.display, 
                root,
                False, MOUSEMASK, xlib.GrabModeAsync, xlib.GrabModeAsync,
                root,
                samuraix.cursors['resize'], xlib.CurrentTime) != xlib.GrabSuccess):
            return 

        #xlib.XGrabServer(samuraix.display)
        
        gc = xlib.XCreateGC(samuraix.display, self.window, 0, None)
        xlib.XSetForeground(samuraix.display, gc, self.screen.white_pixel)
        xlib.XSetFunction(samuraix.display, gc, xlib.GXxor)
        xlib.XSetSubwindowMode(samuraix.display, gc, xlib.IncludeInferiors)
        xlib.XSetBackground(samuraix.display, gc, self.screen.white_pixel)

        xlib.XWarpPointer(samuraix.display, xlib.None_, self.window, 0, 0, 0, 0,
            self.geom.width + self.border_width - 1, self.geom.height + self.border_width - 1)   

        ev = xlib.XEvent()

        geom = self.geom.copy()

        xlib.XDrawRectangle(samuraix.display, root, gc, 
                geom.x, geom.y, geom.width, geom.height)
        xlib.XFlush(samuraix.display)
        xlib.XSync(samuraix.display, 0)

        ev = xlib.XEvent()

        while True:

            #xlib.XNextEvent(samuraix.display, byref(ev))

            xlib.XMaskEvent(samuraix.display, 
                MOUSEMASK | xlib.ExposureMask | xlib.SubstructureRedirectMask,
                byref(ev))

            if ev.type == xlib.ButtonRelease:
                xlib.XUngrabPointer(samuraix.display, xlib.CurrentTime)
                break
            elif ev.type == xlib.MotionNotify:
                # erase the old box 
                xlib.XDrawRectangle(samuraix.display, root, gc, 
                        geom.x, geom.y, geom.width, geom.height)

                geom.width = max(0, ev.xmotion.x - ocx - 2 * self.border_width + 1)
                geom.height = max(0, ev.xmotion.y - ocy - 2 * self.border_width + 1)

                xlib.XDrawRectangle(samuraix.display, root, gc, 
                        geom.x, geom.y, geom.width, geom.height)
                xlib.XFlush(samuraix.display)
                xlib.XSync(samuraix.display, 0)
            else:
                samuraix.app.handle_event(ev)

        # erase the box
        xlib.XDrawRectangle(samuraix.display, root, gc, 
                geom.x, geom.y, geom.width, geom.height)

        xlib.XWarpPointer(samuraix.display, xlib.None_, root, 0, 0, 0, 0, omx, omy)   

        xlib.XFlush(samuraix.display)
        xlib.XSync(samuraix.display, 0)

        #xlib.XUngrabServer(samuraix.display)
        xlib.XFreeGC(samuraix.display, gc)

        self.resize(geom)
        self.floating_geom = self.geom.copy()
        self.resizing = False
        self.update_decorations()
                
    def on_enter(self):
        log.debug("enter %s" % self)
        self.grab_buttons()

        #if samuraix.config['focus'] == 'sloppy':
        #    self.desktop.focus_client(self)

    def ban(self):
        log.debug('banning %s' % self)
        xlib.XUnmapWindow(samuraix.display, self.window)
        xhelpers.set_window_state(self.window, xlib.IconicState)
        for decoration in self.decorations:
            decoration.ban()

    def unban(self):
        log.debug('unbanning %s' % self)
        xlib.XMapWindow(samuraix.display, self.window)
        xhelpers.set_window_state(self.window, xlib.NormalState)
        for decoration in self.decorations:
            decoration.unban()
                
    def move_to_desktop(self, desktop):
        log.debug('move to desktop %s %s' % (self, desktop))
        self.desktop.remove_client(self)
        desktop.add_client(self)
        

Client.register_event_type('on_button_press')
Client.register_event_type('on_enter')
Client.register_event_type('on_focus')
Client.register_event_type('on_blur')
Client.register_event_type('on_removed')
Client.register_event_type('on_title_changed')


