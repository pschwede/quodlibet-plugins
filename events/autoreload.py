# -*- coding: utf-8 -*-

import gobject
from plugins.events import EventPlugin
from quodlibet import widgets
from quodlibet.qltk.msg import Message, WarningMessage

class AutoRefresh(EventPlugin):
    PLUGIN_ID = 'Auto Refresh Library Query'
    PLUGIN_NAME = _('Auto Refresh')
    PLUGIN_DESC = ("Refreshes the currently shown browser query when has song ended.")
    PLUGIN_VERSION = "1"

    def plugin_on_song_ended(self, song, skipped):
        print "[Auto Refresh] Refreshing.."
        gobject.timeout_add(1000, widgets.main.browser.activate)
