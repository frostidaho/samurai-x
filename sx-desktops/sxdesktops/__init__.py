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

"""
    sx-desktops is a plugin that enables multiple desktops in samurai-x.

    Dependencies
    ------------

    sx-desktops depends on :ref:`sx-actions`.

    Configuration
    -------------

    .. attribute:: desktops.desktops

        A list of tuples of (desktop name, desktop info dictionary).
        sx-desktops itself doesn't define any desktop information
        keys, but e.g. :ref:`sx-layoutmgr` does.

        An example::

            'desktops.desktops': [
                ('desktop number one', {'layout': 'floating'}),
                ('oh, just another desktop', {'layout': 'vert'})
             ]

    .. attribute:: desktops.autofocus

        If `desktops.autofocus` is True, a new client is automatically
        focused.

        Default value: True

    Actions
    -------

    .. function:: desktops.cycle([offset=1])
        :module:

        Cycle desktops by *offset*. Positive values mean
        forward cycling, negative values mean backwards cycling.

        Required parameters:
            * `screen`

    .. function:: desktops.cycle_clients([offset=1])
        :module:

        Cycle the clients of the current desktop by *offset*.

        Required parameters:
            * `screen`

    .. function:: desktops.goto(index)
        :module:

        go to the desktop with the index *index*.

        Required parameters:
            * `screen`
            * `index`

"""

import logging
log = logging.getLogger(__name__)

from samuraix import config
from samuraix.client import Client
from samuraix.plugin import Plugin
from ooxcb.list import List
from ooxcb.eventsys import EventDispatcher
from samuraix.base import SXObject

def cycle_indices(current, offset, length):
    """
        Return the index `current`, cycled
        by `offset` indices.
    """
    return ((current or length) + offset) % length


class FocusStack(list):
    """ 
        focus stack implementation based on a list 
    
        the last item in the list is the focused item
    """

    def __init__(self, conn, *args):
        self.conn = conn 
        list.__init__(self, *args)

    def sort(self):
        list.sort(self, cmp = self._sort)

    def _sort(self, client_a, client_b):
        # from: 
        # http://standards.freedesktop.org/wm-spec/wm-spec-1.3.html#STACKINGORDER

        # Stacking order

        # To obtain good interoperability between different Desktop 
        # Environments, the following layered stacking order is 
        # recommended, from the bottom:
        #
        #    * windows of type _NET_WM_TYPE_DESKTOP
        #    * windows having state _NET_WM_STATE_BELOW
        #    * windows not belonging in any other layer
        #    * windows of type _NET_WM_TYPE_DOCK 
        #      (unless they have state _NET_WM_TYPE_BELOW) and windows 
        #      having state _NET_WM_STATE_ABOVE
        #    * focused windows having state _NET_WM_STATE_FULLSCREEN
        #
        # Windows that are transient for another window should be kept above this
        # window.
        #
        # The window manager may choose to put some windows in different stacking
        # positions, for example to allow the user to bring currently a active 
        # window to the top and return it back when the window looses focus. 

        if (    self.conn.atoms['_NET_WM_WINDOW_TYPE_DESKTOP'] in client_a.window_type
            and self.conn.atoms['_NET_WM_WINDOW_TYPE_DESKTOP'] not in client_b.window_type):
            return -1
        elif (  self.conn.atoms['_NET_WM_WINDOW_TYPE_DESKTOP'] not in client_a.window_type
            and self.conn.atoms['_NET_WM_WINDOW_TYPE_DESKTOP'] in client_b.window_type):
            return 1
        if (    self.conn.atoms['_NET_WM_STATE_BELOW'] in client_a.state 
            and self.conn.atoms['_NET_WM_STATE_BELOW'] not in client_b.state):
            return -1
        elif (  self.conn.atoms['_NET_WM_STATE_BELOW'] not in client_a.state 
            and self.conn.atoms['_NET_WM_STATE_BELOW'] in client_b.state):
            return 1
        if (    self.conn.atoms['_NET_WM_TYPE_DOCK'] in client_a.state
            and self.conn.atoms['_NET_WM_TYPE_DOCK'] not in client_b.state):
            return -1
        elif (  self.conn.atoms['_NET_WM_TYPE_DOCK'] not in client_a.state
            and self.conn.atoms['_NET_WM_TYPE_DOCK'] in client_b.state):
            return 1
        if (    self.conn.atoms['_NET_WM_STATE_FULLSCREEN'] in client_a.state
            and self.conn.atoms['_NET_WM_STATE_FULLSCREEN'] not in client_b.state):
            return -1
        elif (  self.conn.atoms['_NET_WM_STATE_FULLSCREEN'] not in client_a.state
            and self.conn.atoms['_NET_WM_STATE_FULLSCREEN'] in client_b.state):
            return 1

        # TODO should compare x stacking order here?

        return 0

    # define our own append so we can insert the client in the right place 
    def append(self, client):
        # TODO make this much more clever... we just need to loop to the 
        # right point 
        list.append(self, client)
        #self.sort()
        
    def move_to_top(self, client):
        if self.current() is client:
            return
        try:
            self.remove(client)
            self.append(client)
        except IndexError:
            log.warn('cant move client %s to top! not in list!' % client)

    def prev(self):
        c = self.pop(-1)
        self.insert(0, c)
        return self.current()

    def next(self):
        c = self.pop(0)
        self.append(c)
        return self.current()

    def current(self):
        try:
            return self[-1]
        except IndexError:
            return None

    def contains_manager(self, window):
        """
            returns True if the focus stack contains any
            client managing the window *window*.
        """
        for client in self:
            if client.window is window:
                return True
        return False


