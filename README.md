# My Quodlibet plugins

* ~~*Autorefresh*: Reloads the Browser view (in some search queries, by that, it makes sure no song is played over and over again or that the playlist doesn`t stop)~~

* ~~*AudioScrobble Submission*: Fork of the official plugin, but with more options.~~

* *AutoSeek*: Skip into the next song and skip after some seconds. Configurable.

* *AutoCast*: Get a real talk radio rotation by enqueuing a random yet unplayed
  podcast entry after some seconds of music have been played. Configurable.


## Installation on Unix

```bash
git clone https://github.com/pschwede/qlplugins.git ~/.quodlibet/plugins/
```

or copy the events folder to `~/.quodlibet/plugins/`:

```bash
git clone https://github.com/pschwede/qlplugins.git; t=~.quodlibet/plugins/events; mkdir -p $t; cp qlplugins/events/*.py $t
```
