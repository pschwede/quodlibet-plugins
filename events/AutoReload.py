# -*- coding: utf-8 -*-

"""(c) 2014 pschwede"""

from gi.repository import GObject

from quodlibet.plugins.events import EventPlugin
from quodlibet import app


class AutoRefresh(EventPlugin):
    """Refreshes the currently shown browser query when a song has ended."""
    PLUGIN_ID = 'Auto Refresh Library Query'
    PLUGIN_NAME = 'AutoRefresh'
    PLUGIN_DESC = ("Refreshes the currently shown browser query when a song "
                   "has ended.")
    PLUGIN_VERSION = "1"

    def plugin_on_song_ended(self, song, skipped):
        """action on song ended"""
        print "[Auto Refresh] Refreshing.."
        GObject.timeout_add(1000, app.window.browser.activate)
