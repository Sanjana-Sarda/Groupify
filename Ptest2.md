---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.13.7
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

```python
!pip install Spotipy
```

```python
import os
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
%config InlineBackend.figure_format ='retina'
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import oauth2
import random
from functools import reduce

import json, os
import traceback
import matplotlib.pyplot as plt
%matplotlib inline
```

```python
# constants
redirect_uri = 'https://example.com'
```

```python
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

import groupify.app.psecrets as psecrets

try: 
    cid = psecrets.client_id
    secret = psecrets.secret
    userdata = json.load(open('groupify/app/json/userdata.json', 'r'))
    username = list(userdata.keys())[0]
    scope = 'user-top-read user-read-recently-played user-follow-read playlist-modify-public user-library-read playlist-read-collaborative'
    token = util.prompt_for_user_token(username, scope, client_id=cid, client_secret=secret, redirect_uri=redirect_uri)

    if token:
        sp = spotipy.Spotify(auth=token)
    else:
        print("Can't get token for", username)
except: 
    print(traceback.format_exc(5))

```

```python
results_top_tracks = sp.current_user_top_tracks(limit=25, offset=0,time_range='medium_term')
results_top_tracks
```

```python
results_recently_played = sp.current_user_recently_played(limit=25)
# results_try = sp.current_user_saved_tracks(limit = 50, offset= 0)
results_recently_played
```

```python
results_top_tracks = sp.current_user_top_tracks(limit=25, offset=0,time_range='medium_term')
results_recently_played = sp.current_user_recently_played(limit=25)
all_results = {}
all_results['items'] = results_top_tracks['items']
print(type(all_results['items']))
for ind, item in enumerate(results_recently_played['items']): 
    all_results['items'] = all_results['items'] + [results_recently_played['items'][ind]['track']]

# all_results['items'] += results_try['items']
results = all_results
```

```python
# Convert it to Dataframe
track_name = []
track_id = []
artist = []
artist_id = []
album = []
duration = []
popularity = []
for i, items in enumerate(results['items']):
        track_name.append(items['name'])
        track_id.append(items['id'])
        artist.append(items["artists"][0]["name"])
        artist_id.append(items["artists"][0]["id"])
        duration.append(items["duration_ms"])
        album.append(items["album"]["name"])
        popularity.append(items["popularity"])

# Create the final df   
df_favorite = pd.DataFrame({ "track_name": track_name, 
                             "album": album, 
                             "track_id": track_id,
                             "artist": artist, 
                             "artist_id": artist_id,
                             "duration": duration, 
                             "popularity": popularity})

df_favorite
```

```python
def fetch_audio_features(sp, df):
    playlist = df[['track_id','track_name', 'artist_id']] 
    index = 0
    audio_features = []
    genres = []
    
    # Make the API request
    while index < playlist.shape[0]:
        audio_features += sp.audio_features(playlist.iloc[index:index + 50, 0])
        index += 50
        
    index = 0
    while index < playlist.shape[0]:
        genres += [sp.artist('spotify:artist:'+ playlist.iloc[index, 2])['genres']]
        index += 1
    
    # Create an empty list to feed in different charactieritcs of the tracks
    features_list = []
    #Create keys-values of empty lists inside nested dictionary for album
    for features in audio_features:
        features_list.append([features['danceability'],
                              features['acousticness'],
                              features['energy'], 
                              features['tempo'],
                              features['instrumentalness'], 
                              features['loudness'],
                              features['liveness'],
                              features['duration_ms'],
                              features['key'],
                              features['valence'],
                              features['speechiness'],
                              features['mode']
                             ])
    
    df_audio_features = pd.DataFrame(features_list, columns=['danceability', 'acousticness', 'energy','tempo', 
                                                             'instrumentalness', 'loudness', 'liveness','duration_ms', 'key',
                                                             'valence', 'speechiness', 'mode',])
    df_audio_features['genres'] = genres
    
    # Create the final df, using the 'track_id' as index for future reference
    df_playlist_audio_features = pd.concat([playlist, df_audio_features], axis=1)
    df_playlist_audio_features.set_index('track_name', inplace=True, drop=True)
    return df_playlist_audio_features
```

```python
df_fav = fetch_audio_features (sp, df_favorite)
df_fav
```

```python
df_fav.info()
```

```python
df_fav.hist(figsize=(35,25)) 
plt.tight_layout()
plt.show()
```

```python
def featured_playlists(sp, username):
    id = []
    name = []
    num_tracks = []
 # For looping through the API request  
    playlists = sp.user_playlists(username)#Replace with user id
    for i, items in enumerate(playlists['items']):
        id.append(items['id'])
        name.append(items['name'])
        num_tracks.append(items['tracks']['total'])

# Create the final df   
    df_playlists = pd.DataFrame({"id":id, "name": name, "#tracks": num_tracks})
    return df_playlists
```

```python
df_playlists = featured_playlists(sp, creds['username'])
df_playlists
```

```python
def fetch_playlist_tracks(sp, playlistsid): 
    offset = 0
    tracks = []
    # Make the API request
    while True:
            content = sp.playlist_tracks( playlistsid, fields=None, limit=100, offset=offset, market=None)
            tracks += content['items']
        
            if content['next'] is not None:
                offset += 100
            else:
                break
    
    track_id = []
    track_name = []
    
    for track in tracks:
        track_id.append(track['track']['id'])
        track_name.append(track['track']['name'])
    
# Create the final df
    df_playlists_tracks = pd.DataFrame({"track_id":track_id, "track_name": track_name})
    return df_playlists_tracks
```

