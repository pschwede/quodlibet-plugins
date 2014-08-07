# Copyright 2014 Peter Schwede
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation

from os.path import join
import random
import pickle
import itertools

from gi.repository import Gtk, GObject

from quodlibet import app
from quodlibet import qltk
from quodlibet import const
from quodlibet import config
from quodlibet.plugins.events import EventPlugin

_PLUGIN_ID = "autocast"

_SETTINGS = {
    "minmusic": [_("_Music minutes:"),
                 _("Music minimum between podcasts in seconds"),
                 60.],
}


def get_cfg(option):
    cfg_option = "%s_%s" % (_PLUGIN_ID, option)
    default = _SETTINGS[option][2]
    if option == "minmusic":
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
        for idx, key in enumerate(["minmusic"]):
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

        minmusic_scale = Gtk.HScale(adjustment=Gtk.Adjustment(5, 0, 30, 1, 5))
        minmusic_scale.set_digits(0)
        minmusic_scale.set_value(get_cfg("minmusic") / 60)

        labels["minmusic"].set_mnemonic_widget(minmusic_scale)
        minmusic_scale.set_value_pos(Gtk.PositionType.RIGHT)
        table.attach(minmusic_scale, 1, 2, 0, 1)

        def minmusic_changed(scale):
            value = scale.get_value() * 60
            set_cfg("minmusic", value)
            self.emit("changed")
        minmusic_scale.connect('value-changed', minmusic_changed)

        self.pack_start(qltk.Frame(_("Preferences"), child=table),
                        True, True, 0)


class AutoCast(EventPlugin):
    PLUGIN_ID = _PLUGIN_ID
    PLUGIN_NAME = _("AutoCast")
    PLUGIN_ICON = "gtk-jump-to"
    PLUGIN_VERSION = "1.0"
    PLUGIN_DESC = ("Plays a random not yet listened podcast")

    def __init__(self):
        self.__feeds = pickle.load(file(join(const.USERDIR, "feeds")))
        self.__seconds_of_music = 0

    def plugin_on_song_started(self, song):
        if not song or not app.player:
            return False
        if not app.player.can_play_uri("http://"):
            return False
        if len(app.window.playlist.q):
            return False
        if self.__seconds_of_music < get_cfg("minmusic"):
            return False
        if get_cfg("minmusic") and song["~filename"].startswith("http://"):
            self.__seconds_of_music = 0
            return False
        filtr = lambda x: '~#playcount' not in x and '~#skipcount' not in x
        items = [[i for i in f if filtr(i)] for f in self.__feeds]
        items = list(itertools.chain(*items))
        item = random.choice(items)
        app.window.playlist.enqueue([item])

    def plugin_on_song_ended(self, song, stopped):
        if not song:
            return False
        if not song["~filename"].startswith("http://"):
            self.__seconds_of_music += app.player.get_position() / 1000
        else:
            self.__seconds_of_music = 0
        return False

    @classmethod
    def PluginPreferences(cls, window):
        prefs = Preferences()
        return prefs
