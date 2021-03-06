#
# This file generated automatically from randr.xml by py_client.py.
# Edit at your peril.
#

import xcb
import cStringIO
import ctypes
from struct import pack, unpack_from, calcsize
from array import array

def unpack_ex(fmt, protobj, offset=0):
    s = protobj.get_slice(calcsize(fmt), offset)
    return unpack_from(fmt, s, 0)

import xproto

MAJOR_VERSION = 1
MINOR_VERSION = 2

key = xcb.ExtensionKey('RANDR')

class OutputError(xcb.Error):
    def __init__(self, parent):
        xcb.Error.__init__(self, parent)

class BadOutput(xcb.ProtocolException):
    pass

class CrtcError(xcb.Error):
    def __init__(self, parent):
        xcb.Error.__init__(self, parent)

class BadCrtc(xcb.ProtocolException):
    pass

class ModeError(xcb.Error):
    def __init__(self, parent):
        xcb.Error.__init__(self, parent)

class BadMode(xcb.ProtocolException):
    pass

class Rotation:
    Rotate_0 = (1 << 0)
    Rotate_90 = (1 << 1)
    Rotate_180 = (1 << 2)
    Rotate_270 = (1 << 3)
    Reflect_X = (1 << 4)
    Reflect_Y = (1 << 5)

class ScreenSize(xcb.Struct):
    def __init__(self, parent, offset, size):
        xcb.Struct.__init__(self, parent, offset, size)
        count = 0
        (self.width, self.height, self.mwidth, self.mheight,) = unpack_ex('hhhh', self, count)

class RefreshRates(xcb.Struct):
    def __init__(self, parent, offset):
        xcb.Struct.__init__(self, parent, offset)
        count = 0
        (self.nRates,) = unpack_ex('H', self, count)
        count += 2
        self.rates = xcb.List(self, count, self.nRates, 'H', 2)
        count += len(self.rates.buf())
        xcb._resize_obj(self, count)

class QueryVersionCookie(xcb.Cookie):
    pass

class QueryVersionReply(xcb.Reply):
    def __init__(self, parent):
        xcb.Reply.__init__(self, parent)
        count = 0
        (self.major_version, self.minor_version,) = unpack_ex('xx2x4xII16x', self, count)

class SetScreenConfigCookie(xcb.Cookie):
    pass

class SetScreenConfigReply(xcb.Reply):
    def __init__(self, parent):
        xcb.Reply.__init__(self, parent)
        count = 0
        (self.status, self.new_timestamp, self.config_timestamp, self.root, self.subpixel_order,) = unpack_ex('xB2x4xIIIH10x', self, count)

class SetConfig:
    Success = 0
    InvalidConfigTime = 1
    InvalidTime = 2
    Failed = 3

class GetScreenInfoCookie(xcb.Cookie):
    pass

class GetScreenInfoReply(xcb.Reply):
    def __init__(self, parent):
        xcb.Reply.__init__(self, parent)
        count = 0
        (self.rotations, self.root, self.timestamp, self.config_timestamp, self.nSizes, self.sizeID, self.rotation, self.rate, self.nInfo,) = unpack_ex('xB2x4xIIIHHhHH2x', self, count)
        count += 32
        self.sizes = xcb.List(self, count, self.nSizes, ScreenSize, 8)
        count += len(self.sizes.buf())
        count += xcb.type_pad(4, count)
        self.rates = xcb.List(self, count, (self.nInfo - self.nSizes), RefreshRates, -1)

class GetScreenSizeRangeCookie(xcb.Cookie):
    pass

class GetScreenSizeRangeReply(xcb.Reply):
    def __init__(self, parent):
        xcb.Reply.__init__(self, parent)
        count = 0
        (self.min_width, self.min_height, self.max_width, self.max_height,) = unpack_ex('xx2x4xHHHH', self, count)

class ModeFlag:
    HsyncPositive = (1 << 0)
    HsyncNegative = (1 << 1)
    VsyncPositive = (1 << 2)
    VsyncNegative = (1 << 3)
    Interlace = (1 << 4)
    DoubleScan = (1 << 5)
    Csync = (1 << 6)
    CsyncPositive = (1 << 7)
    CsyncNegative = (1 << 8)
    HskewPresent = (1 << 9)
    Bcast = (1 << 10)
    PixelMultiplex = (1 << 11)
    DoubleClock = (1 << 12)
    HalveClock = (1 << 13)

