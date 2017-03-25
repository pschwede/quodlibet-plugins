# QuodLibet Plugin Collection

## Installation

1. Clone this repository into the plugins folder of your quodlibet home directory.

```bash
git clone https://github.com/pschwede/quodlibet-plugins.git ~/.quodlibet/plugins/
```

2. Restart quodlibet
3. Now you can see and enable the new plugins in File->Plugins.

## Features

### GUI

**Autorefresh** reloads the Browser view (in some search queries, by that, it
makes sure no song is played over and over again or that the playlist doesn't
stop)

### Playback

**AutoSeek** Plays only a few seconds of a track. Skipping rate and relative
seek position are configurable.

**Detector BPM** Apply BPM analysis to songs and write it to the tag 'bpm'.
Currently, only bpm-tools (from Ubuntu repositories) is supported.

### Podcasting

**GPodderSync** Fetch podcast urls from your account on
[gPodder](http://gpodder.net) and add them to QL's Audio Feeds.

**AutoCast** Create a radio rotation between music and talk.  It enqueues
podcast entries after play music has been played.  The seconds of music between
the podcasts can be configured.

### Covers

**gPodder cover source** Download podcast logos from the gPodder.net API

**Jamendo cover source** Download covers from the Jamendo.com API


## Guarantee

These plugins have only been tested on linux.