```python
def fetch_audio_features(sp, playlist_id):
    playlist = fetch_playlist_tracks(sp, playlist_id)
    index = 0
    audio_features = []
    
    # Make the API request
    while index < playlist.shape[0]:
        audio_features += sp.audio_features(playlist.iloc[index:index + 50, 0])
        index += 50
    
    # Create an empty list to feed in different charactieritcs of the tracks
    features_list = []
    #Create keys-values of empty lists inside nested dictionary for album
    for features in audio_features:
        features_list.append([features['danceability'],
                              features['acousticness'],
                              features['energy'], 
                              features['tempo'],
                              features['instrumentalness'], 
                              features['loudness'],
                              features['liveness'],
                              features['duration_ms'],
                              features['key'],
                              features['valence'],
                              features['speechiness']
                             ])
    
    df_audio_features = pd.DataFrame(features_list, columns=['danceability', 'acousticness', 'energy','tempo', 
                                                             'instrumentalness', 'loudness', 'liveness', 'duration_ms', 'key',
                                                             'valence', 'speechiness'])
    
    # Create the final df, using the 'track_id' as index for future reference
    df_playlist_audio_features = pd.concat([playlist, df_audio_features], axis=1)
    df_playlist_audio_features.set_index('track_name', inplace=True, drop=True)
    return df_playlist_audio_features
```

```python
# Build the dtaframe froms the playlists
for i, playlist in enumerate(df_playlists['id']):
    try:
        string_command = "df_{} = fetch_audio_features(sp, playlist)".format(playlist)
        print("Create {}".format(string_command))
        exec(string_command)
    except:
        print("playlist with id {} is not valid, skiping ".format(playlist))
        pass
```

```python
def fetch_audio_features_mean(sp, playlist_id):
    Playlist = fetch_audio_features(sp, playlist_id)#df_playlist_audio_features(sp, playlist_id)
    return pd.DataFrame(Playlist.mean(), columns= [playlist_id])
```

```python
# Merge them together
import numpy
dataframes = []
# Loop through the filenames to populate dataframes with different dataframes 
for  playlist in df_playlists['id']:
    try:
        mean_df = fetch_audio_features_mean(sp, playlist)

        if any(numpy.isnan(mean_df.values)): 
            
            print ("Skip "+playlist)
            continue
        dataframes.append(mean_df)
    except:
        print ("Skip "+playlist)
```

```python
dataframes
```

```python
X = reduce(lambda left,right: pd.merge(left,right, left_index=True, right_index=True), dataframes)
X
```

```python
Y = pd.DataFrame(df_fav.median(), columns= ['fav_playlist'])
Y= Y.drop('mode')
Y
```

```python
# Analyze feature importances
from sklearn.ensemble._forest import RandomForestRegressor
# Can combine step above with this
forest = RandomForestRegressor(n_estimators=10)#random_state=42, max_depth=2, max_features=9) 
forest.fit(X,Y.values.ravel())
importances = forest.feature_importances_
indices = np.argsort(importances)[::-1]
# Print the feature rankings
print("Playlist ranking:")
  
for f in range(len(importances)):
    print("%d. %s %f " % (f + 1, 
            X.columns[indices[f]], 
            importances[indices[f]]))
```

```python
frames = []
for i, playlist in enumerate(df_playlists['id']):
    try:
        string_command = "frames.append(df_{})".format(playlist)
        print("Create {}".format(string_command))
        exec(string_command)
    except:
        print("playlist with id {} is not valid, skiping ".format(playlist))
        pass
print (frames)
df =pd.concat(frames)
df.drop_duplicates()
df
```

```python
df = df.set_index(['track_id'])
df
```

```python
# CO
Y= Y.squeeze('columns')
```

```python
Y = Y.sort_index( axis=0, level=None, ascending=True, inplace=False, kind='quicksort')
Y
```

```python
# Subtract mean of the favorite plalyist from the top 3 playlist 
df1= df.subtract(Y, axis='columns') 
df1
```

```python
df1= df1.divide(Y, axis='columns') 
df1
```

```python
df1 = df1.drop(['instrumentalness'], axis=1)
```

```python
# Add all the score 
df1['variation'] = df1.sum(axis=1)
# take the absoulte of the variatio
df1['variation'] = df1['variation'].abs()
df1 = df1.drop_duplicates()
df1
```

```python
# Now we have the variation, we will take the songs with the least variation 
df2 = df1.nsmallest(50,'variation', keep='first')
df2
```

```python
def create_playlist(sp, username, playlist_name, playlist_description):
    playlists = sp.user_playlist_create(username, playlist_name, description = playlist_description)
```

```python

```

```python
create_playlist(sp, username, 'JS Blend2', 'Test playlist created using python!')
```

```python
def fetch_playlists(sp, username):
    """
    Returns the user's playlists.
    """
        
    id = []
    name = []
    num_tracks = []
    
    # Make the API request
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:
        id.append(playlist['id'])
        name.append(playlist['name'])
        num_tracks.append(playlist['tracks']['total'])

    # Create the final df   
    df_playlists = pd.DataFrame({"id":id, "name": name, "#tracks": num_tracks})
    return df_playlists
```

```python
fetch_playlists(sp,username)
```

```python
def enrich_playlist(sp, username, playlist_id, playlist_tracks):
    index = 0
    results = []
    
    while index < len(playlist_tracks):
        results += sp.user_playlist_add_tracks(username, playlist_id, tracks = playlist_tracks[index:index + 50])
        index += 50
```

```python
list_track = df2.index
```

```python
enrich_playlist(sp, username, '', list_track) #playlist id
```

```python
fetch_playlists(sp,username)
```

```python

```
