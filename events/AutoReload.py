# -*- coding: utf-8 -*-

"""(c) 2014 pschwede"""

from gi.repository import GObject

from quodlibet import _
from quodlibet.util.dprint import print_d
from quodlibet.plugins.events import EventPlugin
from quodlibet import app


class AutoRefresh(EventPlugin):
    """Refreshes the currently shown browser query when a song has ended."""
    PLUGIN_ID = 'Auto Refresh Library Query'
    PLUGIN_NAME = 'AutoRefresh'
    PLUGIN_DESC = ("Refreshes the currently shown browser query when a song "
                   "has ended.")
    PLUGIN_VERSION = "1.1"

    def plugin_on_song_ended(self, song, skipped):
        """action on song ended"""
        print_d("[Auto Refresh] Refreshing..")
        GObject.timeout_add(1500, app.window.browser.activate)
