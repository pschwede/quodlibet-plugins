# -*- coding: utf-8 -*-
# Copyright 2014 Nick Boultbee
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation

from quodlibet.plugins.playlist import PlaylistPlugin
from quodlibet.qltk import Icons

from random import shuffle, choice

class MakeParty(PlaylistPlugin):
    PLUGIN_ID = "MakeParty"
    PLUGIN_NAME = _("Make Party")
    PLUGIN_DESC = _("Mixes the playlist according bpm and genre.")
    PLUGIN_ICON = Icons.SYSTEM_RUN

    def plugin_playlist(self, playlist):
        try:
            for song in playlist:
                    assert song["bpm"]
                    assert song["genre"]
        except KeyError:
            print_d("CRITICAL: All songs need to have genre and bpm defined!")
            return
        for song in playlist:
            if not song("~#rating"):
                song["~#rating"] = float(0.0)
            song.write()

        fresh = set(playlist)
        playlist.clear()
        old_genre = None
        while len(fresh) > 0:
            # prepare set of genres and a sorted list by bpm
            limit = 2
            picked = set()
            reasons = {'genre': 0, 'picked': 0}
            genres = list(set([x["genre"] for x in fresh]))
            ranked = sorted(fresh, key=lambda x: float(x('~#bpm')) + 80*float(x("~#rating")))

            # pick a genre
            genre = choice(genres)
            while genre == old_genre:
                genre = choice(genres)
            
            # add fast songs of same genre
            for song in ranked[::-1]:
                if song["genre"] != genre:
                    #print_d("X %s, %s has NOT genre %s" % (song["genre"], song["title"], genre))
                    reasons['genre'] += 1
                    continue
                if song in picked:
                    #print_d("X %s, %s has already been picked" % (song["genre"], song["title"]))
                    reasons['picked'] += 1
                    continue

                #print_d("O %s, %s HAS genre %s and was not picked yet." % (song["title"], song["genre"], genre))
                playlist.append(song)
                picked.add(song)

                limit -= 1
                if limit == 0:
                    break

            # pick a slow song
            for song in ranked:
                if song["genre"] != genre or song in picked:
                    continue
                playlist.append(song)
                picked.add(song)
                break

            # if too few were picked: add one random but of same genre
            if len(picked)-1 < limit:
                if reasons['genre'] < reasons['picked']:
                    for song in shuffle(fresh):
                        if song["genre"] == genre:
                            playlist.append(song)
                            picked.add(song)

            for song in picked:
                fresh.remove(song)

            #print_d([(x['title'], x['genre']) for x in picked])
        playlist.finalize()
        return True

    def plugin_handles(self, playlists):
        return len(playlists) == 1 and len(playlists[0].songs) > 1
