import logging
log = logging.getLogger(__name__)

from samuraix.plugin import Plugin
from samuraix.rect import Rect
from ooxcb import xproto

BAR_HEIGHT = 20

def compute_window_geom(geom):
    """ convert the 'frame geom' to the 'window geom' """
    geom.y += BAR_HEIGHT
    geom.height -= BAR_HEIGHT

def compute_actor_geom(geom):
    """ convert the 'window geom' to the 'geom geom' """
    geom.y = max(0, geom.y - BAR_HEIGHT)
    geom.height = max(1, geom.height + BAR_HEIGHT)

class ClientData(object):
    def __init__(self, plugin, screen, client):
        self.plugin = plugin
        self.client = client

        self._obsolete = False
        self._active = True
        
        self.gc = xproto.GContext.create(self.client.conn,
                self.client.actor,
                foreground=screen.info.black_pixel,
                background=screen.info.white_pixel
                )

        self.client.actor.push_handlers(on_configure_notify=self.actor_on_configure_notify,
                on_expose=self.on_expose,
                on_unmap_notify=self.on_unmap_notify,
                on_map_notify=self.on_map_notify
                )
        self.client.window.push_handlers(on_property_notify=self.on_property_notify)

    def on_expose(self, evt):
        if (self._active and not self._obsolete):
            self.redraw()

    def on_unmap_notify(self, evt):
        if not self._obsolete:
            self._active = False
            self.client.actor.unmap()
            self.client.conn.flush()

    def on_map_notify(self, evt):
        if not self._obsolete:
            self._active = True
            self.client.actor.map()
            self.client.conn.flush()

    def on_property_notify(self, evt):
        """
            if a window changes a watched atom, redraw
            the title bar.
        """
        if evt.atom in self.plugin.watched_atoms:
            self.redraw()

    def redraw(self):
        self.client.actor.clear_area(0, 0, self.client.geom.width, self.client.geom.height)

        wm_name = self.client.window.get_property("WM_NAME", "STRING").reply().value.to_string()
        print wm_name
        self.gc.image_text8(self.client.actor, 1, BAR_HEIGHT - 4, wm_name)
        self.client.conn.flush()

    def actor_on_configure_notify(self, evt):
        """ if the actor is configured, configure the window, too """
        geom = Rect(width=evt.width, height=evt.height)
        compute_window_geom(geom)
        self.client.window.configure(**geom.to_dict()) # TODO: is that efficient?
        self.client.conn.flush()

#    def window_on_configure_notify(self, evt):
#        """ if the window is configured, configure the actor, too """
#        geom = self.client.geom.copy()
#        compute_actor_geom(geom)
#        self.client.actor.configure(**geom.to_dict())
#        self.client.conn.flush()

    def remove(self):
        """ the end. """
        self.client.actor.destroy()
        self.gc.free()
        self.client.conn.flush()
        del self.client
        self._obsolete = True

class SXDeco(Plugin):
    key = 'decoration'

    def __init__(self, app):
        self.app = app
        app.push_handlers(self)

        self.watched_atoms = [self.app.conn.atoms[name] for name in
                ["WM_NAME"]
                ]

    def on_ready(self, app):
        for screen in app.screens:
            screen.push_handlers(self)
            for client in screen.clients:
                self.create_client_data(screen, client)
        
    def on_new_client(self, screen, client):
        self.create_client_data(screen, client)

    def on_unmanage_client(self, screen, client):
        self.get_data(client).remove()

    def create_client_data(self, screen, client):
        client.actor = xproto.Window.create(self.app.conn, 
                screen.root,
                screen.info.root_depth,
                screen.info.root_visual,
                client.geom.x,
                client.geom.y,
                client.geom.width,
                client.geom.height,
                override_redirect=True,
                back_pixel=screen.info.white_pixel,
                event_mask=
                    xproto.EventMask.Exposure | 
                    xproto.EventMask.StructureNotify | 
                    xproto.EventMask.SubstructureNotify,
                )
        client.window.reparent(client.actor, 0, BAR_HEIGHT)

        self.attach_data_to(client, ClientData(self, screen, client))
        client.actor.map()
        log.debug('created client actor %s', client)

