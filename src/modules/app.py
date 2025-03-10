import os
import sys
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from gi.repository import Gio

from modules.configs import get_configs, get_themes
from modules.dbus import start_server
from modules.configs_change import listen_to_directory
from modules.window import OscarWindow
# Constants

USER_CONFIGS_PATH = os.path.expanduser('~/.config/oscar-launcher')
DEFAULT_CONFIGS_PATH = os.path.expanduser('/etc/oscar-launcher')

USER_THEMES_PATH = os.path.expanduser('~/.config/oscar-launcher/themes')
DEFAULT_THEMES_PATH = os.path.expanduser('/etc/oscar-launcher/themes')



def create_window(app, config, theme):
    window = OscarWindow(app, config, theme)
    return window


class OscarApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="io.github.oscar-launcher", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.windows = {}
        self.configs = []
        self.themes = []
        self.load_config_and_theme()

        self.last_open = None
        self.connect("activate", self.on_activate)

    def reset_all(self):
        self.load_config_and_theme()
        self.create_windows()


    def load_config_and_theme(self):
        # load the config and theme
        self.configs = get_configs([USER_CONFIGS_PATH, DEFAULT_CONFIGS_PATH])
        self.themes = get_themes([USER_THEMES_PATH, DEFAULT_THEMES_PATH])
        pass

    def create_windows(self):
        # create the windows
        for config in self.configs:
            self.create_window(config)
    
    def create_window(self, config):
        name = config['name']
        if name in self.windows:
            self.windows[name].destroy()
            self.windows[name] = None

        # create a window
        theme_name = config['json']['theme'] if 'theme' in config['json'] else 'default'
        theme = next((t for t in self.themes if t['name'] == theme_name), None)
        self.windows[name] = create_window(self, config, theme)

        if self.last_open == name:
            self.windows[name].present()
            

    def on_activate(self, app):
        self.create_windows()
        listen_to_directory([USER_CONFIGS_PATH, USER_THEMES_PATH, DEFAULT_CONFIGS_PATH, DEFAULT_THEMES_PATH], lambda event, path: self.reset_all())
        start_server(self.on_dbus_event)

    def on_dbus_event(self, event, name):
        if event == 'open':
            self.open(name)
            return 'Window open: ' + name
        elif event == 'close':
            if self.last_open is not None:
                name = self.last_open
                self.close(name)
                return 'Window close:' + name
            else:
                return 'No window to close'
        elif event == 'status':
            return self.status()

    def status(self):
        response = 'Oscar Status\n::::::::::::::::::::::::::::\n'
        if self.last_open is not None:
            response += 'Current: ' + self.last_open + '\n'
        else:
            response += 'Current: None\n'

        # get all keys of self.window
        windows = list(self.windows.keys())
        response += 'windows: ' + str(windows) + '\n'

        configs = list(map(lambda c: c['name'], self.configs))
        response += 'configs: ' + str(configs) + '\n'

        themes = list(map(lambda t: t['name'], self.themes))
        response += 'themes: ' + str(themes) + '\n'

        return response

    def open(self, name):

        if self.last_open is not None and name == self.last_open:
            return

        if self.last_open is not None:
            self.close(self.last_open)
            self.last_open = None

        window = self.windows[name] if name in self.windows else None

        if window is None:
            return
        self.last_open = name
        window.open_window()

    def close(self, name):
        window = self.windows[name] if name in self.windows else None

        if window is None:
            return
        else :
            window.destroy()
        
        window = None
        self.last_open = None
        config = next((c for c in self.configs if c['name'] == name), None)
        self.create_window(config)


        