from importlib.machinery import DEBUG_BYTECODE_SUFFIXES
from statistics import mean
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

try:
    from .psecrets import client_id, secret
except:
    from psecrets import client_id, secret

app = Flask(__name__, static_folder="static")
path = os.path.dirname(os.path.abspath(__file__))
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")
scopes  = 'user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control user-read-playback-position user-read-private user-read-email user-top-read playlist-modify-public playlist-modify-private'
user_json = os.path.join(path, 'json', 'userdata.json')
party_json = os.path.join(path, 'json', 'parties.json')

debug = True

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
    checkjson('userdata')
    users = readjson(user_json)

    number_of_users=len(users)
    songs_of_all_users=[]
    for user in users:
        token = users[user]['token']#'6Fu7clVzrnvLUBC0YbxDrN'#
        if token:
            sp = spotipy.Spotify(auth=token)
        else:
            print("Can't get token for", owner)
        songs_of_all_users.append(get_user_top_tracks(sp))
    
    songs_df = pd.concat(songs_of_all_users)

    song_audio_features=fetch_audio_features(sp, songs_df)
    
    owner_token = users[owner]['token']
    if owner_token:
            sp_owner = spotipy.Spotify(auth=owner_token)
    else:
        print("Can't get token for", owner)

    mean_song_audio_features=mean_of_song_features(song_audio_features)

    normalized_songs=normalize_songs_with_common_user_features(song_audio_features, mean_song_audio_features)

    id = create_playlist(sp_owner, 'JS Blend', 'Test playlist created using python!')
    enrich_playlist(sp_owner, owner, id, normalized_songs)
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
    
    
def get_user_top_tracks(sp):
    results = sp.current_user_top_tracks(limit=50, offset=0,time_range='medium_term')
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



def mean_of_song_features(songs_of_all_users):
    return pd.DataFrame(songs_of_all_users.median(), columns= ['fav_playlist'])

def normalize_songs_with_common_user_features(songs_of_all_users, mean_of_song_features):
    new_dataframe=songs_of_all_users.subtract(mean_of_song_features.squeeze(), axis=1)
    new_dataframe.divide(mean_of_song_features, axis='columns')
    new_dataframe.drop(['instrumentalness'], axis=1)
    new_dataframe['variation'] = new_dataframe.sum(axis=1)
    new_dataframe['variation'] = new_dataframe['variation'].abs()
    new_dataframe = new_dataframe.drop_duplicates()
    new_dataframe=new_dataframe.nsmallest(50,'variation', keep='first')
    
    return new_dataframe.index

def create_playlist(sp, playlist_name, playlist_description):
    user =  sp.current_user()['id']
    playlists = sp.user_playlist_create(user,"TestPlaylist", description = "Test Playlist")
    playlist_id = playlists['id']
    return playlist_id


def enrich_playlist(sp, username, playlist_id, playlist_tracks):
    index = 0
    results = []
    
    while index < len(playlist_tracks):
        results += sp.user_playlist_add_tracks(username, playlist_id, tracks = playlist_tracks[index:index + 50])
        index += 50


if __name__ == '__main__':
    socketio.run(app, debug=True)#port=10001,host='0.0.0.0', debug=True)
