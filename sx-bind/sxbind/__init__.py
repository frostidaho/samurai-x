import logging
log = logging.getLogger(__name__)

from samuraix.plugin import Plugin

from ooxcb import keysymdef
from ooxcb.xproto import ModMask

from sxactions import ActionInfo

MODIFIERS = {
        # TODO: I am not sure about the 
        # following four modifiers.
        'alt': ModMask._1,
        'numlock': ModMask._2,
        'meta': ModMask._4,
        'altgr': ModMask._5,

        'shift': ModMask.Shift,
        'lock': ModMask.Lock,
        'ctrl': ModMask.Control,
        'control': ModMask.Control,

        'mod1': ModMask._1,
        'mod2': ModMask._2,
        'mod3': ModMask._3,
        'mod4': ModMask._4,
        'mod5': ModMask._5,
        }

def parse_keystroke(s):
    """
        Return (modifiers, keysym), extracted from the string `s`.

        It has to contain several modifiers and keysym names,
        joined together with a '+':

        CTRL+A
        MOD4+q
    """
    modmask, keysym = 0, 0

    parts = s.split('+') 
    modifiers = parts[:-1]
    key = parts[-1]
    
    # create modmask
    for mod in modifiers:
        try:
            modmask |= MODIFIERS[mod.lower()]
        except KeyError:
            log.error('Unknown modifier: "%s"' % mod)

    # get keysym
    try:
        keysym = getattr(keysymdef, 'XK_%s' % key)
    except AttributeError:
        log.error('Unknown key: "%s"' % key)

    return modmask, keysym


class SXBind(Plugin):
    key = 'bind'

    def __init__(self, app):
        self.app = app
        self.bindings = {} # (modifier, keycode): 'action line'

        app.push_handlers(self)

    def on_ready(self, config):
        self.setup_handlers()

    def on_load_config(self, config):
        for keystroke, action in config.get('bind.keys', {}).iteritems():
            self.bind_keystroke(keystroke, action)

    def setup_handlers(self):
        for screen in self.app.screens:
            screen.root.push_handlers(on_key_press=self.on_key_press)

    def on_key_press(self, event):
        key = (event.state, event.detail)
        if key in self.bindings:
            info = ActionInfo(screen=self.app.get_screen_by_root(event.root)) # TODO: no additional info? :/
            # ... call the action
            self.app.plugins['actions'].emit(self.bindings[key], info)
        else:
            log.warning('received an invalid key press event: %s' % key)

    def bind_key_to_action(self, modifiers, keycode, line):
        """ 
            TODO: support keysyms
        """
        self.bindings[(modifiers, keycode)] = line 
        for screen in self.app.screens:
            screen.root.grab_key(modifiers, keycode)

    def bind_keystroke(self, keystroke, line):
        modifiers, keysym = parse_keystroke(keystroke)
        keycode = self.app.conn.keysyms.get_keycode(keysym)
        
        self.bind_key_to_action(modifiers, keycode, line)
