
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Gdk

from modules.set_interval import set_interval
import subprocess

def execute_command(command, shell):
    try:
        subprocess.Popen(command, shell=shell)
    except Exception as e:
        pass

def get_output_command(command):
    try:
        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        out, err = result.communicate()
        return out
    except Exception as e:
        return '-- Error --'




class OscarWindow(Gtk.ApplicationWindow):
    def __init__(self, app, config, theme):
        super().__init__(application=app)
        self.app = app
        self.config = config
        self.json = config['json']
        self.theme = theme

        self.shortcuts = []
        self.timeouts = []

        width = 400
        height = 200
        if 'width' in self.json:
            width = self.json['width']
        if 'height' in self.json:
            height = self.json['height']

        self.set_title(config['name'])
        self.set_default_size(width, height)
        self.set_modal(True)
        self.set_resizable(False)

        orientation = Gtk.Orientation.VERTICAL
        if 'orientation' in self.json:
            if self.json['orientation'] == 'horizontal':
                orientation = Gtk.Orientation.HORIZONTAL
        box = Gtk.Box()
        box.set_orientation(orientation)
        box.add_css_class('main')
        items = []
        if 'items' in self.json:
            items = self.json['items']

        self.loop_items(items, box)

        self.set_child(box)
        self.connect("close-request", self.on_close)


        keycontroller = Gtk.EventControllerKey.new()
        keycontroller.connect("key-pressed", self.on_key_pressed)
        self.add_controller(keycontroller)

    def on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == 65307:
            self.close()

        letter = chr(keyval)

        for shortcut in self.shortcuts:
            if shortcut['shortcut'] == letter:
                execute_command(shortcut['command'], True)
                self.close()


    def open_window(self):
        self.apply_theme()
        self.present()
    
    def apply_theme(self):
        if self.app.last_theme_applied is None or self.app.last_theme_applied != self.theme['name']:
            self.app.last_theme_applied = self.theme['name']
            css = self.theme['css']
            provider = Gtk.CssProvider()
            provider.load_from_data(css.encode())
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_USER
            )

    def on_close(self, w):

        for t in self.timeouts:
            t.event.set()

        self.app.close(self.config['name'])



    def loop_items(self, items, parent):
        for item in items:
            if 'disabled' in item and item['disabled']:
                continue

            if 'shortcut' in item:
                short = {
                    "shortcut": item['shortcut'],
                    "command": item['command']
                }
                
                exist = next((s for s in self.shortcuts if s['shortcut'] == item['shortcut']), None)
                if exist is None:
                    self.shortcuts.append(short)

            type = 'button'
            if 'type' in item:
                type = item['type']

            if type == 'button':
                i = self.create_button(item)
            elif type == 'output':
                i = self.create_output(item)
            elif type == 'group':
                i = self.create_group(item)
            elif type == 'runner':
                i = self.create_runner(item)
            elif type == 'separator':
                i = self.create_separator(item)
            elif type == 'text':
                i = self.create_text(item)

            if i is not None:
                i.set_cursor_from_name(None)
                i.set_hexpand(True)

                i.add_css_class('widget')
                i.add_css_class('widget__' + type)
                if 'class_name' in item:
                    names = item['class_name'].split(' ')
                    for name in names:
                        i.add_css_class(name)

                parent.append(i)


    def create_button(self, item):
        button = Gtk.Button()

        label = ''
        if 'label' in item:
            label = item['label']

        if 'shortcut' in item:
            label = label + ' (' + item['shortcut'] + ')'

        button.set_label(label)

        def on_button_clicked(button):
            command = ''
            if 'command' in item:
                command = item['command']
            execute_command(command, True)
            self.close()
            
        button.connect("clicked", on_button_clicked)
        return button
    

    def create_output(self, item):
        output = Gtk.Label()
        command = ''
        if 'command' in item:
            command = item['command']
        def on_interval():
            if command:
                t = get_output_command(command)
                t = t.decode('utf-8')
                t = t.strip()
                output.set_text(t)   
                return t
            else:
                output.set_text('')   
        on_interval()
        interval = 0
        if 'interval' in item:
            interval = item['interval']
       
        if interval > 0:
            job = set_interval(on_interval, interval)
            self.timeouts.append(job)

        return output

    def create_group(self, item):
        group = Gtk.Box()
        orientation = Gtk.Orientation.HORIZONTAL
        if 'orientation' in item:
            if item['orientation'] == 'vertical':
                orientation = Gtk.Orientatifon.VERTICAL
            elif item['orientation'] == 'horizontal':
                orientation = Gtk.Orientation.HORIZONTAL

        group.set_orientation(orientation)
        self.loop_items(item['items'], group)
        return group


    def create_runner(self, item):
        runner = Gtk.Entry()
        runner.set_text('')
        def on_activate(entry):
            command = runner.get_text()
            if command:
                execute_command(command, True)
                self.close()
        runner.connect("activate", on_activate)
        return runner

    def create_separator(self, item):
        separator = Gtk.Separator()
        return separator

    def create_text(self, item):
        text = Gtk.Label()
        text.set_text(item['text'])
        return text