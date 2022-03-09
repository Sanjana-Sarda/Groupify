from importlib.machinery import DEBUG_BYTECODE_SUFFIXES
from statistics import mean
import traceback
from flask import Flask, render_template, request, abort, make_response, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from werkzeug.exceptions import HTTPException
import os
import json
import requests
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import pandas as pd
import numpy as np
from sklearn import preprocessing
from operator import itemgetter
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from sklearn.utils import shuffle

from spotify_utils import *
from feature_engineering_utils import *

# import ipdb

import argparse

try:
    from .psecrets import client_id, secret
except:
    from psecrets import client_id, secret

app = Flask(__name__, static_folder="static")
path = os.path.dirname(os.path.abspath(__file__))
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")
scopes  = 'user-read-playback-state user-read-recently-played user-modify-playback-state user-read-currently-playing app-remote-control user-read-playback-position user-read-private user-read-email user-top-read playlist-modify-public playlist-modify-private'
scopes = scopes + ' user-follow-read user-library-read playlist-read-collaborative'

user_json = os.path.join(path, 'json', 'userdata.json')
party_json = os.path.join(path, 'json', 'parties.json')

debug = True


parser = argparse.ArgumentParser('What algorithm to run?')
parser.add_argument('--algo', type=int, help = '0. numerical features + genre, 1. audio analysis + genre, 3. DSP + audio analysis + genre ', default=1)
args = parser.parse_args()
algo_choice = int(args.algo)

if __name__ =='__main__':
    debug = True

def checkjson(name):
    name  = '{}.json'.format(name)
    if 'json' not in os.listdir(path):
        os.mkdir(os.path.join(path, 'json'))
    if name not in os.listdir(os.path.join(path, 'json')):
        with open(os.path.join(path, 'json', name), 'w') as e:
            json.dump({}, e)

def readjson(file):
    
    with open(file, 'r') as e:
        return json.load(e)

def writejson(file, data):
    with open(file, 'w') as e:
        json.dump(data, e)

def randomchars(n):
    return ''.join([random.choice('abcedfghijklmnopqrstuywxzABCDEFGHIJKLMNOPQRSTUVWXZ1234567') for i in range(n)])

@app.route('/')
def home():
    redirect = 'http://' + request.host+ '/logged-in'
    link = 'https://accounts.spotify.com/authorize?response_type=code&client_id={}&scope={}&redirect_uri={}'.format(client_id, scopes, redirect)  
    resp = make_response(render_template('home.html', host=request.host))
    resp.set_cookie('link', link)
    return resp

@app.route('/login')
def login():
    redirect = 'http://' + request.host+ '/logged-in'
    link = 'https://accounts.spotify.com/authorize?response_type=code&client_id={}&scope={}&redirect_uri={}'.format(client_id, scopes, redirect)  
    resp = make_response(render_template('login.html', host=request.host))
    resp.set_cookie('link', link)
    return resp

@app.route('/logged-in')
def logged_in():
    code = request.args.get('code')
    if not code:
        abort(404)    
    redirect_url = 'http://' + request.host+ '/logged-in'
    response = requests.post('https://accounts.spotify.com/api/token', data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_url,
        'client_id': client_id,
        'client_secret': secret
    }).json()
    if 'access_token' in response:
        token, refresh = response['access_token'], response['refresh_token']
        user_info = requests.get('https://api.spotify.com/v1/me', headers = {'Authorization': 'Bearer {}'.format(token)}).json()
        user, link = user_info['display_name'], user_info['external_urls']['spotify']
        if user_info['product'] == 'premium':
            premium = True
        else:
            premium = False
        user_id = randomchars(40)
        checkjson('userdata')
        data = readjson(user_json)
        if user not in data:    
            data[user] = {'token': token, 'refresh': refresh, 'id': user_id, 'link': link, 'premium': premium}
        else:
            data[user]['token'] = token
            data[user]['premium'] = premium
            user_id = data[user]['id']
        writejson(user_json, data)
        resp = make_response('<script src="/static/js/globals.js"></script><script src="/static/js/loggedin.js"></script>')
        resp.set_cookie('user_id', user_id)
        resp.set_cookie('username', user)
        resp.set_cookie('token', token)
        return resp
    return redirect('/')

@app.route('/logout')
def logout():
    return '<script src="/static/js/globals.js"></script><script src="/static/js/logout.js"></script>'

