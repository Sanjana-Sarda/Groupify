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
from groupify.app.spotify_utils import get_user_top_tracks, fetch_audio_features, get_playlists_of_user, fetch_playlist_tracks 
from groupify.app.spotify_utils import create_playlist_new, enrich_playlist, fetch_playlist_tracks
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
df_favorite = get_user_top_tracks(sp)
df_fav = fetch_audio_features (sp, df_favorite)

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
df_playlists = get_playlists_of_user(sp, username)
df_playlists
```

```python

```

```python

```

```python

```

```python
from groupify.app.spotify_utils import mean_audio_features_playlist
# Merge them together
import numpy
dataframes = []
# Loop through the filenames to populate dataframes with different dataframes 
for  playlist in df_playlists['id']:
    try:
        mean_df = mean_audio_features_playlist(sp, playlist)

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
    playlist_name = df_playlists[df_playlists['id']==X.columns[indices[f]]]['name'].values[0]
    
    print("%d. %s %s %f " % (f + 1, 
            X.columns[indices[f]],
            playlist_name,
            importances[indices[f]]))
```

```python
for i, playlist in enumerate(df_playlists['id']):
    try:
        string_command = "df_{} = fetch_audio_features(sp, playlist)".format(playlist)
        print("Create {}".format(string_command))
        exec(string_command)
    except:
        print("playlist with id {} is not valid, skiping ".format(playlist))
        pass


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
df = df.set_index(['track_id'])


```

```python
df
```

```python
Y= Y.squeeze('columns')
Y = Y.sort_index( axis=0, level=None, ascending=True, inplace=False, kind='quicksort')
Y
```

```python
std_dev = pd.DataFrame(df_fav.std(), columns= ['fav_playlist'])
std_dev
```

```python
# Subtract mean of the favorite plalyist from the top 3 playlist 
df1= df.subtract(Y, axis='columns') 
df1
```

```python
## this operation needs to be performed with standard deviation, not median. 
df1= df1.divide(Y, axis='columns') ## not sure if this has to be fixed!
# df1
```

```python
# df1 = df1.drop(['instrumentalness'], axis=1)
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

```

```python
new_playlist_id = create_playlist_new(sp,  'JS Blend2', 'Test playlist created using python!')
```

```python
get_playlists_of_user(sp,username)
```

```python
list_track = df2.index
```

```python
enrich_playlist(sp, username, new_playlist_id, list_track) #playlist id
```

```python
get_playlists_of_user(sp,username)
```

```python
fetch_playlist_tracks(sp, new_playlist_id)
```

```python

```