class ModeInfo(xcb.Struct):
    def __init__(self, parent, offset, size):
        xcb.Struct.__init__(self, parent, offset, size)
        count = 0
        (self.id, self.width, self.height, self.dot_clock, self.hsync_start, self.hsync_end, self.htotal, self.hskew, self.vsync_start, self.vsync_end, self.vtotal, self.name_len, self.mode_flags,) = unpack_ex('IHHIHHHHHHHHI', self, count)

class GetScreenResourcesCookie(xcb.Cookie):
    pass

class GetScreenResourcesReply(xcb.Reply):
    def __init__(self, parent):
        xcb.Reply.__init__(self, parent)
        count = 0
        (self.timestamp, self.config_timestamp, self.num_crtcs, self.num_outputs, self.num_modes, self.names_len,) = unpack_ex('xx2x4xIIHHHH8x', self, count)
        count += 32
        self.crtcs = xcb.List(self, count, self.num_crtcs, 'I', 4)
        count += len(self.crtcs.buf())
        count += xcb.type_pad(4, count)
        self.outputs = xcb.List(self, count, self.num_outputs, 'I', 4)
        count += len(self.outputs.buf())
        count += xcb.type_pad(32, count)
        self.modes = xcb.List(self, count, self.num_modes, ModeInfo, 32)
        count += len(self.modes.buf())
        count += xcb.type_pad(1, count)
        self.names = xcb.List(self, count, self.names_len, 'B', 1)

class Connection:
    Connected = 0
    Disconnected = 1
    Unknown = 2

class GetOutputInfoCookie(xcb.Cookie):
    pass

class GetOutputInfoReply(xcb.Reply):
    def __init__(self, parent):
        xcb.Reply.__init__(self, parent)
        count = 0
        (self.status, self.timestamp, self.crtc, self.mm_width, self.mm_height, self.connection, self.subpixel_order, self.num_crtcs, self.num_modes, self.num_preferred, self.num_clones, self.name_len,) = unpack_ex('xB2x4xIIIIBBHHHHH', self, count)
        count += 36
        self.crtcs = xcb.List(self, count, self.num_crtcs, 'I', 4)
        count += len(self.crtcs.buf())
        count += xcb.type_pad(4, count)
        self.modes = xcb.List(self, count, self.num_modes, 'I', 4)
        count += len(self.modes.buf())
        count += xcb.type_pad(4, count)
        self.clones = xcb.List(self, count, self.num_clones, 'I', 4)
        count += len(self.clones.buf())
        count += xcb.type_pad(1, count)
        self.name = xcb.List(self, count, self.name_len, 'B', 1)

class ListOutputPropertiesCookie(xcb.Cookie):
    pass

class ListOutputPropertiesReply(xcb.Reply):
    def __init__(self, parent):
        xcb.Reply.__init__(self, parent)
        count = 0
        (self.num_atoms,) = unpack_ex('xx2x4xH22x', self, count)
        count += 32
        self.atoms = xcb.List(self, count, self.num_atoms, 'I', 4)

class QueryOutputPropertyCookie(xcb.Cookie):
    pass

class QueryOutputPropertyReply(xcb.Reply):
    def __init__(self, parent):
        xcb.Reply.__init__(self, parent)
        count = 0
        (self.pending, self.range, self.immutable,) = unpack_ex('xx2x4xBBB21x', self, count)
        count += 32
        self.validValues = xcb.List(self, count, self.length, 'i', 4)

class GetOutputPropertyCookie(xcb.Cookie):
    pass

class GetOutputPropertyReply(xcb.Reply):
    def __init__(self, parent):
        xcb.Reply.__init__(self, parent)
        count = 0
        (self.format, self.type, self.bytes_after, self.num_items,) = unpack_ex('xB2x4xIII12x', self, count)
        count += 32
        self.data = xcb.List(self, count, (self.num_items * (self.format / 8)), 'B', 1)

class CreateModeCookie(xcb.Cookie):
    pass

