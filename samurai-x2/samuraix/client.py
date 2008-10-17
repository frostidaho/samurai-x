import weakref

import samuraix.event
import samuraix.drawcontext
import samuraix.xcb, samuraix.xcb._xcb
from samuraix import cairo

from .rect import Rect

import logging 
log = logging.getLogger(__name__)

class Client(samuraix.event.EventDispatcher):
    all_clients = []
    window_2_client_map = weakref.WeakValueDictionary()
    
    all_frames = []
    window_2_frame_map = weakref.WeakValueDictionary()

    class ClientHandler(object):
        def __init__(self, client, x, y):
            self.client = client
            self.offset_x, self.offset_y = x, y
        
        def on_motion_notify(self, evt):
            pass

        def on_button_releae(self, evt):
            pass

    class MoveHandler(ClientHandler):
        def __init__(self, client, x, y):
            super(Client.MoveHandler, self).__init__(client, x, y)
            client.screen.root.grab_pointer()

        def on_motion_notify(self, evt):
            self.client.frame.configure(x=evt.root_x-self.offset_x, y=evt.root_y - self.offset_y)
            return True

        def on_button_release(self, evt):
            self.client.screen.root.remove_handlers(self)
            self.client.screen.root.ungrab_pointer()
            self.client.force_update_geom()
            return True

    class ResizeHandler(ClientHandler):
        def __init__(self, client, x, y):
            super(Client.ResizeHandler, self).__init__(client, x, y)
            client.screen.root.grab_pointer()

        def on_motion_notify(self, evt):
            return True

        def on_button_release(self, evt):
            geom = self.client.geom
            w = evt.root_x - geom.x
            h = evt.root_y - geom.y

            self.client.window.resize(geom.x, geom.y, w, h)

            self.client.frame.resize(geom.x-self.client.style['border'],
                    geom.y-(self.client.style['title_height']+self.client.style['border']),
                    w+self.client.style['border']*2,
                    h+self.client.style['title_height']+(self.client.style['border']*2))

            self.client.window.reparent(self.client.frame, self.client.style['border'], self.client.style['border'] + self.client.style['title_height'])

            #configure(width=w, height=h)

            self.client.screen.root.remove_handlers(self)
            self.client.screen.root.ungrab_pointer()
            self.client.force_update_geom()
            self.client._recreate_context()
            self.client.frame_on_expose(None)
            return True

    @classmethod
    def get_by_window(cls, window):
        return cls.window_2_client_map.get(window)

    def __init__(self, screen, window, wa, geometry):
        self.screen = screen
        self.window = window
        self.window.attributes = {'event_mask': (samuraix.xcb.event.StructureNotifyEvent,)}

        self.geom = Rect(geometry['x'], geometry['y'], geometry['width'], geometry['height'])

        self.all_clients.append(self)
        self.window_2_client_map[self.window] = self

        self.create_frame()
        self.window.map()

        self.window.push_handlers(self)

        self._moving = False
        self._resizing = False

    def on_configure_notify(self, evt):
        self.force_update_geom() # TODO. ugly

    def create_frame(self):
        self.frame_geom = frame_geom = self.geom.copy()

        self.style = dict(
            title_height=20,
            border=3,
        )

        frame_geom.height += self.style['title_height'] + (self.style['border'] * 2)
        frame_geom.width += self.style['border'] * 2
        frame_geom.x -= self.style['border']
        frame_geom.y -= self.style['title_height'] + self.style['border']
        frame = samuraix.xcb.window.Window.create(
                self.screen.connection,
                self.screen,
                frame_geom.x,
                frame_geom.y,
                frame_geom.width,
                frame_geom.height,
                1,
                attributes={'event_mask': (samuraix.xcb.event.ExposeEvent,
                                         samuraix.xcb.event.ButtonPressEvent,
                                         samuraix.xcb.event.ButtonReleaseEvent),
                           'override_redirect': True},
        )

        self.window.reparent(frame, self.style['border'], self.style['border'] + self.style['title_height'])
        frame.map()
        frame.set_handler('on_button_press', self.frame_on_button_press)
        #frame.set_handler('on_button_release', self.frame_on_button_release)
        frame.set_handler('on_expose', self.frame_on_expose)

        #context = samuraix.drawcontext.DrawContext(self.screen, frame_geom.width, frame_geom.height, frame)
        #context.text(0, 0, self.window.get_property('WM_NAME')[0], (0, 255, 255))

        self.frame = frame

        self._recreate_context()

    def update_geom(self, geometry):
        if isinstance(geometry, dict):
            geometry = Rect(geometry['x'], geometry['y'], geometry['width'], geometry['height'])
        self.geom = geometry
        self.frame_geom = frame_geom = self.geom.copy()
        frame_geom.height += self.style['title_height'] + (self.style['border'] * 2)
        frame_geom.width += self.style['border'] * 2
        frame_geom.x -= self.style['border']
        frame_geom.y -= self.style['title_height'] + self.style['border']
        print "%s geom %s" % (self, geometry)
        self.frame_on_expose(None)

    def frame_on_button_press(self, evt):
        if evt.detail == 1:
            self._moving = True
            #assert self.screen.root.grab_pointer()
            # TODO this should push a class not just some functions
            #self.screen.root.push_handlers(on_motion_notify=self.moving_motion_notify, on_button_release=self.moving_release)
            self.screen.root.push_handlers(self.MoveHandler(self, evt.event_x, evt.event_y))
        if evt.detail == 3:
            self.screen.root.push_handlers(self.ResizeHandler(self, evt.event_x, evt.event_y))

    def force_update_geom(self):
        self.update_geom(self.window.get_geometry())

    def _recreate_context(self):
        self.context = samuraix.drawcontext.DrawContext(
                self.screen, 
                self.frame_geom.width+1, self.frame_geom.height+1, 
                self.frame
        )

    def frame_on_expose(self, evt):
        log.warn('expose! %s', self)

        context = self.context
        cr = context.cr
        
        if False:
            context.fill((255, 0, 255))
            context.text(0, 10, self.window.get_property('WM_NAME')[0], (255, 255, 255))
            # fred: why do I have to set y=10?
            # dunk: because its specifying the baseline of the text not the top 
        else:
            g = self.frame.get_geometry()
            log.warn(str((g, dir(g))))

            cairo.cairo_set_antialias(cr, cairo.CAIRO_ANTIALIAS_NONE)
            cairo.cairo_set_line_width(cr, 1)
            cairo.cairo_set_source_rgb(cr, 0.8, 0.0, 0.0)
            cairo.cairo_rectangle(cr, 0, 0, g['width']-1, g['height']-1)
            cairo.cairo_fill_preserve(cr)
            cairo.cairo_set_source_rgb(cr, 1.0, 1.0, 1.0)
            cairo.cairo_stroke(cr)

            context.text(
                    self.style['border'] + 1, 
                    self.style['border'] + 1 + context.default_font_size, 
                    self.window.get_property('WM_NAME')[0], 
                    (255, 255, 255)
            )

            # TODO should the client know its own connection?
            self.window.connection.flush()

