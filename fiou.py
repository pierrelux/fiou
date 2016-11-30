import os
import signal
import threading
import time

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3
from phue import Bridge

class FiouIndicator:
    def __init__(self, addr='192.168.1.170', refresh=5):
        super(FiouIndicator, self).__init__()
        self.refresh = refresh
        self.bridge = Bridge(addr)
        self.menu = Gtk.Menu()

        self.light_widgets = {}
        for light in self.bridge.lights:
            light_item = Gtk.CheckMenuItem('{} ({:.0f} %)'.format(light.name, 100*light.brightness/254))
            self.light_widgets[light_item] = light
            light_item.set_active(light.on)
            light_item.connect('toggled', self.toggle_light, light)
            self.menu.append(light_item)

        self.menu.append(Gtk.SeparatorMenuItem())
        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', Gtk.main_quit)
        self.menu.append(item_quit)
        self.menu.show_all()

        self.indicator = AppIndicator3.Indicator.new('fiou', os.path.abspath('bulb.svg'), AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.menu)

        self.thread = threading.Thread(target=self.refresh_bridge)
        self.thread.daemon = True
        self.thread.start()

    def toggle_light(self, source, light):
        light.on = source.get_active()

    def refresh_bridge(self):
        while True:
            for widget, light in self.light_widgets.items():
                widget.set_active(light.on)
            time.sleep(self.refresh)

if __name__ == "__main__":
    GObject.threads_init()
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    ind = FiouIndicator()

    Gtk.main()
