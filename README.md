# pymonomusic

Python bindings for the Monochrome Tracks API.

## Usage

### Get track stream URL
```
import pymonomusic
client = pymonomusic.MonochromeClient()
stream = client.streamTrack(166114521845624832)
```

### Search Tracks
```
import pymonomusic
client = pymonomusic.MonochromeClient()
searchResults = client.search("Cavetown")
tracks = searchResults.tracks
```