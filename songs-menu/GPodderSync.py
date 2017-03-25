# Copyright 2014 Peter Schwede
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation

import os.path
import pickle

import opml
import requests
from mygpoclient import simple

from gi.repository import Gtk, GObject

import quodlibet
from quodlibet import _
from quodlibet import app
from quodlibet import const
from quodlibet import config
from quodlibet import browsers
from quodlibet import qltk
from quodlibet.util.dprint import print_d
from quodlibet.qltk.entry import UndoEntry
from quodlibet.browsers.audiofeeds import Feed
from quodlibet.browsers.audiofeeds import AudioFeeds
from quodlibet.plugins.songsmenu import SongsMenuPlugin

_PLUGIN_ID = "gpoddersync"

_SETTINGS = {
    "gpodder.net/name": ["_Nickname",
                         "Login name for Gpodder.net",
                         ""],
    "gpodder.net/password": ["_Password",
                             "Login name for Gpodder.net",
                             ""],
    "gpodder.net/device": ["_Device",
                           "Name of device. Leave empty to fetch all podcasts",
                           ""]
}


def get_cfg(option):
    cfg_option = "%s_%s" % (_PLUGIN_ID, option)
    default = _SETTINGS[option][2]
    if option in ["gpodder.net/name", "gpodder.net/password", "gpodder.net/device"]:
        return config.get("plugins", cfg_option, default)


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

        correct_browser = not isinstance(app.browser, AudioFeeds)

        table = Gtk.Table(2, 2)
        table.set_col_spacings(6)
        table.set_row_spacings(6)

        labels = {}
        entries = {}
        for idx, key in enumerate(["gpodder.net/name",
                                   "gpodder.net/password",
                                   "gpodder.net/device"]):
            text, tooltip = _SETTINGS[key][:2]
            label = Gtk.Label(label=text)
            entry = UndoEntry()
            entry.set_text(get_cfg(key))
            if key == "gpodder.net/password":
                entry.set_visibility(False)
            entries[key] = entry
            labels[key] = label
            labels[key].set_mnemonic_widget(entry)
            label.set_tooltip_text(tooltip)
            label.set_alignment(0.0, 0.5)
            label.set_padding(0, 6)
            label.set_use_underline(True)
            table.attach(label, 0, 1, idx, idx+1,
                         xoptions=Gtk.AttachOptions.FILL |
                         Gtk.AttachOptions.SHRINK)
            table.attach(entry, 1, 2, idx, idx+1,
                         xoptions=Gtk.AttachOptions.FILL |
                         Gtk.AttachOptions.SHRINK)
        # value, lower, upper, step_increment, page_increment

        def gpodder_go(button):
            for key in entries:
                value = entries[key].get_text()
                set_cfg(key, value)
            name = get_cfg("gpodder.net/name")
            password = get_cfg("gpodder.net/password")
            device = get_cfg("gpodder.net/device")
            fetch_gpodder(name, password, device)

        button = Gtk.Button(label=_("Fetch!" if correct_browser else "(Fetch) Please switch to a different browser!"), sensitive=correct_browser)
        button.connect("pressed", gpodder_go)
        table.attach(button, 0, 2, idx+1, idx+2)

        self.pack_start(qltk.Frame("Preferences", child=table),
                        True, True, 0)


def update_feeds(subscriptions):
    feeds = []
    with open(os.path.join(quodlibet.get_user_dir(), "feeds"), "rb") as f:
        try:
            feeds = pickle.load(f)
        except:
            print_d("Couldn't read feeds.")

    subbed = frozenset([f.uri for f in feeds])
    newfeeds = list()

    for subscription in subscriptions:
        try:
            r = requests.get(subscription)
        except requests.exceptions.ConnectionError as e:
            print_d("ConnectionError %s - %s" % (subscription, e));
            continue

        if not r.status_code == 200:
            print_d("Cannot access %s - %i" % (subscription, r.status_code))
            continue

        feed = Feed(subscription)
        if feed.uri in subbed:
            print_d("Feed already subscribed: %s" % subscription)
            continue
        feed.changed = feed.parse()
        if feed:
            print_d("Appending %s" % subscription)
            feeds.append(feed)
            newfeeds.append(feed)
        else:
            print_d("Feed could not be added: %s" % subscription)

    print_d("Adding %i feeds." % len(newfeeds))
    with open(os.path.join(quodlibet.get_user_dir(), "feeds"), "wb") as f:
        pickle.dump(feeds, f)
    app.browser.reload(app.library)  # adds feeds

    #app.browser.restore()


def fetch_opml(url):
    try:
        outline = opml.parse(url)
    except IOError:
        print_d("Failed opening OPML %s" % url)
        return []
    GObject.idle_add(lambda: update_feeds([x.xmlUrl for x in outline]))


def fetch_gpodder(name, password, device):
    client = simple.SimpleClient(name, password)
    subscriptions = client.get_subscriptions(device)
    GObject.idle_add(lambda: update_feeds(subscriptions))


class OPMLsupport(SongsMenuPlugin):
    PLUGIN_ID = _PLUGIN_ID
    PLUGIN_NAME = "GPodderSync"
    PLUGIN_ICON = "gtk-jump-to"
    PLUGIN_VERSION = "1.0"
    PLUGIN_DESC = ("Sync your podcasts with gpodder.net")

    @classmethod
    def PluginPreferences(cls, window):
        prefs = Preferences()
        return prefs
