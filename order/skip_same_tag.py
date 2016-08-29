from gi.repository import Gtk, GObject

from quodlibet import app
from quodlibet import config
from quodlibet import qltk
from quodlibet.qltk.entry import ValidatingEntry
from quodlibet.util.dprint import print_d
from quodlibet.plugins.playorder import PlayOrderPlugin

_PLUGIN_ID = "skip_same_tag"
_SETTINGS = {
    "tag": ["_Tag",
            "Tag to check for same value",
            "artist"],
}


def get_cfg(option):
    cfg_option = "%s_%s" % (_PLUGIN_ID, option)
    default = _SETTINGS[option][2]
    if option in "tag":
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

        table = Gtk.Table(2, 2)
        table.set_col_spacings(6)
        table.set_row_spacings(6)

        labels = {}
        for idx, key in enumerate(["tag"]):
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

        def is_valid(x):
            return len(str(app.player.song(x))) > 0

        tag_entry = ValidatingEntry(validator=is_valid)
        tag_entry.set_text(get_cfg("tag"))

        labels["tag"].set_mnemonic_widget(tag_entry)
        table.attach(tag_entry, 1, 2, 0, 1)

        def tag_changed(scale):
            value = scale.get_text()
            if is_valid(value):
                set_cfg("tag", value)
                self.emit("changed")

        tag_entry.connect('changed', tag_changed)

        self.pack_start(qltk.Frame("Preferences", child=table),
                        True, True, 0)


class SkipSameTag(PlayOrderPlugin):
    PLUGIN_ID = "Skip same tag"
    PLUGIN_NAME = _("Skip same tag")
    name = "skip_same_tag"
    display_name = _("Skip same tag")
    accelerated_name = _("_Skip same tag")
    replaygain_profiles = ["track"]
    is_shuffle = False
    current = None

    def __init__(self, playlist):
        self.playlist = playlist

    def next(self, playlist, iter):
        if iter is None:
            return playlist.get_iter_first()

        if len(playlist) < 2:
            return playlist.iter_next(iter)

        tag = get_cfg("tag")
        played_song = app.player.song

        try:
            self.current = played_song(tag)
        except KeyError:
            print_d("Key not in song while retreiving current tag value: %s" % tag)


        next = None
        found = False
        songs = playlist.get()
        print_d("%i songs in playlist." % len(songs))
        for song_number, song in enumerate(songs):
            if song == played_song:
                found = True
                continue

            if found:
                try:
                    if song(tag) == self.current:
                        continue
                except KeyError:
                    # not having the tag is enough to be played.
                    print_d("Key not in song while looking for current song: %s" % tag)

            if found:
                next = playlist.get_iter((song_number,)) or playlist.get_iter((0,))
                break

        if not found or not next:
            for song_number, song in enumerate(songs):
                try:
                    if song(tag) != self.current:
                        next = playlist.get_iter((song_number,))
                        break
                except KeyError:
                    # not having the tag is enough to be played.
                    print_d("Key not in song while looking for next song: %s" % tag)
                    next = playlist.get_iter((song_number,))

        print_d("New song: %s" % next)
        return next

    def previous(self, *args):
        return super(SkipSameTag, self).previous(*args)

    @classmethod
    def PluginPreferences(cls, window):
        prefs = Preferences()
        return prefs
