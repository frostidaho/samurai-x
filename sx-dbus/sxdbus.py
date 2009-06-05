import gobject

import dbus
import dbus.service
import dbus.mainloop.glib

from samuraix.plugin import Plugin

import logging 
log = logging.getLogger(__name__)

class DemoException(dbus.DBusException):
    _dbus_error_name = 'com.example.DemoException'


class SomeObject(dbus.service.Object):

    @dbus.service.method("com.example.SampleInterface",
                         in_signature='s', out_signature='as')
    def HelloWorld(self, hello_message):
        print (str(hello_message))
        return ["Hello", " from example-service.py", "with unique name",
                session_bus.get_unique_name()]

    @dbus.service.method("com.example.SampleInterface",
                         in_signature='', out_signature='')
    def RaiseException(self):
        raise DemoException('The RaiseException method does what you might '
                            'expect')

    @dbus.service.method("com.example.SampleInterface",
                         in_signature='', out_signature='(ss)')
    def GetTuple(self):
        return ("Hello Tuple", " from example-service.py")

    @dbus.service.method("com.example.SampleInterface",
                         in_signature='', out_signature='a{ss}')
    def GetDict(self):
        return {"first": "Hello Dict", "second": " from example-service.py"}

    @dbus.service.method("com.example.SampleInterface",
                         in_signature='', out_signature='')
    def Exit(self):
        mainloop.quit()


class SXDBus(Plugin):
    def __init__(self, app):
        log.info('DBUS ----------------------------')

        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        session_bus = dbus.SessionBus()
        name = dbus.service.BusName("com.example.SampleService", session_bus)
        object = SomeObject(session_bus, '/SomeObject')