class CreateModeReply(xcb.Reply):
    def __init__(self, parent):
        xcb.Reply.__init__(self, parent)
        count = 0
        (self.status, self.mode,) = unpack_ex('xB2x4xI', self, count)

class GetCrtcInfoCookie(xcb.Cookie):
    pass

class GetCrtcInfoReply(xcb.Reply):
    def __init__(self, parent):
        xcb.Reply.__init__(self, parent)
        count = 0
        (self.status, self.timestamp, self.crtc, self.x, self.y, self.width, self.height, self.mode, self.rotation, self.rotations, self.num_outputs, self.num_possible_outputs,) = unpack_ex('xB2x4xIIhhHHIHHHH', self, count)
        count += 36
        self.outputs = xcb.List(self, count, self.num_outputs, 'I', 4)

class SetCrtcConfigCookie(xcb.Cookie):
    pass

class SetCrtcConfigReply(xcb.Reply):
    def __init__(self, parent):
        xcb.Reply.__init__(self, parent)
        count = 0
        (self.status, self.timestamp,) = unpack_ex('xB2x4xI', self, count)

class GetCrtcGammaSizeCookie(xcb.Cookie):
    pass

class GetCrtcGammaSizeReply(xcb.Reply):
    def __init__(self, parent):
        xcb.Reply.__init__(self, parent)
        count = 0
        (self.status, self.size,) = unpack_ex('xB2x4xH', self, count)

class GetCrtcGammaCookie(xcb.Cookie):
    pass

class GetCrtcGammaReply(xcb.Reply):
    def __init__(self, parent):
        xcb.Reply.__init__(self, parent)
        count = 0
        (self.status, self.size,) = unpack_ex('xB2x4xH22x', self, count)
        count += 32
        self.red = xcb.List(self, count, self.size, 'H', 2)
        count += len(self.red.buf())
        count += xcb.type_pad(2, count)
        self.green = xcb.List(self, count, self.size, 'H', 2)
        count += len(self.green.buf())
        count += xcb.type_pad(2, count)
        self.blue = xcb.List(self, count, self.size, 'H', 2)

class NotifyMask:
    ScreenChange = (1 << 0)
    CrtcChange = (1 << 1)
    OutputChange = (1 << 2)
    OutputProperty = (1 << 3)

class ScreenChangeNotifyEvent(xcb.Event):
    def __init__(self, parent):
        xcb.Event.__init__(self, parent)
        count = 0
        (self.rotation, self.timestamp, self.config_timestamp, self.root, self.request_window, self.sizeID, self.subpixel_order, self.width, self.height, self.mwidth, self.mheight,) = unpack_ex('xB2xIIIIHHHHHH', self, count)

class Notify:
    CrtcChange = 0
    OutputChange = 1
    OutputProperty = 2

class CrtcChange(xcb.Struct):
    def __init__(self, parent, offset, size):
        xcb.Struct.__init__(self, parent, offset, size)
        count = 0
        (self.timestamp, self.window, self.crtc, self.mode, self.rotation, self.x, self.y, self.width, self.height,) = unpack_ex('IIIIH2xhhHH', self, count)

class OutputChange(xcb.Struct):
    def __init__(self, parent, offset, size):
        xcb.Struct.__init__(self, parent, offset, size)
        count = 0
        (self.timestamp, self.config_timestamp, self.window, self.output, self.crtc, self.mode, self.rotation, self.connection, self.subpixel_order,) = unpack_ex('IIIIIIHBB', self, count)

class OutputProperty(xcb.Struct):
    def __init__(self, parent, offset, size):
        xcb.Struct.__init__(self, parent, offset, size)
        count = 0
        (self.window, self.output, self.atom, self.timestamp, self.status,) = unpack_ex('IIIIB11x', self, count)

class NotifyData(xcb.Union):
    def __init__(self, parent, offset, size):
        xcb.Union.__init__(self, parent, offset, size)
        count = 0
        self.cc = CrtcChange(self, 0, 28)
        count = max(count, 28)
        self.oc = OutputChange(self, 0, 28)
        count = max(count, 28)
        self.op = OutputProperty(self, 0, 28)
        count = max(count, 28)

