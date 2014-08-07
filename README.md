# My Quodlibet plugins

* ~~__Autorefresh__: Reloads the Browser view (in some search queries, by that,
  it makes sure no song is played over and over again or that the playlist
  doesn`t stop)~~
* ~~__AudioScrobble Submission__: Fork of the official plugin with more
  options.~~
* __AutoSeek__: Plays only a few seconds of a track. Skipping rate and relative
  seek position are configurable.
* __AutoCast__: Creates a radio rotation between music and talk. Repeatingly
  enqueues podcast entries after playing music. The seconds of music between the
  podcasts are configurable.


## Installation on Unix

```bash
git clone https://github.com/pschwede/qlplugins.git ~/.quodlibet/plugins/
```

or copy the events folder to `~/.quodlibet/plugins/`:

```bash
git clone https://github.com/pschwede/qlplugins.git
mkdir -p ~.quodlibet/plugins/events/
cp qlplugins/events/*.py ~.quodlibet/plugins/events/
```