class Desktop(SXObject):
    def __init__(self, plugin, screen, name, idx, config):
        SXObject.__init__(self)

        self.plugin = plugin
        self.screen = screen
        self.name = name
        self.clients = FocusStack(self.screen.conn) # maybe weak references are a good idea.
        self.idx = idx
        self.config = config

    def __repr__(self):
        return '<Desktop "%s">' % self.name

    @property
    def active(self):
        return self.plugin.get_data(self.screen).active_desktop is self

    def on_focus(self, client):
        """ a client was focused: move it to top of the focus stack """
        self.clients.move_to_top(client)
        self.rearrange()

    def on_before_focus(self, client):
        """
            s-x attempts to focus a client.
            If the client is not member of the currently active desktop,
            activate its desktop.

            .. todo:: should this behaviour be configurable?
        """
        if (not self.active 
            and not client.conn.atoms['_NET_WM_STATE_STICKY'] in client.state):
            idx = client.window.ewmh_get_desktop()
            self.plugin.get_data(self.screen).set_active_desktop_idx(idx)

    def add_client(self, client):
        self.clients.append(client)
        self.dispatch_event('on_new_client', self, client)

        # add handlers for the desktop-specific client messages
        # FIXME i dont think we clean up after these properly in remove_client
        client.client_message_handlers.register_handler(
                client.conn.atoms['_NET_WM_DESKTOP'],
                self.handle_net_wm_desktop)

        client.push_handlers(
                on_focus=self.on_focus,
                on_before_focus=self.on_before_focus
                )
        client.window.change_property(
                '_NET_WM_DESKTOP',
                'CARDINAL',
                32,
                [self.idx])

        # check if the desktop is the active one. if not,
        # "iconify" the client. openbox says that
        # icccm 4.1.3.1 says that.
        if self.active:
            client.unban()
        elif client.conn.atoms['_NET_WM_STATE_STICKY'] not in client.state:
            client.ban(False, False)

        client.conn.flush()
        if self.active:
            self.rearrange()

    def handle_net_wm_desktop(self, evt):
        """
            handle the _NET_WM_DESKTOP client message. Somebody
            is requesting to change the desktop of the client.
        """
        client = Client.get_by_window(evt.window)
        if client: # but shouldnt ever be invalid.
            new_idx = evt.data.data32[0]
            if new_idx == self.idx: # doesn't change anything, so don't do anything.
                pass
            elif new_idx == 0xffffffff: # TODO: show on all desktops
                log.warning('%s requests to be shown on all desktops - not implemented' % client)
            else:
                if not new_idx < len(desktops):
                    log.warning('%s requests to be shown on desktop %d - no such desktop' % new_idx)
                else:
                    desktop = desktops[new_idx]
                    self.move_client_to_desktop(client, desktop)

    def move_client_to_desktop(self, client, desktop):
        log.debug('Moving %s to desktop %s' % (client, desktop))
        self.remove_client(client)
        desktops = self.plugin.get_data(self.screen).desktops
        desktop.add_client(client)

    def rearrange(self):
        self.dispatch_event('on_rearrange', self)

    def remove_client(self, client):
        try:
            self.clients.remove(client)
        except ValueError:
            return False
        else:
            client.remove_handlers(
                    on_focus=self.on_focus,
                    on_before_focus=self.on_before_focus
                    )
            self.dispatch_event('on_unmanage_client', self, client)
            return True
    
    def calculate_work_area(self):
        return (0, 0, self.screen.root.width, self.screen.root.height)