class NotifyEvent(xcb.Event):
    def __init__(self, parent):
        xcb.Event.__init__(self, parent)
        count = 0
        (self.subCode,) = unpack_ex('xB2x', self, count)
        count += 4
        self.u = NotifyData(self, count, 84)

class randrExtension(xcb.Extension):

    def QueryVersion(self, major_version, minor_version):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xII', major_version, minor_version))
        return self.send_request(xcb.Request(buf.getvalue(), 0, False, True),
                                 QueryVersionCookie(),
                                 QueryVersionReply)

    def QueryVersionUnchecked(self, major_version, minor_version):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xII', major_version, minor_version))
        return self.send_request(xcb.Request(buf.getvalue(), 0, False, False),
                                 QueryVersionCookie(),
                                 QueryVersionReply)

    def SetScreenConfig(self, drawable, timestamp, config_timestamp, sizeID, rotation, rate):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xIIIHhH2x', drawable, timestamp, config_timestamp, sizeID, rotation, rate))
        return self.send_request(xcb.Request(buf.getvalue(), 2, False, True),
                                 SetScreenConfigCookie(),
                                 SetScreenConfigReply)

    def SetScreenConfigUnchecked(self, drawable, timestamp, config_timestamp, sizeID, rotation, rate):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xIIIHhH2x', drawable, timestamp, config_timestamp, sizeID, rotation, rate))
        return self.send_request(xcb.Request(buf.getvalue(), 2, False, False),
                                 SetScreenConfigCookie(),
                                 SetScreenConfigReply)

    def SelectInputChecked(self, window, enable):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xIH2x', window, enable))
        return self.send_request(xcb.Request(buf.getvalue(), 4, True, True),
                                 xcb.VoidCookie())

    def SelectInput(self, window, enable):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xIH2x', window, enable))
        return self.send_request(xcb.Request(buf.getvalue(), 4, True, False),
                                 xcb.VoidCookie())

    def GetScreenInfo(self, window):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xI', window))
        return self.send_request(xcb.Request(buf.getvalue(), 5, False, True),
                                 GetScreenInfoCookie(),
                                 GetScreenInfoReply)

    def GetScreenInfoUnchecked(self, window):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xI', window))
        return self.send_request(xcb.Request(buf.getvalue(), 5, False, False),
                                 GetScreenInfoCookie(),
                                 GetScreenInfoReply)

    def GetScreenSizeRange(self, window):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xI', window))
        return self.send_request(xcb.Request(buf.getvalue(), 6, False, True),
                                 GetScreenSizeRangeCookie(),
                                 GetScreenSizeRangeReply)

    def GetScreenSizeRangeUnchecked(self, window):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xI', window))
        return self.send_request(xcb.Request(buf.getvalue(), 6, False, False),
                                 GetScreenSizeRangeCookie(),
                                 GetScreenSizeRangeReply)

    def SetScreenSizeChecked(self, window, width, height, mm_width, mm_height):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xIHHII', window, width, height, mm_width, mm_height))
        return self.send_request(xcb.Request(buf.getvalue(), 7, True, True),
                                 xcb.VoidCookie())

    def SetScreenSize(self, window, width, height, mm_width, mm_height):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xIHHII', window, width, height, mm_width, mm_height))
        return self.send_request(xcb.Request(buf.getvalue(), 7, True, False),
                                 xcb.VoidCookie())

    def GetScreenResources(self, window):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xI', window))
        return self.send_request(xcb.Request(buf.getvalue(), 8, False, True),
                                 GetScreenResourcesCookie(),
                                 GetScreenResourcesReply)

    def GetScreenResourcesUnchecked(self, window):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xI', window))
        return self.send_request(xcb.Request(buf.getvalue(), 8, False, False),
                                 GetScreenResourcesCookie(),
                                 GetScreenResourcesReply)

    def GetOutputInfo(self, output, config_timestamp):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xII', output, config_timestamp))
        return self.send_request(xcb.Request(buf.getvalue(), 9, False, True),
                                 GetOutputInfoCookie(),
                                 GetOutputInfoReply)

    def GetOutputInfoUnchecked(self, output, config_timestamp):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xII', output, config_timestamp))
        return self.send_request(xcb.Request(buf.getvalue(), 9, False, False),
                                 GetOutputInfoCookie(),
                                 GetOutputInfoReply)

    def ListOutputProperties(self, output):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xI', output))
        return self.send_request(xcb.Request(buf.getvalue(), 10, False, True),
                                 ListOutputPropertiesCookie(),
                                 ListOutputPropertiesReply)

    def ListOutputPropertiesUnchecked(self, output):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xI', output))
        return self.send_request(xcb.Request(buf.getvalue(), 10, False, False),
                                 ListOutputPropertiesCookie(),
                                 ListOutputPropertiesReply)

    def QueryOutputProperty(self, output, property):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xII', output, property))
        return self.send_request(xcb.Request(buf.getvalue(), 11, False, True),
                                 QueryOutputPropertyCookie(),
                                 QueryOutputPropertyReply)

    def QueryOutputPropertyUnchecked(self, output, property):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xII', output, property))
        return self.send_request(xcb.Request(buf.getvalue(), 11, False, False),
                                 QueryOutputPropertyCookie(),
                                 QueryOutputPropertyReply)

    def ConfigureOutputPropertyChecked(self, output, property, pending, range):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xIIBB2x', output, property, pending, range))
        return self.send_request(xcb.Request(buf.getvalue(), 12, True, True),
                                 xcb.VoidCookie())

    def ConfigureOutputProperty(self, output, property, pending, range):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xIIBB2x', output, property, pending, range))
        return self.send_request(xcb.Request(buf.getvalue(), 12, True, False),
                                 xcb.VoidCookie())

    def ChangeOutputPropertyChecked(self, output, property, type, format, mode, num_units):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xIIIBB2xI', output, property, type, format, mode, num_units))
        return self.send_request(xcb.Request(buf.getvalue(), 13, True, True),
                                 xcb.VoidCookie())

    def ChangeOutputProperty(self, output, property, type, format, mode, num_units):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xIIIBB2xI', output, property, type, format, mode, num_units))
        return self.send_request(xcb.Request(buf.getvalue(), 13, True, False),
                                 xcb.VoidCookie())

    def DeleteOutputPropertyChecked(self, output, property):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xII', output, property))
        return self.send_request(xcb.Request(buf.getvalue(), 14, True, True),
                                 xcb.VoidCookie())

    def DeleteOutputProperty(self, output, property):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xII', output, property))
        return self.send_request(xcb.Request(buf.getvalue(), 14, True, False),
                                 xcb.VoidCookie())

    def GetOutputProperty(self, output, property, type, long_offset, long_length, delete, pending):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xIIIIIBB', output, property, type, long_offset, long_length, delete, pending))
        return self.send_request(xcb.Request(buf.getvalue(), 15, False, True),
                                 GetOutputPropertyCookie(),
                                 GetOutputPropertyReply)

    def GetOutputPropertyUnchecked(self, output, property, type, long_offset, long_length, delete, pending):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xIIIIIBB', output, property, type, long_offset, long_length, delete, pending))
        return self.send_request(xcb.Request(buf.getvalue(), 15, False, False),
                                 GetOutputPropertyCookie(),
                                 GetOutputPropertyReply)

    def CreateMode(self, window, mode_info):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xI', window))
        for elt in xcb.Iterator(mode_info, 13, 'mode_info', False):
            buf.write(pack('IHHIHHHHHHHHI', *elt))
        return self.send_request(xcb.Request(buf.getvalue(), 16, False, True),
                                 CreateModeCookie(),
                                 CreateModeReply)

    def CreateModeUnchecked(self, window, mode_info):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xI', window))
        for elt in xcb.Iterator(mode_info, 13, 'mode_info', False):
            buf.write(pack('IHHIHHHHHHHHI', *elt))
        return self.send_request(xcb.Request(buf.getvalue(), 16, False, False),
                                 CreateModeCookie(),
                                 CreateModeReply)

    def DestroyModeChecked(self, mode):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xI', mode))
        return self.send_request(xcb.Request(buf.getvalue(), 17, True, True),
                                 xcb.VoidCookie())

    def DestroyMode(self, mode):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xI', mode))
        return self.send_request(xcb.Request(buf.getvalue(), 17, True, False),
                                 xcb.VoidCookie())

    def AddOutputModeChecked(self, output, mode):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xII', output, mode))
        return self.send_request(xcb.Request(buf.getvalue(), 18, True, True),
                                 xcb.VoidCookie())

    def AddOutputMode(self, output, mode):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xII', output, mode))
        return self.send_request(xcb.Request(buf.getvalue(), 18, True, False),
                                 xcb.VoidCookie())

    def DeleteOutputModeChecked(self, output, mode):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xII', output, mode))
        return self.send_request(xcb.Request(buf.getvalue(), 19, True, True),
                                 xcb.VoidCookie())

    def DeleteOutputMode(self, output, mode):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xII', output, mode))
        return self.send_request(xcb.Request(buf.getvalue(), 19, True, False),
                                 xcb.VoidCookie())

    def GetCrtcInfo(self, crtc, config_timestamp):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xII', crtc, config_timestamp))
        return self.send_request(xcb.Request(buf.getvalue(), 20, False, True),
                                 GetCrtcInfoCookie(),
                                 GetCrtcInfoReply)

    def GetCrtcInfoUnchecked(self, crtc, config_timestamp):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xII', crtc, config_timestamp))
        return self.send_request(xcb.Request(buf.getvalue(), 20, False, False),
                                 GetCrtcInfoCookie(),
                                 GetCrtcInfoReply)

    def SetCrtcConfig(self, crtc, timestamp, config_timestamp, x, y, mode, rotation):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xIIIhhIH', crtc, timestamp, config_timestamp, x, y, mode, rotation))
        return self.send_request(xcb.Request(buf.getvalue(), 21, False, True),
                                 SetCrtcConfigCookie(),
                                 SetCrtcConfigReply)

    def SetCrtcConfigUnchecked(self, crtc, timestamp, config_timestamp, x, y, mode, rotation):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xIIIhhIH', crtc, timestamp, config_timestamp, x, y, mode, rotation))
        return self.send_request(xcb.Request(buf.getvalue(), 21, False, False),
                                 SetCrtcConfigCookie(),
                                 SetCrtcConfigReply)

    def GetCrtcGammaSize(self, crtc):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xI', crtc))
        return self.send_request(xcb.Request(buf.getvalue(), 22, False, True),
                                 GetCrtcGammaSizeCookie(),
                                 GetCrtcGammaSizeReply)

    def GetCrtcGammaSizeUnchecked(self, crtc):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xI', crtc))
        return self.send_request(xcb.Request(buf.getvalue(), 22, False, False),
                                 GetCrtcGammaSizeCookie(),
                                 GetCrtcGammaSizeReply)

    def GetCrtcGamma(self, crtc):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xI', crtc))
        return self.send_request(xcb.Request(buf.getvalue(), 23, False, True),
                                 GetCrtcGammaCookie(),
                                 GetCrtcGammaReply)

    def GetCrtcGammaUnchecked(self, crtc):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xI', crtc))
        return self.send_request(xcb.Request(buf.getvalue(), 23, False, False),
                                 GetCrtcGammaCookie(),
                                 GetCrtcGammaReply)

    def SetCrtcGammaChecked(self, crtc, size, red, green, blue):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xIH2x', crtc, size))
        buf.write(str(buffer(array('H', red))))
        buf.write(str(buffer(array('H', green))))
        buf.write(str(buffer(array('H', blue))))
        return self.send_request(xcb.Request(buf.getvalue(), 24, True, True),
                                 xcb.VoidCookie())

    def SetCrtcGamma(self, crtc, size, red, green, blue):
        buf = cStringIO.StringIO()
        buf.write(pack('xx2xIH2x', crtc, size))
        buf.write(str(buffer(array('H', red))))
        buf.write(str(buffer(array('H', green))))
        buf.write(str(buffer(array('H', blue))))
        return self.send_request(xcb.Request(buf.getvalue(), 24, True, False),
                                 xcb.VoidCookie())

_events = {
    0 : ScreenChangeNotifyEvent,
    1 : NotifyEvent,
}

_errors = {
    0 : (OutputError, BadOutput),
    1 : (CrtcError, BadCrtc),
    2 : (ModeError, BadMode),
}

xcb._add_ext(key, randrExtension, _events, _errors)
