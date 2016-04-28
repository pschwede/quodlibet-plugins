# QuodLibet Plugin Collection

(only tested on linux)

## Installation

1. Clone this repository into the plugins folder of your quodlibet home directory.

```bash
git clone https://github.com/pschwede/quodlibet-plugins.git ~/.quodlibet/plugins/
```

2. Restart quodlibet
3. Now you can see the new plugins in Music-->Plugins.


## Features

### General

#### Autorefresh
* Reloads the Browser view (in some search queries, by that,
  it makes sure no song is played over and over again or that the playlist
  doesn't stop)

#### AutoSeek
* Plays only a few seconds of a track. Skipping rate and relative
  seek position are configurable.

#### Detector BPM
* Apply BPM analysis to songs and write it to the tag 'bpm'.
	Currently, only bpm-tools (from Ubuntu repositories) is supported.


### Podcasting

#### GPodderSync
* Fetch podcast urls from your account on [gPodder](http://gpodder.net) and add
	them to QL's Audio Feeds.

#### AutoCast
* Create a radio rotation between music and talk.
* It repeatingly enqueues podcast entries after playing music.
* The seconds of music between the podcasts are configurable.

#### gPodder cover source
* Download podcast logos from the gPodder.net API


### Jamendo support

#### Jamendo cover source
* Download covers from the Jamendo.com API
