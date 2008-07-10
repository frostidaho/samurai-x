from pyglet.window.xlib import xlib 
import samuraix

class Cursors(dict):
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            r = self[item] = xlib.XCreateFontCursor(samuraix.display, item)
            return r


