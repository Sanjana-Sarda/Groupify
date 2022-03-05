import pandas as pd
import numpy as np


def get_user_top_tracks(sp):
    '''
    Given user auth, get a combination of users top tracks and recently played music 
    '''

    results_top_tracks = sp.current_user_top_tracks(limit=25, offset=0,time_range='medium_term')
    results_recently_played = sp.current_user_recently_played(limit=25)
    all_results = {}
    all_results['items'] = results_top_tracks['items']
    print(type(all_results['items']))
    for ind, item in enumerate(results_recently_played['items']): 
        all_results['items'] = all_results['items'] + [results_recently_played['items'][ind]['track']]

    # all_results['items'] += results_try['items']
    results = all_results

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
        
    df_favorite = pd.DataFrame({ "track_name": track_name, 
    "album": album,
    "track_id": track_id,
    "artist": artist,
    "artist_id": artist_id,
    "duration": duration,
    "popularity": popularity})
    return df_favorite


def get_playlists_of_user(sp, username):
    '''
    Gets a list of playlists from the user
    '''
    id = []
    name = []
    num_tracks = []
 # For looping through the API request  
    playlists = sp.user_playlists(username)
    for i, items in enumerate(playlists['items']):
        id.append(items['id'])
        name.append(items['name'])
        num_tracks.append(items['tracks']['total'])

# Create the final df   
    df_playlists = pd.DataFrame({"id":id, "name": name, "#tracks": num_tracks})
    return df_playlists



def fetch_playlist_tracks(sp, playlistsid): 
    '''
    Fetches playlist tracks given a playlist id 
    '''
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



def fetch_audio_features(sp, inp):

    if isinstance(inp, type('')): 
        playlist = fetch_playlist_tracks(sp, inp)
    elif isinstance(inp, pd.DataFrame): 
        df = inp
        playlist = df[['track_id','track_name', 'artist_id']] 

    index = 0
    audio_features = []
    genres = []
    
    # Make the API request
    while index < playlist.shape[0]:
        audio_features += sp.audio_features(playlist.iloc[index:index + 50, 0])
        index += 50
        
    index = 0
    #while index < playlist.shape[0]:
     #   genres += [sp.artist('spotify:artist:'+ playlist.iloc[index, 2])['genres']]
      #  index += 1
    
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
        features['mode']])
    

    
    df_audio_features = pd.DataFrame(features_list, columns=['danceability', 'acousticness', 'energy','tempo',
    'instrumentalness', 'loudness', 'liveness','duration_ms', 'key',
    'valence', 'speechiness', 'mode',])
    
    #df_audio_features['genres'] = genres
    df_audio_features['track_id'] = playlist['track_id'].values
    # Create the final df, using the 'track_id' as index for future reference
    #df_playlist_audio_features = pd.concat([playlist, df_audio_features], axis=0)
    #df_playlist_audio_features.set_index('track_name', inplace=True, drop=True)
    df_audio_features.set_index('track_id', inplace=True, drop=True)
    return df_audio_features#df_playlist_audio_features




def agg_of_song_features(songs_of_all_users):
    '''
    Given dataframe of song features, calculate median --- This function should be deprecated but keeping it for convenience
    '''
    assert isinstance(songs_of_all_users, pd.DataFrame)
    return pd.DataFrame(songs_of_all_users.median(), columns= ['fav_playlist'])


def mean_audio_features_playlist(sp, playlist_id):
    assert isinstance(playlist_id, type(''))
    Playlist = fetch_audio_features(sp, playlist_id)#df_playlist_audio_features(sp, playlist_id)
    return pd.DataFrame(Playlist.mean(), columns= [playlist_id])


def normalize_songs_with_common_user_features(songs_of_all_users, mean_of_song_features):
    new_dataframe=songs_of_all_users.subtract(mean_of_song_features.squeeze(), axis=1)
    new_dataframe.divide(mean_of_song_features, axis='columns')
    new_dataframe.drop(['instrumentalness'], axis=1)
    new_dataframe['variation'] = new_dataframe.sum(axis=1)
    new_dataframe['variation'] = new_dataframe['variation'].abs()
    new_dataframe = new_dataframe.drop_duplicates()
    new_dataframe=new_dataframe.nsmallest(50,'variation', keep='first')
    
    return new_dataframe.index

def create_playlist_new(sp, playlist_name = "TestPlaylist", playlist_description="Test Playlist"):
    user =  sp.current_user()['id']
    playlists = sp.user_playlist_create(user,playlist_name, description = playlist_description)
    playlist_id = playlists['id']
    return playlist_id


def enrich_playlist(sp, username, playlist_id, playlist_tracks):
    index = 0
    results = []
    
    while index < len(playlist_tracks):
        results += sp.user_playlist_add_tracks(username, playlist_id, tracks = playlist_tracks[index:index + 50])
        index += 50


def get_genres(sp, track_ids):
    genres= set()
    for track_id in track_ids:
        genres.update(sp.artist(track_id)['genres'])
    return genres  



def get_recently_played_track_ids(sp):
    results_recents= sp.current_user_recently_played(limit=50)
    track_id = []
    for i, items in enumerate(results_recents['items']):
        track_id.append(items['track']['id'])
    return track_id

def get_recommendations_tracks_from_genre (sp,genre,popularity=50,limit=100):
    '''
    Get Tracks that are most popular given genre
    '''
    recos=sp.recommendations(seed_genres=genre,limit=limit, min_popularity=popularity)
    track_ids=[]
    for track in recos['tracks']:
        album_id=track['album']['id']
        album_tracks=sp.album_tracks(album_id)
        for track in album_tracks['items']:
            track_ids.append(track['id'])
    return track_ids