Desktop.register_event_type('on_new_client')
Desktop.register_event_type('on_rearrange')
Desktop.register_event_type('on_unmanage_client')

class ScreenData(EventDispatcher):
    def __init__(self, screen, desktops):
        EventDispatcher.__init__(self)

        self.screen = screen
        self.desktops = desktops
        self.active_desktop = desktops[0]
        self.active_desktop_idx = 0
        self.update_hints()

        self.screen.push_handlers(self)
        self.install_handlers()

    def msg_current_desktop(self, evt):
        """
            handler for the _NET_CURRENT_DESKTOP client message
        """
        self.set_active_desktop_idx(evt.data.data32[0])

    def install_handlers(self):
        self.screen.client_message_handlers.register_handler(
                self.screen.conn.atoms['_NET_CURRENT_DESKTOP'],
                self.msg_current_desktop)

    # we have a handler for on_after_new_client here. This event
    # is dispatched after the client has been initialized
    # and the actor has been set. This ensures that the input
    # focus is set correctly. It wouldn't work if the client
    # was focused in a on_new_client handler.
    def on_after_new_client(self, screen, client):
        self.add_client(client)

    def add_client(self, client):
        """
            add a client. if the window as a _NET_WM_DESKTOP example,
            respect it, otherwise place it on the active desktop.
        """
        desktops = [self.active_desktop]
        reply = client.window.get_property('_NET_WM_DESKTOP', 'CARDINAL').reply()
        if reply.exists:
            # has a property like this
            desktop_idx = reply.value[0]
            if desktop_idx < len(self.desktops):
                # we have this desktop!
                log.debug('Placing %s on desktop %d' % (client, desktop_idx))
                desktops = [self.desktops[desktop_idx]]
            elif desktop_idx == 0xffffffff:
                desktops = self.desktops

        if self.screen.conn.atoms['_NET_WM_STATE_STICKY'] in client.state:
            desktops = self.desktops

        for desktop in desktops:
            # so, either the window doesn't have this property
            # or we don't have this desktop index, so place it on the active desktop
            desktop.add_client(client)

            # should it be focused automatically? but don't do if it isn't
            # the active desktop
            if (desktop.active and config.get('desktops.autofocus', True)):
                self.screen.focus(client)

    def on_unmanage_client(self, screen, client):
        for desktop in self.desktops:
            if desktop.remove_client(client):
                break # a client is only on one desktop
        else:
            log.error('Could not unmanage client %s' % client)
            return
        # display the next one ...
        #self.screen.focus(self.active_desktop.clients.current())
        self.active_desktop.rearrange()

    def set_active_desktop(self, desktop):
        #assert desktop in self.desktops # let's trust the user
        prev = self.active_desktop
        self.active_desktop = desktop
        self.active_desktop_idx = self.desktops.index(desktop)
        self.dispatch_event('on_change_desktop', self, prev)

    def update_hints(self):
        """
            Update _NET_CURRENT_DESKTOP.
        """
        self.screen.root.change_property('_NET_CURRENT_DESKTOP',
                'CARDINAL', 32, [self.active_desktop_idx])
        self.screen.conn.flush()

    def on_change_desktop(self, fles, prev):
        self.update_clients(prev)
        self.update_hints()
        # focus any client on the new desktop,
        # we don't want an off screen focus.
        self.screen.focus(self.active_desktop.clients.current())

    def set_active_desktop_idx(self, idx):
        prev = self.active_desktop
        self.active_desktop_idx = idx
        self.active_desktop = self.desktops[idx]
        self.dispatch_event('on_change_desktop', self, prev)

    def update_clients(self, previous_desktop):
        """
            ban and unban clients
        """
        log.debug('... updating %s %s %s' % (previous_desktop,
            self.active_desktop, previous_desktop.clients))
        if previous_desktop != self.active_desktop:
            for client in previous_desktop.clients:
                # just iconify (see icccm 4.1.3.1), but don't set
                # _NET_WM_STATE_HIDDEN, because it is invisible
                # because it isn't on the current desktop, not
                # because the user has banned it.
                client.ban(False, False)

            for client in self.active_desktop.clients:
                client.unban()

    def cycle_desktops(self, offset=+1):
        self.set_active_desktop_idx(cycle_indices(self.active_desktop_idx,
            offset, len(self.desktops)))

    def cycle_clients(self, offset=+1):
        clients = self.active_desktop.clients
        self.screen.focus(clients.next()) # TODO: respect offset

    def move_client_to_desktop(self, client, new_desktop):
        for desktop in self.desktops:
            if client in desktop.clients:
                desktop.move_client_to_desktop(client, new_desktop)
                break

    def update_workarea(self):
        for desktop in self.desktops:
            pass
            

