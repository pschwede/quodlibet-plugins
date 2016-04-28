# Copyright 2014 Peter Schwede
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation

from gi.repository import Gtk, GLib, GObject

from quodlibet import app
from quodlibet.plugins.events import EventPlugin
from quodlibet import qltk
from quodlibet import config

_PLUGIN_ID = "autoseek"

_SETTINGS = {
    "seekto": [_("_Seek to:"),
                  _("Part of the song to seek to"), 0.33],
    "skipat": [_("S_kip at:"), _("Play next song playing these seconds"), 5.],
}


def get_cfg(option):
    cfg_option = "%s_%s" % (_PLUGIN_ID, option)
    default = _SETTINGS[option][2]

    if option == "seekto":
        return config.getfloat("plugins", cfg_option, default)
    elif option == "skipat":
        return config.getfloat("plugins", cfg_option, default)


def set_cfg(option, value):
    cfg_option = "%s_%s" % (_PLUGIN_ID, option)
    if get_cfg(option) != value:
        config.set("plugins", cfg_option, value)


class Preferences(Gtk.VBox):
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_LAST, None, tuple()),
    }

    def __init__(self):
        super(Preferences, self).__init__(spacing=12)

        table = Gtk.Table(2, 2)
        table.set_col_spacings(6)
        table.set_row_spacings(6)

        labels = {}
        for idx, key in enumerate(["seekto", "skipat"]):
            text, tooltip = _SETTINGS[key][:2]
            label = Gtk.Label(label=text)
            labels[key] = label
            label.set_tooltip_text(tooltip)
            label.set_alignment(0.0, 0.5)
            label.set_padding(0, 6)
            label.set_use_underline(True)
            table.attach(label, 0, 1, idx, idx + 1,
                         xoptions=Gtk.AttachOptions.FILL |
                         Gtk.AttachOptions.SHRINK)

        seekto_scale = Gtk.HScale(
            adjustment=Gtk.Adjustment(0, 0, .99, 0.01, 0.1))
        seekto_scale.set_digits(2)
        labels["seekto"].set_mnemonic_widget(seekto_scale)
        seekto_scale.set_value_pos(Gtk.PositionType.RIGHT)

        def format_perc(scale, value):
            return _("%d %%") % (value * 100)
        seekto_scale.connect('format-value', format_perc)
        table.attach(seekto_scale, 1, 2, 0, 1)

        def seekto_changed(scale):
            value = scale.get_value()
            set_cfg("seekto", value)
            self.emit("changed")
        seekto_scale.connect('value-changed', seekto_changed)
        seekto_scale.set_value(get_cfg("seekto"))

        skipat_scale = Gtk.HScale(adjustment=Gtk.Adjustment(5, 1, 30, 1, 5))
        skipat_scale.set_digits(0)
        labels["skipat"].set_mnemonic_widget(skipat_scale)
        skipat_scale.set_value_pos(Gtk.PositionType.RIGHT)
        table.attach(skipat_scale, 1, 2, 1, 2)

        def skipat_changed(scale):
            value = scale.get_value()
            set_cfg("skipat", value)
            self.emit("changed")
        skipat_scale.connect('value-changed', skipat_changed)
        skipat_scale.set_value(get_cfg("skipat"))

        self.pack_start(qltk.Frame(_("Preferences"), child=table),
                        True, True, 0)


class AutoSeek(EventPlugin):
    PLUGIN_ID = _PLUGIN_ID
    PLUGIN_NAME = _("AutoSeek")
    PLUGIN_ICON = "gtk-jump-to"
    PLUGIN_VERSION = "1.0"
    PLUGIN_DESC = ("Seeks into the next song and skips after a while.")

    def __init__(self):
        pass

    def plugin_on_song_started(self, song):
        if not song:
            return False
        GLib.timeout_add(1, self._seek, song)

    def _seek(self, song):
        print_d("Firing seek %s" % song)
        if app.player.paused or not song or app.player.song("~filename") != song("~filename"):
            return False

        seekto = 1000 * (get_cfg("seekto") * song("~#length"))
        position = app.player.get_position()
        if(position < seekto):
            app.player.seek(seekto)
            position = seekto

        skipat = max(1, 1000 * get_cfg("skipat"))
        GLib.timeout_add(skipat, self._skip, song)
        return False

    def _skip(self, song):
        print_d("Firing skip %s" % song)
        if app.player.paused or \
           not song or \
           app.player.song("~filename") != song("~filename"):
            return False

        oldskips = song("~#skipcount")
        app.player.next()
        song.update({"~#skipcount": oldskips})
        return False

    @classmethod
    def PluginPreferences(cls, window):
        prefs = Preferences()
        #gobject_weak(prefs.connect, "changed", lambda *x: cls.queue_update())
        return prefs
