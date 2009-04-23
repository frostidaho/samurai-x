"""
    pywmctrl for ooxcb
"""

import sys
sys.path.append('..')

from ooxcb import xproto, connect

EVENT_MASK = (xproto.EventMask.SubstructureRedirect |
        xproto.EventMask.SubstructureNotify)

class WMControl(object):
    def __init__(self, conn, root):
        self.conn = conn
        self.root = root

    def _send_clientmessage(self, window, atom_name, format, values):
        """
            send a client message to the root window.
            
            :Parameters:
                `window`: xproto.Window
                    the window property
                `atom_name`: str
                    the type atom name
                `format`: int
                    the value format, one of 8, 16, 32
                `values`: list
                    a list of values. Can be heterogenous (either ints
                    or Protobj subclasses). Will be padded to the
                    correct size.
        """
        values = values + [0] * ((160 // format) - len(values))
        event = xproto.ClientMessageEvent(self.conn)
        event.format = format
        event.window = window
        event.type = self.conn.atoms[atom_name]
        event.data = xproto.ClientMessageData(self.conn)
        setattr(event.data, 'data%d' % format, values)
        self.root.send_event_checked(EVENT_MASK, event).check()

    def get_active_window(self):
        """
            returns the active window object
        """
        return self.root.get_active_window()

    def change_desktop(self, desktop):
        """
            change the current desktop. The desktops' count is
            starting at 0.
        """
        self._send_clientmessage(self.root, "_NET_CURRENT_DESKTOP", 32,
                [desktop])

if __name__ == '__main__':
    conn = connect()
    wmctrl = WMControl(conn, conn.setup.roots[0].root)
    wmctrl.change_desktop(1)