@app.route('/create')
def create():
    owner = request.cookies.get('username')
    if not owner: 
        return redirect('/login?redirect=create')
    party_id, party_key = randomchars(10), randomchars(40)
    checkjson('parties')
    checkjson('userdata')
    users, data = readjson(user_json), readjson(party_json)
    for party in data:
        if data[party]['owner'] == owner:
            return redirect('/party/{}'.format(party))
    data[party_id] = {
        'owner': owner, 'owner_id': request.cookies.get('user_id'), 
        'key': party_key, 
        "members": {owner: {'link': users[owner]['link'], 'owner': True}}
    }
    writejson(party_json, data)
    resp = make_response(redirect('/party/{}'.format(party_id)))
    resp.set_cookie('party_key', party_key)
    resp.set_cookie('party_id', party_id)
    return resp

@app.route('/create-playlist')
def create_playlist():
    owner = request.cookies.get('username')
    if not owner: 
        return redirect('/login?redirect=create')
    party_id = request.referrer[28:]
    checkjson('parties')
    party_users = list(readjson(party_json)[party_id]['members'].keys())
    checkjson('userdata')
    users = readjson(user_json)
    # import ipdb
    # ipdb.set_trace()
    number_of_users=len(users)
    songs_of_all_users=[]
    user_str = ""
    for user in party_users:
        print (user)
        user_str += user+ " + "
        token = users[user]['token']
        if token:
            sp = spotipy.Spotify(auth=token)
        else:
            print("Can't get token for", owner)
        songs_of_all_users.append(fetch_playlists(sp, users[user]['link'][30:]))
        #songs_of_all_users.append(get_user_top_tracks(sp))

    songs_df = pd.concat(songs_of_all_users)
    song_audio_features=fetch_audio_features_playlist(sp, songs_df)
    # ipdb.set_trace()
    songs_df = preprocess(song_audio_features)
    # ipdb.set_trace()

    playlist_tracks = model(songs_df)

    # import ipdb
    # ipdb.set_trace()
    
    # playlist_tracks = sp.recommendations(seed_tracks = playlist_tracks.indexes.tolist(), limit = 100)

    owner_token = users[owner]['token']
    if owner_token:
            sp_owner = spotipy.Spotify(auth=owner_token)
    else:
        print("Can't get token for", owner)
    
    id = create_playlist(sp_owner, user_str[:-2] +'Blend')
    enrich_playlist(sp_owner, owner, id, playlist_tracks)
    resp = make_response(render_template('playlists.html', host=request.host))
    resp.set_cookie('playlist_id', id)
    return resp
    #return "200"

@app.route('/party/<name>')
def party(name):
    checkjson('parties')
    parties = readjson(party_json)
    if not name in parties:
        abort(404)
    username = request.cookies.get('username')
    party_key = request.cookies.get('party_key')
    user_id = request.cookies.get('user_id')
    if not username:
        return redirect('/login?redirect=/party/{}'.format(name))
    if username==parties[name]['owner']:
        if user_id == parties[name]['owner_id'] or party_key==parties[name]['key']:
            resp = make_response(render_template('party_owner.html', host=request.host))
            resp.set_cookie('party_key', parties[name]['key'])
            resp.set_cookie('party_id', name)
            return resp
    resp = make_response(render_template('party_member.html', host=request.host, party_host=parties[name]['owner']))
    return resp

@app.route('/end/<name>')
def end(name):
    checkjson('parties')
    parties = readjson(party_json)
    if not name in parties:
        abort(404)
    owner = request.cookies.get('username')
    party_key = request.cookies.get('party_key')
    if parties[name]['owner'] != owner or parties[name]['key'] != party_key:
        abort(404)
    del parties[name]
    writejson(party_json, parties)
    resp = make_response(redirect('/'))
    resp.delete_cookie('party_key')
    resp.delete_cookie('party_id')
    return resp

@app.route('/refresh/<name>/<uid>')
def refresh(name, uid):
    checkjson('userdata')
    data = readjson(user_json)
    if name not in data:
        abort(404)
    if data[name]['id'] != uid:
        abort(404)
    refresh = data[name]['refresh']
    response = requests.post('https://accounts.spotify.com/api/token', data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh,
        'client_id': client_id,
        'client_secret': secret
    }).json()
    return response['access_token']

