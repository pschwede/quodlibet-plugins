# Copyright 2014 Peter Schwede
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation

import os.path
import time
import random
import pickle

from gi.repository import Gtk, GObject

from quodlibet import app
from quodlibet import qltk
from quodlibet import const
from quodlibet import config
from quodlibet.plugins.events import EventPlugin

_PLUGIN_ID = "autocast"

_SETTINGS = {
    "minmusic": ["_Music minutes:",
                 "Music minimum between podcasts in seconds",
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

        self.pack_start(qltk.Frame("Preferences", child=table),
                        True, True, 0)


def score(item, preference, reference):
    assert preference.keys() == reference.keys()
    res = 0
    for key in preference:
        try:
            res += preference[key] * item[key] / reference[key]
        except KeyError:
            continue
    return res / len(preference)


class AutoCast(EventPlugin):
    PLUGIN_ID = _PLUGIN_ID
    PLUGIN_NAME = "AutoCast"
    PLUGIN_ICON = "gtk-jump-to"
    PLUGIN_VERSION = "1.0"
    PLUGIN_DESC = ("Plays a random not yet listened podcast")

    def __init__(self):
        with open(os.path.join(const.USERDIR, "feeds"), "r") as f:
            self.__feeds = pickle.load(f)
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
        if song["~filename"].startswith("http://"):
            song["~#laststarted"] = int(time.time())
            app.librarian.changed([song])
            if get_cfg("minmusic") > 1:
                return False

        track = self.get_track(current_song=song)
        self.enqueue_track(track)

    def get_track(self, current_song,
                  preference={"~#length": -1.0, "~#added": 1.0}):
        """
        OLD:
        """
        feeds_with_items = []
        filtr = lambda x: '~#playcount' not in x and '~#skipcount' not in x
        for f in self.__feeds:
            items = [i for i in f if filtr(i)]
            if items:
                feeds_with_items.append(items)
        feed_items = random.choice(feeds_with_items)
        item = random.choice([i for i in feed_items])
        return item
        """
        NEW: Take the newest entry. BUT: laststarted won't be saved that way.
        filtr = lambda x: '~#laststarted' not in x
        items = []
        for feed_items in self.__feeds:
           items += [f for f in feed_items if filtr(f)]
        reference = {}
        for key in preference:
           reference[key] = max([i[key] for i in items if key in i])
        items = sorted(items, key=lambda x: -score(x, preference, reference))
        for item in items:
           if item["~filename"] == current_song["~filename"]:
            continue
           break
        return item
        """

    def enqueue_track(self, track):
        if track.can_add:
            app.window.playlist.enqueue([track])
            if app.player.song is None:
                app.player.next()

    def plugin_on_song_ended(self, song, stopped):
        if not song:
            return False
        if song["~filename"].startswith("http://"):  # podcast
            self.__seconds_of_music = 0
        elif app.player.get_position() > 0:
                self.__seconds_of_music += app.player.get_position() / 1000
        if self.__seconds_of_music < get_cfg("minmusic"):
            return False

    @classmethod
    def PluginPreferences(cls, window):
        prefs = Preferences()
        return prefs
