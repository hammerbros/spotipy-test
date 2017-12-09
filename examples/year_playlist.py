#!/usr/bin/env python3

"""Script for retrieving songs from a user's 'Your Top Songs 2017'
playlist.

Note: Requests to Spotify API do not currently include relevant fields arg,
which should eventually be added.
"""

from collections import namedtuple
import sys
import argparse
import spotipy
from spotipy import oauth2

# Client ID and Client Secret for zachthehammer's spotipy-test API key
_CLIENT_ID = '5c243ed8edc9475a90bda2cc4a9a828c'
_CLIENT_SECRET = 'b414caddc10143eea70db6edc1f4fb47'

# Your Top Songs 2017 is actually owned by spotify user.
_SPOTIFY_USER_ID = 'spotify'
_YEAR_PLAYLIST_NAME = 'Your Top Songs 2017'

# Format strings
_SCRIPT_DESCRIPTION_FMT = 'Get the list of tracks from a user\'s "{}" playlist.'
_NO_PLAYLISTS_FOUND_FMT = 'No playlists found for user {}.'
_PLAYLIST_NOT_FOUND_FMT = 'User "{user}"" does not follow their "{playlist}" playlist.'
_USER_PLAYLIST_FMT = '{user}\'s "{playlist}" playlist!'
_TRACK_FMT = '{artist} // {name} [{album}]'

SpotifyTrack = namedtuple('SpotifyTrack', ['name', 'artist', 'album'])

def _parse_args():
    """Helper function to create the command-line argument parser for
    year_playlist.  Return the parsed arguments as a Namespace object if
    successful. Exits the program if unsuccessful or if the help
    message is printed.
    """
    description = (_SCRIPT_DESCRIPTION_FMT.format(_YEAR_PLAYLIST_NAME))
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        'username',
        help='User\'s username.')

    return parser.parse_args()

def _get_user_playlists(spotify_client, username):
    """Get the list of playlists of a user as raw dictionaries. """
    playlists = spotify_client.user_playlists(user=username)
    return playlists and playlists['items']

def _get_playlist_by_name(playlists, name):
    """Get a playlist by its name from a list of raw playlist dictionaries."""
    found_playlist = None
    for playlist in playlists:
        if playlist['name'] == name:
            found_playlist = playlist
            break
    return found_playlist

def _extract_track_data(raw_track):
    """Extract relevant track data from a track's raw dictionary representation
    and return it is a SpotifyTrack object."""
    return SpotifyTrack(
        name=raw_track['track']['name'],
        artist=raw_track['track']['artists'][0]['name'],
        album=raw_track['track']['album']['name'])

def _fetch_tracks_of_playlist(spotify_client, playlist_id, owner_id):
    """Get the list of tracks on a spotify playlist.

    Args:
        spotify_client: Authenticated spotify client.
        playlist_id: String ID of playlist.
        owner_id: String ID of playlist owner.

    Returns:
        List of SpotifyTracks in a playlist.

    """
    raw_tracks = spotify_client.user_playlist_tracks(owner_id, playlist_id=playlist_id)['items']
    return [_extract_track_data(raw_track) for raw_track in raw_tracks]

def _extract_playlist_id(playlist):
    """Get the id of a playlist from its dictionary representation."""
    return playlist['id']

def _fetch_authenticated_client():
    """Get an authenticated client for non-user-private data requests."""
    credentials = oauth2.SpotifyClientCredentials(
        client_id=_CLIENT_ID,
        client_secret=_CLIENT_SECRET
    )
    token = credentials.get_access_token()
    return spotipy.Spotify(auth=token)

def _billboardify(string, wrapper='#', wrap_sides=False):
    """Wrap a string like a billboard.

    Input:
    Hey there!

    Output:
    ##############
    # Hey there! #
    ##############
    """
    center_line = string if not wrap_sides else '{w} {s} {w}'.format(w=wrapper, s=string)
    wrapper_line = wrapper * len(center_line)
    return wrapper_line + '\n' + center_line + '\n' + wrapper_line


def main():
    """Main"""
    args = _parse_args()
    spotify_client = _fetch_authenticated_client()

    # Get user's playlists. If not found, print error message
    playlists = _get_user_playlists(spotify_client, args.username)
    if not playlists:
        print(_NO_PLAYLISTS_FOUND_FMT.format(args.username))
        sys.exit(1)

    # Get user's 'year' playlist. If not found, print error message
    year_playlist = _get_playlist_by_name(playlists, _YEAR_PLAYLIST_NAME)
    if not year_playlist:
        print(
            _PLAYLIST_NOT_FOUND_FMT.format(
                user=args.username,
                playlist=_YEAR_PLAYLIST_NAME))
        sys.exit(1)

    # Get tracks from user's 'year' playlist and print to stdout
    year_tracks = _fetch_tracks_of_playlist(
        spotify_client,
        _extract_playlist_id(year_playlist),
        _SPOTIFY_USER_ID)

    # Print results
    print(_billboardify(_USER_PLAYLIST_FMT.format(user=args.username, playlist=_YEAR_PLAYLIST_NAME),
                        wrap_sides=True))
    for track in year_tracks:
        print(_TRACK_FMT.format(
            artist=track.artist,
            name=track.name,
            album=track.album))

if __name__ == '__main__':
    main()
