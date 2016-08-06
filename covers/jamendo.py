# -*- coding: utf-8 -*-
# Copyright 2013 Simonas Kazlauskas
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation

import json
from os import path
from gi.repository import Soup, GLib

from quodlibet.plugins.cover import CoverSourcePlugin, cover_dir
from quodlibet.util.dprint import print_d
from quodlibet.util.http import download_json
from quodlibet.util.cover.http import HTTPDownloadMixin
from quodlibet.util.path import escape_filename


class JamendoCover(CoverSourcePlugin, HTTPDownloadMixin):
    PLUGIN_ID = "jamendo-cover"
    PLUGIN_NAME = _("Jamendo cover source")
    PLUGIN_DESC = _("Use Jamendo database to fetch covers")
    PLUGIN_VERSION = "1.0"

    @staticmethod
    def priority():
        return 0.33  # No cover size guarantee, accurate

    @property
    def cover_path(self):
        mbid = self.song.get('musicbrainz_albumid', None)
        # It is beneficial to use mbid for cover names.
        if mbid:
            return path.join(cover_dir, escape_filename(mbid))
        else:
            return super(JamendoCover, self).cover_path

    @property
    def url(self):
        _url = ('https://api.jamendo.com/v3.0/albums/?'
                'format=json'
                '&imagesize=500'
                '&client_id=6c6873dc')
        artist = self.song.get('artist', '').replace(' ', '+')
        artist = Soup.URI.encode(artist)
        album = self.song.get('album', '').replace(' ', '+')
        album = Soup.URI.encode(album)
        if artist:
            return _url + '&artist_name=' + artist
        elif album:
            return _url + '&name=' + album
        else:
            return None   # Not enough data

    def search(self):
        if not self.url:
            return self.emit('search-complete', [])
        msg = Soup.Message.new('GET', self.url)
        download_json(msg, self.cancellable, self.album_data, None)

    def album_data(self, message, json, data=None):
        if not json:
            print_d('Server did not return valid JSON')
            return self.emit('search-complete', [])
        results = json.get('results', {})
        if not results:
            print_d('Album data is not available')
            return self.emit('search-complete', [])

        def score(r):
            album = self.song.get('album', 'Unknown')
            artist = self.song.get('artist', 'Unknown')
            _score = 0
            for key, value in {'name': album, 'artist_name': artist}.items():
                if not value:
                    continue
                for word in r[key].split(' '):
                    if word in value:
                        _score += 1
            return _score

        result = [r['image'] for r in sorted(results, key=score, reverse=True)]
        self.emit('search-complete', result)

    def fetch_cover(self):
        if not self.url:
            return self.fail('Not enough data to get cover from Jamendo')

        def search_complete(self, res):
            self.disconnect(sci)
            if res:
                print res
                self.download(Soup.Message.new('GET', res[0]))
            else:
                return self.fail('No cover was found')
        sci = self.connect('search-complete', search_complete)
        self.search()
