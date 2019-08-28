# -*- coding: utf-8 -*-
from gi.repository import Gtk

from subprocess import check_output, CalledProcessError
from multiprocessing import Pool, cpu_count
import sqlite3
from os.path import expanduser

from quodlibet import _
from quodlibet import formats
from quodlibet.qltk import Icons
from quodlibet.plugins.songsmenu import SongsMenuPlugin
from quodlibet.util.path import iscommand
from quodlibet.util.dprint import print_d
from quodlibet.util import connect_obj

class SyncMixxxCommand(object):
    def __init__(self):
        self.title = "Sync rating with Mixxx"

    def exists(self):
        return True

    def run(self, songs):
        try:
            con = sqlite3.connect(expanduser("~/.mixxx/mixxxdb.sqlite"))
        except Exception as e:
            print_d("Failed: %s" % e.message)
        cur = con.cursor()
        for song in songs:
            query = ( "SELECT id "
                    "FROM track_locations "
                    "WHERE location=\"{}\";" ).format(song('~filename').replace("\"", "\\\""))
            try:
                cur.execute(query)
                print_d("Success: %s" % query)
            except Exception as e:
                print_d("Failed: %s" % query)
                continue

            location_id = cur.fetchone()
            if location_id is None:
                print_d("Failed: %s" % query)
                continue

            query = ( "UPDATE library "
                    "SET rating = {} "
                    "WHERE location = {};" ).format(
                        5 * song('~#rating'),
                        location_id[0]
                        )
            try:
                cur.execute( query )
                print_d("Success: %s" % query)
                con.commit()
            except Exception as e:
                print_d("Failed: %s" % query)
        con.close()
        print_d("All done.")


class SyncMixxx(SongsMenuPlugin):
    PLUGIN_ID = 'SyncMixxx'
    PLUGIN_NAME = _(u'SyncMixxx')
    PLUGIN_DESC = _("Synchronizes ratings to Mixxx")
    PLUGIN_ICON = Icons.SYSTEM_RUN

    def __init__(self, *args, **kwargs):
        super(SyncMixxx, self).__init__(*args, **kwargs)
        submenu = Gtk.Menu()
        self.command = SyncMixxxCommand()
        item = Gtk.MenuItem(label=self.command.title)
        if not self.command.exists():
            item.set_sensitive(False)
        else:
            connect_obj(item, 'activate', self.__set, self.command)
        submenu.append(item)
        if submenu.get_children():
            self.set_submenu(submenu)
        else:
            self.set_sensitive(False)

    def __set(self, command):
        self.command = command

    def plugin_songs(self, songs):
        if self.command:
            self.command.run(songs)