if debug:
    @app.errorhandler(Exception)
    def error(e):
        print (e)
        code = 500
        name = "Internal Server Error"
        if isinstance(e, HTTPException):
            code = e.code
            name = " " + e.name
        return render_template("error.html", host=request.host, errno=str(code), name=name)

@socketio.on('join')
def join(data):
    username = data['username']
    party = data['party_id']
    user_data, parties = readjson(user_json), readjson(party_json) 
    if party in parties:
        members, owner = parties[party]['members'], False
        if username == parties[party]['owner']:
            owner = True
        members[username] = {'link': user_data[username]['link'], 'owner': owner}
        parties[party]['members'] = members
        writejson(party_json, parties)
        print(username + ' joined ' + party)
        join_room(party)
        emit('join', {'username': username, 'members': members, 'owner': owner}, room=party)

@socketio.on('leave')
def leave_socket(data):
    username = data['username']
    party = data['party_id']
    if party:
        parties = readjson(party_json)
        if party in parties:
            members = parties[party]['members']
            del members[username]
            parties[party]['members'] = members
            writejson(party_json, parties)
            print(username + ' left ' + party)
            leave_room(party)
            emit('leave',  {'username': username, 'action': 'left', 'members': members, 'owner': parties[party]['owner']}, room=party)

@socketio.on('end')
def end_party(data):
    parties = readjson(party_json)
    party_id = data['party_id']
    key = data['key']
    party = parties[party_id]
    if party['key'] == key:
        print(party_id + ' has been ended')
        emit('end', '{} has ended this party'.format(party['owner']), room=party_id)

@socketio.on('update')
def update(data):
    user = None
    if 'user' in data:
        user = data['user']
    artists = [{'name': a['name'], 'link': a['external_urls']['spotify']} for a in data['item']['artists']]
    ret_data = {
        'song': {'name': data['item']['name'], 'link': data['item']['album']['external_urls']['spotify'] + '?highlight=' + data['item']['uri'],}, 
        'playing': data['is_playing'],
        'song_uri': data['item']['uri'],
        'artists': artists,
        'cover': {'img': data['item']['album']['images'][1]['url'], 'link': data['item']['album']['external_urls']['spotify']},
        'time': data['progress_ms'],
        'user': user
    }
    print(json.dumps(ret_data, indent=2))
    emit('update', ret_data, room=data['party_id'])
    
   
   
    
def fetch_playlists(sp, username):
    id = []
    name = []
    num_tracks = []
    playlists = sp.user_playlists(username)
    for i, items in enumerate(playlists['items']):
        id.append(items['id'])
        name.append(items['name'])
        num_tracks.append(items['tracks']['total'])
    df_playlists = pd.DataFrame({"id":id, "name": name, "#tracks": num_tracks})
    for i, playlist in enumerate(df_playlists['id']):
        try:
            string_command = "df_{} = fetch_playlist_tracks(sp, playlist)".format(playlist)
            exec(string_command)
        except:
            pass
    frames = []
    for i, playlist in enumerate(df_playlists['id']):
        try:
            string_command = "frames.append(df_{})".format(playlist)
            exec(string_command)
        except:
            pass
    frames.append(fetch_tracks(sp))
    df =pd.concat(frames)
    return df


def fetch_tracks(sp):
    results_recently_played = sp.current_user_recently_played(limit=25)['items']
    track_name = []
    track_id = []
    artist = []
    artist_id = []
    duration = []
    popularity = []
    for i, items in enumerate(results_recently_played):
        track_name.append(items['track']['name'])
        track_id.append(items['track']['id'])
        artist.append(items['track']["artists"][0]["name"])
        artist_id.append(items['track']["artists"][0]["id"])
        duration.append(items['track']["duration_ms"])
        popularity.append(items['track']["popularity"])

    df_playlist_tracks = pd.DataFrame({ "track_name": track_name, 
    "track_id": track_id,
    "artist": artist,
    "artist_id": artist_id,
    "duration": duration,
    "popularity": popularity})
    df_playlist_tracks= df_playlist_tracks.assign(user_id=sp.current_user()['id'])
    return df_playlist_tracks
    

