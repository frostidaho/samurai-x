from pyglet.window.xlib import xlib 
import samuraix
from samuraix.sxctypes import *

import logging
log = logging.getLogger(__name__)

class SimpleWindow(object):
    
    def __init__(self, screen, geom, border_width=0):
        self.screen = screen
        self.geom = geom 
        if border_width is None:
            border_width = 1
        self.border_width = border_width

        wa = xlib.XSetWindowAttributes()
        wa.event_mask = (xlib.SubstructureRedirectMask |
                         xlib.SubstructureNotifyMask |
                         xlib.EnterWindowMask | 
                         xlib.LeaveWindowMask | 
                         xlib.StructureNotifyMask |
                         xlib.ButtonPressMask | 
                         xlib.KeyPressMask | 
                         xlib.ExposureMask)

        wa.override_redirect = 1
        wa.background_pixmap = xlib.ParentRelative

        root = screen.root_window
        default_depth = screen.default_depth
        self.window = xlib.XCreateWindow(samuraix.display, root, 
                            geom.x, geom.y, geom.width, geom.height,
                            self.border_width,
                            default_depth,
                            xlib.CopyFromParent,
                            screen.default_visual,
                            xlib.CWOverrideRedirect | xlib.CWBackPixmap | xlib.CWEventMask,
                            byref(wa))

        xlib.XSelectInput(samuraix.display, self.window, wa.event_mask)

        self.drawable = xlib.XCreatePixmap(samuraix.display, root, 
                            geom.width, geom.height,
                            default_depth)

    def delete(self):
        xlib.XDestroyWindow(samuraix.display, self.window)
        xlib.XFreePixmap(samuraix.display, self.drawable)
    
    def move(self, x, y):
        self.geom.x = x
        self.geom.y = y
        return xlib.XMoveWindow(samuraix.display, self.window, x, y)

    def resize(self, width, height):
        self.geom.width = width
        self.geom.height = height 
        xlib.XFreePixmap(samuraix.display, self.drawable)
        self.drawable = xlib.XCreatePixmap(samuraix.display, self.screen.root_window, 
                width, height, self.screen.default_depth)
        return xlib.XResizeWindow(samuraix.display, self.window, width, height)

    def refresh_drawable(self):
        #log.debug('refresh drawable %s' % self)
        xlib.XCopyArea(samuraix.display, self.drawable, self.window,
                xlib.XDefaultGC(samuraix.display, self.screen.num), 0, 0,
                self.geom.width, self.geom.height, 0, 0)





