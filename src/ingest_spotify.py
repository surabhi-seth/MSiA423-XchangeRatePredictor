import logging
import os
import json

import boto3
import numpy as np
import pandas as pd
import spotipy
import spotipy.util as util

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


def authenticate_spotify(username, client_id=None, client_secret=None, redirect_uri='https://example.com/callback'):
    client_id = os.environ.get("SPOTIFY_CLIENT_ID") if client_id is None else client_id
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET") if client_secret is None else client_secret
    scope = 'user-read-recently-played'
    token = util.prompt_for_user_token(username, scope,
                                       client_id=client_id,
                                       client_secret=client_secret,
                                       redirect_uri=redirect_uri)

    sp = spotipy.Spotify(auth=token)

    return sp


def get_all_playlists(username, playlists_per_call=50, put_in_s3=None,
                      s3=None, sp=None, authenticate_spotify_kwargs=None):

    if sp is None:
        if type(authenticate_spotify_kwargs) != dict:
            raise ValueError("Either sp (authorized spotify object) needs to be provided or arguments necessary "
                             "to create it must be given in 'authenticate_spotify_kwargs' as a dictionary")
        else:
            sp = authenticate_spotify(**authenticate_spotify_kwargs)

    # Get first instance of playlists (offset=0) to know total number of iterations necessary
    playlists = sp.user_playlists(username, offset=0)

    # Initialize objects for compiling data
    raw_playlists = dict(playlists=[playlists])
    playlist_items = playlists["items"]

    # Retrieve playlists until the total number of playlists has been reached
    for offset in np.arange(playlists_per_call, playlists["total"],
                            playlists_per_call):
        playlists = sp.user_playlists(username, offset=offset)
        raw_playlists["playlists"].append(playlists)
        playlist_items += playlists["items"]

    logger.info("%i playlists retrieved in %i API calls", len(playlist_items),
                len(raw_playlists["playlists"]))

    # Put raw JSON in S3 if provided
    if put_in_s3 is not None:
        if s3 is None:
            s3 = boto3.resource('s3')
        s3.Bucket('msia423').put_object(
            Key=put_in_s3, Body=json.dumps(raw_playlists))
        logger.info("Raw playlist JSON put into %s", put_in_s3)

    return playlist_items


def get_playlist_songs(playlist_items,
                       max_num_tracks=100,
                       put_in_s3=None,
                       s3=None,
                       song_columns=None, sp=None, authenticate_spotify_kwargs=None):

    if sp is None:
        if type(authenticate_spotify_kwargs) != dict:
            raise ValueError("Either sp (authorized spotify object) needs to be provided or arguments necessary "
                             "to create it must be given in 'authenticate_spotify_kwargs' as a dictionary")
        else:
            sp = authenticate_spotify(**authenticate_spotify_kwargs)

    if song_columns is None:
        song_columns = [
            'name', 'artist', 'spotify_id', 'isrc', 'artist_id', 'album',
            'playlist', 'track_number', 'duration_ms', 'explicit', 'added_at'
        ]
    data = []
    raw_song_data = dict(tracks=[])
    for playlist in playlist_items:
        num_tracks = max_num_tracks
        offset = 0
        while num_tracks > 0:
            results = sp.user_playlist_tracks(
                playlist['owner']['id'],
                playlist['id'],
                fields="items,next",
                offset=offset)
            raw_song_data["tracks"].append(results)
            num_tracks = len(results['items'])
            offset += max_num_tracks
            for track in results['items']:
                added_at = track["added_at"]
                track = track['track']
                artists = []
                artist_id = []
                for artist in track['artists']:
                    artists.append(artist['name'])
                    artist_id.append(str(artist['id']))

                artists = ', '.join(sorted(artists))
                artist_id = ', '.join(sorted(artist_id))
                album = track['album']['name']
                name = track['name']
                duration_ms = track['duration_ms']
                explicit = track['explicit']
                track_number = track['track_number']
                spotify_id = track['id']

                if 'isrc' in track['external_ids'].keys():
                    isrc = track['external_ids']['isrc']
                else:
                    isrc = None

                data.append([
                    name, artists, spotify_id, isrc, artist_id, album,
                    playlist['name'], track_number, duration_ms, explicit,
                    added_at
                ])
    songs = pd.DataFrame(data, columns=song_columns)

    logger.info(
        "%i songs with %i unique song ids retrieved from %i playlists with %i fields of information",
        len(songs), songs.spotify_id.nunique(), len(playlist_items),
        len(songs.columns))

    if put_in_s3 is not None:
        if s3 is None:
            s3 = boto3.resource('s3')
        s3.Bucket('msia423').put_object(
            Key=put_in_s3, Body=json.dumps(raw_song_data))
        logger.info("Playlist song JSON put into %s", put_in_s3)

    return songs


def drop_duplicates(df, column, sort_by=None, ascending=True):
    n_original = len(df)
    if sort_by is not None:
        df = df.sort_values(by=sort_by, ascending=ascending)

    columns = [column] if type(column) != list else column
    for col in columns:
        df = df.groupby(col).head(1)

    logger.warning("%i duplicates dropped from %i rows of data, resulting in %i rows", n_original - len(df), n_original,
                   len(df))
    return df


def drop_values(df, column, value):
    columns = [column] if type(column) != list else column
    values = [value] if type(value) != list else value
    n_original = len(df)
    n = len(df)
    for col, val in zip(columns, values):
        df = df[df[col] != val]
        logger.info("%i rows dropped where df[%s] = %s", n-len(df), col, str(val))
        n = len(df)
    logger.warning("A total of %i rows dropped for having specific values of %s", n_original-len(df), ",".join(columns))
    return df

