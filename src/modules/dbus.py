
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import signal
import sys

# Define the D-Bus service name and path
SERVICE_NAME = 'io.github.oscar-launcher'
SERVICE_PATH = '/io/github/oscar-launcher'
# Define the D-Bus interface name
INTERFACE_NAME = 'io.github.oscar-launcher'

#
# CLIENT
#

def get_client():
    # Connect to the D-Bus session bus
    bus = dbus.SessionBus()

    # Get the D-Bus object
    obj = bus.get_object(SERVICE_NAME, SERVICE_PATH)

    # Get the D-Bus interface
    iface = dbus.Interface(obj, INTERFACE_NAME)

    return iface


#
# SERVER
#
INTERFACE = """
<node>
  <interface name="io.github.oscar-launcher">
    <method name="Open">
      <arg type="s" name="window_name" direction="in"/>
      <arg type="s" name="response" direction="out"/>
    </method>
    <method name="Close">
      <arg type="s" name="response" direction="out"/>
    </method>
    <method name="Status">
      <arg type="s" name="response" direction="out"/>
    </method>
    <method name="Stop">
    </method>
  </interface>
</node>
"""


# Define the D-Bus service class
class OscarDBusService(dbus.service.Object):
    def __init__(self, event_fn):
        bus_name = dbus.service.BusName(SERVICE_NAME, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, SERVICE_PATH)
        self.event_fn = event_fn

    @dbus.service.method(INTERFACE_NAME, in_signature='s', out_signature='s')
    def Open(self, window_name):
        return self.event_fn('open', window_name)
      
    @dbus.service.method(INTERFACE_NAME, out_signature='s')
    def Close(self):
        return self.event_fn('close', None)

    @dbus.service.method(INTERFACE_NAME, out_signature='s')
    def Status(self):
        return self.event_fn('status', None)
      
    @dbus.service.method(INTERFACE_NAME)
    def Stop(self):
        sys.exit(0)
    

def start_server(event_fn):
  try:
    # Initialize the D-Bus main loop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # Create the D-Bus service
    service = OscarDBusService(event_fn)


    # Start the main loop
    loop = GLib.MainLoop()
    loop.run()
  except Exception as e:
    print(e)
    print('Error starting dbus server')
    pass
