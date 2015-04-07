from gi.repository import Gtk, GObject

from quodlibet import app
from quodlibet import config
from quodlibet import qltk
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
        tag_entry = Gtk.Entry()
        tag_entry.set_text(get_cfg("tag"))

        labels["tag"].set_mnemonic_widget(tag_entry)
        table.attach(tag_entry, 1, 2, 0, 1)

        def tag_changed(scale):
            value = scale.get_text()
            set_cfg("tag", value)
            self.emit("changed")
        tag_entry.connect('changed', tag_changed)

        self.pack_start(qltk.Frame("Preferences", child=table),
                        True, True, 0)


class SkipSameArtist(PlayOrderPlugin):
    PLUGIN_ID = "Skip same tag"
    PLUGIN_NAME = _("Skip same tag")
    name = "skip_same_tag"
    display_name = _("Skip same tag")
    accelerated_name = _("_Skip same tag")
    replaygain_profiles = ["track"]
    is_shuffle = False

    def __init__(self, playlist):
        self.playlist = playlist

    def next(self, playlist, iter):
        if iter is None:
            return playlist.get_iter_first()

        if len(playlist) < 2:
            return playlist.iter_next(iter)

        next = playlist.iter_next(iter)

        tag = get_cfg("tag")
        songs = playlist.get()
        current = app.player.song[tag]
        found = False
        for song_number, song in enumerate(songs):
            if song == app.player.song:
                found = True

            if found and song[tag] != current:
                next = playlist.get_iter((song_number,))
                break

        return next

    def previous(self, playlist, iter):
        if len(playlist) == 0:
            return None

        if iter is None:
            return playlist[(len(playlist) - 1,)].iter

        path = max(1, playlist.get_path(iter).get_indices()[0])
        try:
            return playlist.get_iter((path - 1,))
        except ValueError:
            if playlist.repeat:
                return playlist[(len(playlist) - 1,)].iter
        return None

    @classmethod
    def PluginPreferences(cls, window):
        prefs = Preferences()
        return prefs
