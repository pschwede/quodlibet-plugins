# -*- coding: utf-8 -*-
from gi.repository import Gtk

from subprocess import check_output, CalledProcessError
from quodlibet.qltk import Icons
from quodlibet.plugins.songsmenu import SongsMenuPlugin
from quodlibet.util.path import iscommand
from quodlibet.util import connect_obj


class BPMCommand(object):
    def __init__(self, title, command):
        self.title = title
        self.command = command

    def exists(self):
        res = True
        for subcommand in self.command.split("|"):
            subcommand = subcommand.lstrip().rstrip()
            res = res and iscommand(subcommand.split()[0])
        return res

    def run(self, songs):
        for song in songs:
            cmd = self.command % song("~filename")
            try:
                bpm = check_output(cmd, shell=True)
            except CallError, e:
                print_d("Fail: %s" % cmd)
                print_d(e)
            finally:
                if bpm:
                    song["bpm"] = check_output(self.command % song("~filename"), shell=True).rstrip()


class BPMDetector(SongsMenuPlugin):
    PLUGIN_ID = 'BPMDetector'
    PLUGIN_NAME = _(u'Detector BPM')
    PLUGIN_DESC = _("Analyzes songs for beats per minute")
    PLUGIN_ICON = Icons.SYSTEM_RUN

    commands = [
        BPMCommand("bpm-tools", ("sox -v 0.98 \"%s\" -t raw -r 44100 -e float -c 1 -"
                                 " | bpm -f \"%%.2f\""))
        ]

    def __init__(self, *args, **kwargs):
        super(BPMDetector, self).__init__(*args, **kwargs)
        self.command = None
        submenu = Gtk.Menu()
        print_d("Done: init")
        for command in self.commands:
            item = Gtk.MenuItem(label=command.title)
            if not command.exists():
                item.set_sensitive(False)
            else:
                connect_obj(item, 'activate', self.__set, command)
            submenu.append(item)
        print_d("Done: submenu")
        if submenu.get_children():
            self.set_submenu(submenu)
        else:
            self.set_sensitive(False)
        print_d("Done: append submenu")

    def __set(self, command):
        self.command = command
        print_d("Done: __set")

    def plugin_songs(self, songs):
        if self.command:
            self.command.run(songs)
