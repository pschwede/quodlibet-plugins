# -*- coding: utf-8 -*-
# Copyright 2013 Simonas Kazlauskas
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation

from os import path
from gi.repository import Soup

from quodlibet.plugins.cover import CoverSourcePlugin, cover_dir
from quodlibet.util.http import download_json
from quodlibet.util.cover.http import HTTPDownloadMixin
from quodlibet.util.path import escape_filename


class GPodderCover(CoverSourcePlugin, HTTPDownloadMixin):
    PLUGIN_ID = "gpodder-cover"
    PLUGIN_NAME = _("gPodder cover source")
    PLUGIN_DESC = _("Use gPodder.net database to fetch covers")
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
            return super(GPodderCover, self).cover_path

    @property
    def url(self):
        # http://gpodder.net/search.json?q="XLR8R+Magazine"
        _url = 'http://gpodder.net/search.json?'
        album = self.song.get('album', '').replace(' ', '+')
        album = Soup.URI.encode(album)
        if album:
            return _url + 'q="' + album + '"'
        else:
            return None  # Not enough data

    def search(self):
        if not self.url:
            return self.emit('search-complete', [])
        msg = Soup.Message.new('GET', self.url)
        download_json(msg, self.cancellable, self.album_data, None)

    def album_data(self, message, json, data=None):
        if not json:
            print_d('Server did not return valid JSON')
            return self.emit('search-complete', [])
        results = json
        if not results:
            print_d('Album data is not available')
            return self.emit('search-complete', [])

        def score(r):
            album = self.song.get('album', 'Unknown')
            _score = 0
            for key, value in {'title': album}.items():
                if not value:
                    continue
                for word in r[key].split(' '):
                    if word in value:
                        _score += 1
                    if value in word:
                        _score += 1
            return _score

        result = sorted([r for r in results if score(r) > 0], key=score,
                                                              reverse=True)
        result = [r['scaled_logo_url'] for r in result]
        result = list(set(result))
        self.emit('search-complete', result)

    def fetch_cover(self):
        if not self.url:
            return self.fail('Not enough data to get cover from gPodder')

        def search_complete(self, res):
            self.disconnect(sci)
            if res:
                print res
                self.download(Soup.Message.new('GET', res[0]))
            else:
                return self.fail('No cover was found')
        sci = self.connect('search-complete', search_complete)
        self.search()