def fetch_playlist_tracks(sp, playlistsid): 
    offset = 0
    tracks = []
    while True:
        content = sp.playlist_tracks( playlistsid, fields=None, limit=100, offset=offset, market=None)
        tracks += content['items']
        
        if content['next'] is not None:
            offset += 100
        else:
            break
    track_name = []
    track_id = []
    artist = []
    artist_id = []
    duration = []
    popularity = []
    for i, items in enumerate(tracks):
        track_name.append(items['track']['name'])
        track_id.append(items['track']['id'])
        artist.append(items['track']["artists"][0]["name"])
        artist_id.append(items['track']["artists"][0]["id"])
        duration.append(items['track']["duration_ms"])
        popularity.append(items['track']["popularity"])

    df_playlist_tracks = pd.DataFrame({ "track_name": track_name, 
    "track_id": track_id,
    "artist": artist,
    "artist_id": artist_id,
    "duration": duration,
    "popularity": popularity})
    df_playlist_tracks= df_playlist_tracks.assign(user_id=sp.current_user()['id'])
    #df_playlist_tracks.drop_duplicates(inplace=True)
    return df_playlist_tracks


def fetch_audio_features_playlist(sp, playlist):
    #playlist = fetch_playlist_tracks(sp, playlist_id)
    if algo_choice >=2: 
        use_all_features = True
    else: 
        use_all_features = False

    playlist = playlist.reset_index(drop=True)

    # import ipdb
    if use_all_features: 
        # ipdb.set_trace()
        genres = []
        index = 0
        while index < playlist.shape[0]:
            try: 
                #print(sp.artists( playlist.iloc[index:index+50, 3])['artists'])
                genres += list(map(itemgetter('genres'), sp.artists( playlist.iloc[index:index+50, 3])['artists']))
            # genres += [sp.artists( playlist.iloc[index:index+50, 3])['genres']]
                index += 50
            except AttributeError as ae: 
                ## hack fixing bug that happens when trackid = None
                print(traceback.print_exc(5))
                index += 50
                continue
        trackids = playlist.iloc[:, 1].values.tolist()


        from joblib import parallel_backend
        from joblib import Parallel, delayed

        if algo_choice == 2: 
            #import ipdb
            #ipdb.set_trace()
            import time
            now = time.time()
            with parallel_backend('threading', n_jobs=2):
                testdicts=Parallel()(delayed(get_extensive_audio_features)(sp, track) for track in trackids)
            df_audio_features = pandas.DataFrame(testdicts).fillna(0)
            print(time.time()- now)
            #ipdb.set_trace()

            # df_audio_features = gen_extensive_audio_features(sp, trackids, pvalues= [10,25,50,75,90], perform_dsp = False, return_basic_features = True)
        elif algo_choice == 3:
            df_audio_features = gen_extensive_audio_features(sp, trackids, pvalues= [10,25,50,75,90], perform_dsp = True, return_basic_features = True)
        else: 
            print('invalid algo choice/ unable to parse')

        # if algo_choice == 2: 
        #    df_audio_features = gen_extensive_audio_features(sp, trackids, pvalues= [10,25,50,75,90], perform_dsp = False, return_basic_features = True)
        # elif algo_choice == 3:
        #    df_audio_features = gen_extensive_audio_features(sp, trackids, pvalues= [10,25,50,75,90], perform_dsp = True, return_basic_features = True)
        # else: 
        #    print('invalid algo choice/ unable to parse')
        # ipdb.set_trace()

    else: 

        index = 0
        audio_features = []
        # Make the API request
        # ipdb.set_trace()
        while index < playlist.shape[0]:
            try: 
                audio_features += sp.audio_features(playlist.iloc[index:index + 50, 1])
                index += 50
            except AttributeError as ae: 
                ## hack fixing bug that happens when trackid = None
                print(traceback.print_exc(5))
                index += 50
                continue

        # ipdb.set_trace()
        genres = []
        index = 0
        while index < playlist.shape[0]:
            try: 
                #print(sp.artists( playlist.iloc[index:index+50, 3])['artists'])
                genres += list(map(itemgetter('genres'), sp.artists( playlist.iloc[index:index+50, 3])['artists']))
            # genres += [sp.artists( playlist.iloc[index:index+50, 3])['genres']]
                index += 50
            except AttributeError as ae: 
                ## hack fixing bug that happens when trackid = None
                print(traceback.print_exc(5))
                index += 50
                continue

        # ipdb.set_trace()
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
                                                                'instrumentalness', 'loudness', 'liveness', 'duration_ms', 'key',
                                                                'valence', 'speechiness', 'mode'])
        df_audio_features =  pd.get_dummies(df_audio_features, drop_first = True, columns = ['key','mode'])
        # Create the final df, using the 'track_id' as index for future reference
    # ipdb.set_trace()
    df_audio_features['genres'] = genres
    df_audio_features = fix_genres(df_audio_features)
    
    df_playlist_audio_features = pd.concat([playlist, df_audio_features], axis=1)
    df_playlist_audio_features.set_index('track_id', inplace=True, drop=True)
    return df_playlist_audio_features


