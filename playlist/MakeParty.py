# -*- coding: utf-8 -*-
# Copyright 2014 Peter Schwede
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation

from quodlibet import _
from quodlibet import app
from quodlibet.plugins.playlist import PlaylistPlugin
from quodlibet.qltk import Icons

from random import shuffle, choice

class MakeParty(PlaylistPlugin):
    PLUGIN_ID = "MakeParty"
    PLUGIN_NAME = _("Make Party")
    PLUGIN_DESC = _("Mixes the playlist according bpm and genre.")
    PLUGIN_ICON = Icons.SYSTEM_RUN

    def plugin_playlist(self, playlist):
        def sort_key(x):
            try:
                bpm = float(x('~#bpm'))
            except (ValueError, KeyError):
                bpm = 100.
            try:
                rating = float(x("~#rating"))
            except (ValueError, KeyError):
                rating = 0.5
            return bpm + 80*rating

        fresh = set(playlist)
        old_genre = None
        while len(fresh) > 0:
            # prepare set of genres and a sorted list by bpm
            limit = 2
            picked = set()
            reasons = {'genre': 0, 'picked': 0}

            genres = [""]
            for x in fresh:
                try:
                    if x["genre"] != old_genre:
                        genres.append(x["genre"])
                except KeyError:
                    pass
            genres = list(set(genres))

            ranked = sorted(fresh, key=sort_key)

            # pick a genre
            genre = choice(genres)
            
            # add fast songs of same genre
            for song in ranked[::-1]:
                try:
                    song_genre = song["genre"]
                except KeyError:
                    song_genre = ""
                if song_genre != genre:
                    reasons['genre'] += 1
                    continue
                if song in picked:
                    reasons['picked'] += 1
                    continue

                app.window.playlist.enqueue([song])
                picked.add(song)

                limit -= 1
                if limit == 0:
                    break

            # pick a slow song
            for song in ranked:
                if song in picked:
                    continue
                try:
                    if song["genre"] != genre:
                        continue
                except KeyError:
                    if "" != genre:
                        continue
                app.window.playlist.enqueue([song])
                picked.add(song)
                break

            # if too few were picked: add one random but of same genre
            if len(picked)-1 < limit:
                if reasons['genre'] < reasons['picked']:
                    song = choice([x for x in fresh if x["genre"] == genre])
                    app.window.playlist.enqueue([song])
                    picked.add(song)

            for song in picked:
                fresh.remove(song)

        return True

    def plugin_handles(self, playlists):
        return len(playlists) >= 1 and len(playlists[0].songs) > 1
