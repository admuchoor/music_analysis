import sys
import os
import subprocess
import json
import spotipy
import spotipy.util as util
import pandas as pd
import time
from spotipy.oauth2 import SpotifyClientCredentials
import config

CLIENT_ID = config.spotify_login['client_id']
CLIENT_SECRET = config.spotify_login['client_secret']
USERNAME = config.spotify_login['username']
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)


def get_track_features(track_id,sp):
    if track_id is None:
        return None
    else:
        features = sp.audio_features([track_id])
    return features

def get_features(tracks,sp):
    
    tracks_with_features=[]

    for track in tracks:
        features = get_track_features(track['id'],sp)
        print (track['name'])
        if not features:
            print("passing track %s" % track['name'])
            pass
        else:
            f = features[0]
            tracks_with_features.append(dict(
                                            name=track['name'],
                                            artist=track['artist'],
                                            id=track['id'],
                                            danceability=f['danceability'],
                                            energy=f['energy'],
                                            loudness=f['loudness'],
                                            speechiness=f['speechiness'],
                                            acousticness=f['acousticness'],
                                            tempo=f['tempo'],
                                            liveness=f['liveness'],
                                            valence=f['valence']
                                            ))

        time.sleep(0.1)

    return tracks_with_features

def get_tracks_from_playlists(username, sp):
    playlists = sp.user_playlists(username)
    trackList = []
    for playlist in playlists['items']:
        if playlist['owner']['id'] == username:
            print (playlist['name'],' no. of tracks: ',playlist['tracks']['total'])
            results = sp.user_playlist(username, playlist['id'],fields="tracks,next")
            tracks = results['tracks']
            for item in tracks['items']:
                track = item['track']
                trackList.append(dict(name=track['name'], id=track['id'], artist=track['artists'][0]['name']))

    return trackList

def write_to_csv(track_features):
    df = pd.DataFrame(track_features)
    df.drop_duplicates(subset=['name','artist'])
    print ('Total tracks in data set', len(df))
    df.to_csv('songs.csv',index=False)


if __name__ == '__main__':
    print ('Starting...')
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=10)
    print ("Getting user tracks from playlists")
    tracks = get_tracks_from_playlists(USERNAME, sp)
    print ("Getting track audio features")
    tracks_with_features = get_features(tracks,sp)
    print ("Storing into csv")
    write_to_csv(tracks_with_features)

