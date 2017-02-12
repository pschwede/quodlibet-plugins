# -*- coding: utf-8 -*-
from gi.repository import Gtk

from subprocess import check_output, CalledProcessError
from multiprocessing import Pool, cpu_count

from quodlibet import _
from quodlibet import formats
from quodlibet.qltk import Icons
from quodlibet.plugins.songsmenu import SongsMenuPlugin
from quodlibet.util.path import iscommand
from quodlibet.util.dprint import print_d
from quodlibet.util import connect_obj


def get_bpm(cmd_path):
    cmd, path = cmd_path
    TAG = "bpm"
    try:
        bpm = check_output(cmd, shell=True)
        if bpm:
            song = formats.MusicFile(path)
            try:
                assert song.can_change(TAG)
            except AssertionError:
                raise ValueError("File does not support bpm tags.")
            song[TAG] = bpm
            try:
                assert song[TAG]
            except KeyError:
                raise ValueError("Couln't assign tag value.")
            song.write()
            song = formats.MusicFile(path)
            try:
                assert song[TAG]
            except KeyError:
                raise ValueError("Couldn't load tag value.")
            return 'Success %s = %s' % (path, song[TAG])
        raise ValueError("'%s' is no valid bpm value." % bpm)
    except (CalledProcessError, ValueError), e:
        res = "Fail: %s" % cmd
        res += "\n%s" % e
        return res


class BPMCommand(object):
    def __init__(self, title, command, terminal=False):
        self.title = title
        self.command = command
        self.terminal = terminal

    def exists(self):
        res = True
        for subcommand in self.command.split("|"):
            subcommand = subcommand.lstrip().rstrip()
            res = res and iscommand(subcommand.split()[0])
        return res

    def run(self, songs):
        if self.terminal:
            return
        p = Pool(processes=min(len(songs), cpu_count()))
        cmds = [(self.command % s("~filename"), s("~filename")) for s in songs]
        print_d('Running pool on %s' % cmds)
        r = [p.apply_async(get_bpm, (cmd,)) for cmd in cmds]
        p.close()
        p.join()
        for x in r:
            print_d(str(x.get()))


class BPMDetector(SongsMenuPlugin):
    PLUGIN_ID = 'BPMDetector'
    PLUGIN_NAME = _(u'Detector BPM')
    PLUGIN_DESC = _("Analyzes songs for beats per minute")
    PLUGIN_ICON = Icons.SYSTEM_RUN

    commands = [
        BPMCommand("bpm-tools", ("sox -v 0.98 \"%s\" -t raw -r 44100 -e float -c 1 -"
                                 " | bpm -m 30 -x 160 -f \"%%.2f\""))
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