ScreenData.register_event_type('on_change_desktop')


class ClientData(object):
    def __init__(self, desktop, client):
        self.client = client
        self.desktop = desktop


class SXDesktops(Plugin):
    # atm, every screen has the same amount of desktops
    key = 'desktops'

    def __init__(self, app):
        self.app = app
        self.config = {}

        app.push_handlers(self)
        app.plugins['actions'].register('desktops.cycle', self.action_cycle)
        app.plugins['actions'].register('desktops.cycle_clients',
                self.action_cycle_clients)
        app.plugins['actions'].register('desktops.goto', self.action_goto)
        app.plugins['actions'].register('desktops.move_client', self.action_move_client)

        atoms = app.conn.atoms
        app.supported_hints.update([
            atoms['_NET_NUMBER_OF_DESKTOPS'], 
            atoms['_NET_CURRENT_DESKTOP'],
            atoms['_NET_DESKTOP_GEOMETRY'],
            atoms['_NET_DESKTOP_VIEWPORT'],
            atoms['_NET_DESKTOP_NAMES'],
            #atoms['_NET_WORKAREA'], # TODO
        ])

    def on_load_config(self, config):
        #self.names = config.get('desktops.names', ['one desktop'])
        self.config = config.get('desktops.desktops', ())

    #def on_ready(self, app):
    #    print "sxdesktps read"
    #    self.create_desktops(app.screens, self.config)

    def on_new_screen(self, screen):
        self.create_desktops(screen)

    def create_desktops(self, screen):
        # TODO: every screen has the same desktops?
        desktops = []
        for idx, (name, info) in enumerate(self.config):
            desktop = Desktop(self, screen, name, idx, info)
            desktops.append(desktop)
        self.attach_data_to(screen, ScreenData(screen, desktops))

        screen.root.change_property('_NET_NUMBER_OF_DESKTOPS', 'CARDINAL',
                32, [len(desktops)])

        # We don't support large desktops here.
        # But that could be added by a plugin.
        root_geom = screen.get_geometry()
        screen.root.change_property('_NET_DESKTOP_GEOMETRY',
                'CARDINAL', 32,
                [root_geom.width, root_geom.height])
        screen.root.change_property('_NET_DESKTOP_VIEWPORT',
                'CARDINAL', 32, [0, 0])
        screen.root.change_property('_NET_DESKTOP_NAMES',
                'UTF8_STRING', 8,
                List.from_stringlist(
                    (desktop.name for desktop in desktops)
                )
        )

        #screen.push_handlers(
        #        on_map_request=self.screen_on_map_request,
        #)

        # TODO: support _NET_WORKAREA, maybe _NET_SHOWING_DESKTOP?

    def action_cycle(self, info):
        """
            cycle desktop

            parameters:
                `offset`: int
                    optional, defaults to 1

        """
        self.get_data(info['screen']).cycle_desktops(info.get('offset', 1))

    def action_cycle_clients(self, info):
        self.get_data(info['screen']).cycle_clients(info.get('offset', 1))

    def action_goto(self, info):
        """
            go to a specified desktop

            parameters:
                `index`: int
                    index, starting at 0 (required)

        """
        self.get_data(info['screen']).set_active_desktop_idx(info['index'])

    def action_move_client(self, info):
        """
            move a client to a specific desktop 
            
            parameters:
                `index`: int 
                    desktop index, starting at 0 (required)

        """
        screen = info['screen']
        index = info.get('index')
        screen_data = self.get_data(screen)
        if index is None or index >= len(screen_data.desktops) or index < 0:
            log.warning("Invalid desktop index %s" % index)
            return 
        screen_data.move_client_to_desktop(
            info.get('client', screen.focused_client),
            screen_data.desktops[index])
