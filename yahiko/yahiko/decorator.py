# Copyright (c) 2008-2009, samurai-x.org
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

import logging
log = logging.getLogger(__name__)

from samuraix import config
from samuraix.plugin import Plugin
from samuraix.cairo_ext import create_surface
from samuraix.rect import Rect
from ooxcb import xproto
from ooxcb.contrib import cairo

from sxbind import MODIFIERS # Oh no, we depend on sxbind! TODO? (maybe move into samuraix.contrib or something like that?)
from sxactions import ActionInfo

from yahiko import ui

def compute_window_geom(geom):
    """ convert the 'frame geom' to the 'window geom' """
    geom.y += config['cairodeco.height']
    geom.height -= config['cairodeco.height']


def compute_actor_geom(geom):
    """ convert the 'window geom' to the 'geom geom' """
    geom.y = max(0, geom.y - config['cairodeco.height'])
    geom.height = max(1, geom.height + config['cairodeco.height'])


def hex_to_cairo_color(color):
    """
        convert a color in hexadecimal form (e.g. '#ff00ee').
        return a 3-element tuple of (R, G, B), where R, G
        and B are 0..255.
    """
    color = color.lstrip('#')
    return tuple(int(p, 16) for p in (color[:2], color[2:4], color[4:]))


class ClientWindow(ui.Window):
    def __init__(self, window):
        self.window = window 
        ui.Window.__init__(self)

    def set_render_coords(self, x, y, width, height):
        ui.Window.set_render_coords(self, x, y, width, height)
        self.window.configure(x=x, y=y, width=width, height=height)


class Decorator(object):
    def __init__(self, plugin, screen, client):
        self.plugin = plugin
        self.client = client
        self.screen = screen

        self._obsolete = False
        self._active = True

        # This counter ensures that we don't run into
        # an infinite loop. If the window is configured,
        # we configure the actor. If the actor is configured,
        # we configure the window --> much fun.
        # Now, we increment the counter if we configure the
        # window. The actor will only be configured if
        # the counter equals 0. If it is greater than 0,
        # it is simply decremented.
        # Maybe that's not necessary, but it seems to be.
        self._window_configures = 0

        self.watched_atoms = [plugin.app.conn.atoms[name] for name in
                ["WM_NAME", "_NET_WM_NAME", "_NET_WM_VISIBLE_NAME"]
                ]

        self.create_actor_window()

    def create_actor_window(self):
        screen = self.screen
        client = self.client
        colormap = client.window.get_attributes().reply().colormap
        config = self.plugin.config

        geom = self.client.window.get_geometry().reply()
        # dont know how to get this from client.window so setting it to 0 
        client.window.configure(border_width=0)
        window_border = 0

        client.actor = xproto.Window.create(self.plugin.app.conn,
                screen.root,
                screen.info.root_depth,
                screen.info.root_visual,
                geom.x,
                geom.y,
                # dont forget the borders of client.border in this calculation
                geom.width + (2*config['border']) + (2*window_border),
                geom.height + config['title'] + (2*config['border']) + (2*window_border),
                override_redirect=True,
                back_pixel=screen.info.white_pixel,
                colormap=colormap,
                event_mask=
                    xproto.EventMask.Exposure |
                    xproto.EventMask.StructureNotify |
                    # Child.StructureNotify and Parent.SubstructureNotify
                    # seem to block each other. That's not what we want.
                    # I commented this out, and it seems to work.
                    #xproto.EventMask.SubstructureNotify |
                    xproto.EventMask.ButtonPress,
                )

        client.window.reparent(client.actor)

        client.actor.map()
        log.debug('created client actor client=%s actor=%s', client, client.actor)
        
        self.ui = ui.TopLevelContainer(
                client.actor, 
                screen.info.get_root_visual_type(),
                style={
                    'background': {
                        'color': (0.2, 0.2, 0.2),
                        'style': 'gradient',
                        'fill-line': (0.0, 0.0, 0.0, 20.0),
                        'fill-stops': [
                            (0.0, 0.2, 0.2, 0.2),
                            (0.3, 0.7, 0.7, 0.75),
                            (1.0, 0.4, 0.4, 0.4),
                        ],
                    },
                    'border': {
                        'color': (255, 255, 255),
                        'width': 1.0,
                    },
                    'layout': {
                        'padding': 5,
                    },
                },
                layouter=ui.VerticalLayouter,
        )
        window_title = self.client.get_window_title().encode('utf-8') # <- TODO: is that too expensive?
        self.title = ui.Label(
            text=window_title,
            height=20,
            style={
                'text': {
                    'color': (0, 0, 0),
                }
            }
        )
        self.clientwin = ClientWindow(client.window)
        self.ui.add_children([self.title, self.clientwin])
        self.ui.layout()
        self.ui.render()

        client.push_handlers(
                on_focus=self.on_focus,
                #on_updated_geom=self.on_updated_geom,
                on_blur=self.on_blur,
        )

        client.window.push_handlers(
                on_property_notify=self.on_property_notify,
                #on_unmap_notify=self.on_unmap_notify,
                #on_map_notify=self.on_map_notify,
        )
        # TODO: dirty. something's wrong with substructure and structure notify.
        #client.screen.root.push_handlers(
        #        #on_configure_notify=self.screen_on_configure_notify,
        #)

    def on_focus(self, client):
        if (self._active and not self._obsolete):
            self.ui.render()

    def on_blur(self, client):
        if (self._active and not self._obsolete):
            self.ui.render()

    def on_property_notify(self, evt):
        """
            if a window changes a watched atom, redraw
            the title bar.
        """
        if (evt.atom in self.watched_atoms and not self._obsolete):
            self.title.text = self.client.get_window_title().encode('utf-8') # <- TODO: is that too expensive?
            self.ui.render()

    def remove(self):
        # TODO
        pass


class DecoratorPlugin(Plugin):
    key = 'decoration'

    def __init__(self, app):
        self.app = app
        app.push_handlers(self)
        self.bindings = {}

        self.config = {
            'border': 5,
            'title': 12,
        }


    def on_ready(self, app):
        for screen in app.screens:
            screen.push_handlers(self)
            for client in screen.clients:
                self.create_decoration(screen, client)

    def on_new_client(self, screen, client):
        self.create_decoration(screen, client)

    def on_unmanage_client(self, screen, client):
        self.get_data(client).remove()

    def create_decoration(self, screen, client):
        # to have proper transparency, the actor window
        # has to use the same colormap as the foreign window.
        decorator = Decorator(self, screen, client)
        self.attach_data_to(client, decorator)

    def emit_action(self, client, evt):
        stroke = (evt.state, evt.detail)
        if stroke in self.bindings:
            info = ActionInfo(screen = self.app.get_screen_by_root(evt.root),
                    x=evt.event_x,
                    y=evt.event_y,
                    client=client) # TODO: no additional info? :/
            # ... call the action
            self.app.plugins['actions'].emit(self.bindings[stroke], info)

