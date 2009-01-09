import ctypes

from . import libxcb
from .util import MemBuffer
from .event import Event
from .error import Error

class Connection(object):
    def __init__(self, core):
        self.core = core(self)
        self.conn = None
        self.events = {}
        self.errors = {}
        self.extcache = {}
        self._setup = None

    def setup(self):
        import xcb
        # load core ...
        ext = self.core
        events = xcb.CORE_EVENTS
        errors = xcb.CORE_ERRORS
        self.setup_helper(ext, events, errors)
       
        for key, events in xcb.EXT_EVENTS.iteritems():
            errors = xcb.EXT_ERRORS[key]
            ext = self.load_ext(key)

            if ext.present:
                self.setup_helper(ext, events, errors)

    def setup_helper(self, ext, events, errors):
        for num, type in events.iteritems():
            opcode = ext.first_event + num
            self.events[opcode] = type
        for num, type in errors.iteritems():
            opcode = ext.first_error + num
            self.errors[opcode] = type

    def load_ext(self, key):
        import xcb
        if key in self.extcache:
            return self.extcache[key]
        else:
            cls = xcb.EXTDICT[key]
            ext = cls(self, key)
            reply = libxcb.xcb_get_extension_data(self.conn, key.key).contents
            ext.present = reply.present
            ext.major_opcode = reply.major_opcode
            ext.first_event = reply.first_event
            ext.first_error = reply.first_error
            
            self.extcache[key] = ext
            return ext
    
    def __call__(self, key):
        self.check_conn()
        ext = self.load_ext(key)
        return ext 

    def check_conn(self):
        assert self.conn is not None, "Invalid Connection"

    def has_error(self):
        self.check_conn()
        return bool(libxcb.xcb_connection_has_error(self.conn))

    def get_file_descriptor(self):
        self.check_conn()
        return libxcb.xcb_connection_get_file_descriptor(self.conn)
    
    def get_maximum_request_length(self):
        self.check_conn()
        return libxcb.xcb_connection_get_maximum_request_length(self.conn)

    def prefetch_maximum_request_length(self):
        self.check_conn()
        libxcb.xcb_prefetch_maximum_request_length(self.conn)
    
    def get_setup(self):
        self.check_conn()
        if self._setup is None:
            s = libxcb.xcb_get_setup(self.conn)
            shim = MemBuffer(ctypes.addressof(s.contents)) 
            from . import SETUP
            self._setup = SETUP(shim, 0)

        return self._setup

    def generate_id(self):
        self.check_conn()
        xid = libxcb.xcb_generate_id(self.conn)
        # TODO: error checking ...
        return xid

    def wait_for_event(self):
        data = libxcb.xcb_wait_for_event(self.conn)
        if not data:
            raise IOError("I/O error on X server connection.")
        if data.contents.response_type == 0:
            Error.set(self, ctypes.cast(data, ctypes.POINTER(libxcb.xcb_generic_error_t)))
            return
        return Event.create(self, data)

    def poll_for_event(self):
        data = libxcb.xcb_poll_for_event(self.conn)
        if not data:
            raise IOError("I/O error on X server connection.")
        if data.contents.response_type == 0:
            Error.set(self, ctypes.cast(data, ctypes.POINTER(libxcb.xcb_generic_error_t)))
            return
        return Event.create(self, data)
       
    def flush(self):
        self.check_conn()
        libxcb.xcb_flush(self.conn)

    def disconnect(self):
        if self.conn:
            libxcb.xcb_disconnect(self.conn)
            self.conn = None