def fix_genres(df):
    v = df.genres.values
    l = [len(x) for x in v.tolist()]
    f, u = pd.factorize(np.concatenate(v))
    n, m = len(v), u.size
    i = np.arange(n).repeat(l)

    dummies = pd.DataFrame(
        np.bincount(i * m + f, minlength=n * m).reshape(n, m),
        df.index, u
    )
    return df.drop('genres', 1).join(dummies)


def preprocess(df):
    nds = df.select_dtypes(include=['float64',"int64"])
    numerical_features = ['danceability', 'acousticness', 'energy', 'instrumentalness','liveness','valence']
    features_to_be_scaled=nds.drop(columns=numerical_features)
    scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))
    ndsmx = pd.DataFrame((scaler.fit_transform(features_to_be_scaled)))
    ndsmx.columns=features_to_be_scaled.columns 
    normalized_data_set=pd.concat([df[numerical_features].reset_index(drop=True),ndsmx.reset_index(drop=True)],axis=1)
    normalized_data_set['instrumentalness'] = np.where((normalized_data_set.instrumentalness <(10**(-3))), 0, normalized_data_set.instrumentalness)
    thresh = 100    

    to_drop = normalized_data_set.eq(0).rolling(thresh).sum().eq(thresh).any()
    normalized_data_set = normalized_data_set.loc[:, ~to_drop]

    normalized_data_set.set_index(df.index, inplace=True)
    normalized_data_set['user_id'] = df.user_id
    return normalized_data_set


def model (df1):
    df, n_clusters = kmeans(df1.iloc[: , :-1])
    final = list()
    df1 = df1[~df1.index.duplicated(keep='first')]
    for cluster in range(n_clusters):
        try: 
            df2 = df.loc[df['cluster'] == cluster+1]
            df2, n1_clusters = kmeans(df2.iloc[:,:-1])
            df2['user_id']= df1.loc[df2.index.values]['user_id'].values
            final.append(df2.loc[df2['cluster']==(pick_cluster(df2, n1_clusters))])
        except: 
            print(traceback.print_exc(5))
            continue 
    x = 50/sum(len(d) for d in final)
    x = min(1, x)
    tracks = []
    for cluster in range(len(final)): #range(n_clusters):
        tracks.append(final[cluster].groupby('user_id').sample(frac=x))
    return pd.concat(tracks)
        
        
def kmeans(df):
    silhouette_avg = []
    for num_clusters in range(2, 6):
        kmeans = KMeans(n_clusters=num_clusters)
        kmeans.fit(df)
        cluster_labels = kmeans.labels_
        silhouette_avg.append(silhouette_score(df, cluster_labels))
    n_clusters = np.argmax(silhouette_avg)+2
    kmeans = KMeans(n_clusters = n_clusters, init = 'k-means++', random_state = 42)
    y_kmeans = kmeans.fit_predict(df)+1
    df['cluster'] = y_kmeans
    return df, n_clusters


def pick_cluster(df2, n1_clusters):
    p = 1
    o = 1
    for cluster in range(n1_clusters):
        val =  df2[df2['cluster']==cluster+1]['user_id'].value_counts(normalize=True)[0]
        if (val<p):
            p = val
            o = cluster+1
    return o


def create_playlist(sp, playlist_name='TestPlaylist', playlist_description='Groupify Blend'):
    user =  sp.current_user()['id']
    playlists = sp.user_playlist_create(user,playlist_name, description = playlist_description)
    playlist_id = playlists['id']
    return playlist_id


def enrich_playlist(sp, username, playlist_id, playlist_tracks):
    index = 0
    playlist_tracks = shuffle(playlist_tracks)
    sp.user_playlist_add_tracks(username, playlist_id, tracks = playlist_tracks.index.values)



if __name__ == '__main__':
    socketio.run(app, debug=True)#port=10001,host='0.0.0.0', debug=True)
