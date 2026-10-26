import requests
from urllib.parse import quote

class Track:
    def __init__(self, trackDict: dict):
        self.id = trackDict.get("id") if trackDict.get("id") is not None else trackDict.get("trackId")
        self.title = trackDict.get("title")
        self.releaseId = trackDict.get("releaseId")
        self.artwork = trackDict.get("artwork")
        self.explicit = trackDict.get("explicit")
        self.playable = trackDict.get("playable")
        self.duration = trackDict.get("duration") / 1000 if trackDict.get("duration") is not None else None
        self.isrc = trackDict.get("isrc")
        self.recordingId = trackDict.get("recordingId")

        # from search only
        self.artistIds = trackDict.get("artistIds")
        self.artistNames = trackDict.get("artistNames")
        self.searchPriority = trackDict.get("searchPriority")

        # from releases only
        self.artists = [Artist(artist) for artist in trackDict.get("artists")] if trackDict.get("artists") is not None else None
        self.discNumber = trackDict.get("discNumber")
        self.trackNumber = trackDict.get("trackNumber")

    def __repr__(self):
        return f"Track(id={int(self.id)!r}, title={self.title!r})"

class Artist:
    def __init__(self, artistDict: dict):
        self.id = artistDict.get("id") if artistDict.get("id") is not None else artistDict.get("artistId")
        self.name = artistDict.get("name")
        self.username = artistDict.get("username")
        self.displayName = artistDict.get("displayName")
        self.sortName = artistDict.get("sortName")
        self.avatar = artistDict.get("avatar")
        self.bio = artistDict.get("bio")

        # from search only
        self.searchPriority = artistDict.get("searchPriority")

        # from page only
        self.alias = artistDict.get("alias")
        self.createdAt = artistDict.get("createdAt")
        self.updatedAt = artistDict.get("updatedAt")
        self.alternateNames = artistDict.get("alternateNames")
        self.isVerified = artistDict.get("isVerified")
        self.status = artistDict.get("status")
        self.entropyOrchestrationResolution = artistDict.get("entropyOrchestrationResolution")
        self.biography = artistDict.get("biography")
        self.dateOfBirth = artistDict.get("dateOfBirth")
        self.dateOfDeath = artistDict.get("dateOfDeath")
        self.country = artistDict.get("country")
        self.city = artistDict.get("city")
        self.banner = artistDict.get("banner")
        self.externalLink = artistDict.get("externalLink")
        self.socialLinks = artistDict.get("socialLinks")
        self.genres = artistDict.get("genres")
        self.tags = artistDict.get("tags")

        self.latestRelease = Release(artistDict.get("latestRelease")) if artistDict.get("latestRelease") is not None else None
        self.topTracks = [Track(track) for track in artistDict.get("topTracks")] if artistDict.get("topTracks") is not None else None
        self.releases = [Release(release) for release in artistDict.get("releases")] if artistDict.get("releases") is not None else None
        self.albums = [Release(release) for release in artistDict.get("albums")] if artistDict.get("albums") is not None else None
        self.singles = [Release(release) for release in artistDict.get("singles")] if artistDict.get("singles") is not None else None

    def __repr__(self):
        return f"Artist(id={int(self.id)!r}, name={self.name!r}, username={self.username!r})"

class Release:
    def __init__(self, releaseDict: dict):
        self.id = releaseDict.get("id") if releaseDict.get("id") is not None else releaseDict.get("releaseId")
        self.title = releaseDict.get("title")
        self.label = releaseDict.get("label")
        self.artwork = releaseDict.get("artwork")
        self.explicit = releaseDict.get("explicit")

        # from search only
        self.artistIds = releaseDict.get("artistIds")
        self.artistNames = releaseDict.get("artistNames")
        self.releaseDate = releaseDict.get("releaseDate")
        self.releaseType = releaseDict.get("releaseType")
        self.searchPriority = releaseDict.get("searchPriority")

        # from releases only
        self.artists = [Artist(artist) for artist in releaseDict.get("artists")] if releaseDict.get("artists") is not None else None
        self.upc = releaseDict.get("upc")
        self.discCount = releaseDict.get("discCount")
        self.trackCount = releaseDict.get("trackCount")
        self.language = releaseDict.get("language")
        self.script = releaseDict.get("script")
        self.copyrights = releaseDict.get("copyrights")
        self.createdAt = releaseDict.get("createdAt")
        self.updatedAt = releaseDict.get("updatedAt")
        self.tracks = [Track(track) for track in releaseDict.get("tracks")] if releaseDict.get("tracks") is not None else None

    def __repr__(self):
        return f"Release(id={int(self.id)!r}, title={self.title!r})"

class SearchResults:
    def __init__(self, results: dict):
        self.tracks: list = [Track(track) for track in results["tracks"]]
        self.artists: list = [Artist(artist) for artist in results["artists"]]
        self.releases: list = [Release(release) for release in results["releases"]]

class Stream:
    def __init__(self, trackID: int, url: str, bitDepth: int | None, sampleRate: int | None):
        self.id = trackID; self.url = url; self.bitDepth = bitDepth; self.sampleRate = sampleRate
    def __repr__(self):
        return f"Stream(id={int(self.id)!r}, bitDepth={self.bitDepth!r}, sampleRate={self.sampleRate!r})"

class MonochromeClient:
    class InvalidFLACHeaderException(Exception):
        """Exception raised when the FLAC's header doesn't match 'fLaC'."""

        def __init__(self, url):
            super().__init__(f"FLAC from Monochrome ('{url}')'s header doesn't match 'fLaC'.")

    def streamTrack(self, trackID: int, getFLACInfo: bool = False):
        """Gets streaming info from a trackID."""
        url = f"https://tracks.monochrome.st/track/{trackID}"
        if getFLACInfo:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                chunk: bytes = r.raw.read(64)
            if chunk[:4].startswith(b"fLaC"):
                flacSTREAMINFO = chunk[4:38]
                sampleRate = (flacSTREAMINFO[14] << 12) | (flacSTREAMINFO[15] << 4) | (flacSTREAMINFO[16] >> 4)
                bitDepth = (((flacSTREAMINFO[16] & 0x01) << 4) | (flacSTREAMINFO[17] >> 4)) + 1

                return Stream(trackID, url, bitDepth, sampleRate)
            else: raise MonochromeClient.InvalidFLACHeaderException(url)
        else:
            return Stream(trackID, url, None, None)

    def search(self, q: str):
        """Searches Monochrome for a query. Returns tracks, artists and releases."""
        r = requests.get(f"https://tracks.monochrome.st/search?q={quote(q)}")
        r.raise_for_status()
        return SearchResults(r.json())

    def getRelease(self, releaseID: int):
        """Gets detailed information on a release."""
        r = requests.get(f"https://tracks.monochrome.st/releases/{releaseID}")
        r.raise_for_status()
        return Release(r.json())

    def getArtist(self, artistID: int):
        """Gets detailed information on an artist."""
        r = requests.get(f"https://tracks.monochrome.st/artists/{artistID}")
        r.raise_for_status()
        return Artist(r.json())

    def getDonationGoalPercentage(self):
        r = requests.get("https://tracks.monochrome.st/goal")
        r.raise_for_status()
        return int(r.json()["percentage"].replace("%", ""))
