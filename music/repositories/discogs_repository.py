from music.models import Metadata
from music.services.discogs_api import get_track_data

def fetch_release_info_for_track(track):
    artist_map = track.artisttrackmap_set.first()
    if not artist_map:
        return None, "No artist info available for this track."

    artist_name = artist_map.artist.name
    query = f"{track.title} {artist_name}"
    results = get_track_data(query)

    if results:
        result = results[0]
        discogs_url = f"https://www.discogs.com{result.get('uri', '')}"
        release, _ = Metadata.objects.update_or_create(
            track=track,
            defaults={
                "title": result.get("title", ""),
                "year": result.get("year"),
                "label": ", ".join(result.get("label", [])),
                "discogs_url": discogs_url
            }
        )
        return release, None
    else:
        return None, "No results found on Discogs."
