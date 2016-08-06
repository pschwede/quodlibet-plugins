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
from quodlibet import get_user_dir
from quodlibet import config
from quodlibet.util.dprint import print_d
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
        # value, lower, upper, step_increment, page_increment
        minmusic_scale = Gtk.HScale(adjustment=Gtk.Adjustment(5, 0, 60, 1, 5))
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
        self.load()
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

            # DEBUG: podcast still in storage?
            found = False
            for f in self.__feeds:
                for s in f:
                    if s['~filename'] == song['~filename']:
                        found = True
                        break
                if found:
                    break
            print_d("Song in __feeds: %s" % found)

            app.librarian.changed([song])
            self.write()
            if get_cfg("minmusic") > 1:
                return False
        track = self.get_track()
        if track:
            self.enqueue_track(track)

    def write(self):
        with open(os.path.join(get_user_dir(), "feeds"), "wb") as f:
            pickle.dump(self.__feeds, f)

    def load(self):
        with open(os.path.join(get_user_dir(), "feeds"), "rb") as f:
            self.__feeds = pickle.load(f)

    @staticmethod
    def pick_one_of_top(items, key):
        s_items = sorted(
                items,
                key=key,
                reverse=True
                )[:max(1,len(items)/5)]
        print_d(str([key(x) for x in s_items]))
        return random.choice(s_items)

    def get_track(self, preference={"~#length": -1./60/30, "~#added": 1000./time.time(), "~#size": -1.5e-7}):
        items = list()
        def filtr(x):
            return not bool(x('~#laststarted')) and not bool(x('~#lastplayed'))
        def weight(x):
            num_preferences = len(preference)
            res = 1./num_preferences
            for key in preference:
                val = float(x(key)) / num_preferences
                if not val:
                    val = 0.5
                res += preference[key] * val
            return res

        for feed in [f for f in self.__feeds]:
            if not feed:
                print_d("Not playing %s.." % feed)
                continue
            filtered = [x for x in feed if filtr(x)]
            if not filtered:
                print_d("Not playing %s.." % feed[0])
                continue
            items.append(self.pick_one_of_top(filtered, weight))
        if items:
            print_d("Picking one podcast out of %i:" % len(items))
            podcast = self.pick_one_of_top(items, weight)
            print_d(str(podcast))
            return podcast
        print_d("There aren't any items I could play.")
        return None

    def enqueue_track(self, track):
        if track and track.can_add:
            app.window.playlist.enqueue([track])
            if app.player.song is None:
                app.player.next()

    def plugin_on_song_ended(self, song, stopped):
        if not song:
            return False
        if song["~filename"].startswith("http://"):  # podcast
            song["~#lastplayed"] = int(time.time())
            print_d("Before write: %s" % dict(song))
            self.write()
            self.load()
            for feed in self.__feeds:
                for s in feed:
                    if song["~filename"] == s["~filename"]:
                        print_d("Found after write: %s" % dict(song))
            self.__seconds_of_music = 0
        elif app.player.get_position() > 0:
                self.__seconds_of_music += app.player.get_position() / 1000
        if self.__seconds_of_music < get_cfg("minmusic"):
            return False

    @classmethod
    def PluginPreferences(cls, window):
        prefs = Preferences()
        return prefs
