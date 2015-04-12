# My Quodlibet plugins

* __Autorefresh__: Reloads the Browser view (in some search queries, by that,
  it makes sure no song is played over and over again or that the playlist
  doesn't stop)
* ~~__AudioScrobble Submission__: Fork of the official plugin with more
  options.~~
* __AutoSeek__: Plays only a few seconds of a track. Skipping rate and relative
  seek position are configurable.
* __AutoCast__: Creates a radio rotation between music and talk. Repeatingly
  enqueues podcast entries after playing music. The seconds of music between the
  podcasts are configurable.
* __GPodderSync__: Fetch podcast urls from gPodder.net. In future, there will be more general OPML support.
* __gPodder cover source__: Download podcast logos from the gPodder.net API
* __Jamendo cover source__: Download podcast logos from the Jamendo.com API


## Installation on Unix

```bash
git clone https://github.com/pschwede/quodlibet-plugins.git ~/.quodlibet/plugins/
```

You need to restart quodlibet to see and activate the plugins in Music-->Plugins.
