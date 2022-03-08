from collections import Counter
import librosa
import numpy, pandas
import os

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import oauth2

import traceback, wget


numerical_features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness']
numerical_features += ['valence', 'tempo', 'duration_ms']
categorical_features = ['key', 'mode']

def get_stats(arr, col_prefix='', pvalues = [0, 25, 50, 75,100]): 
    assert isinstance(arr, numpy.ndarray) or isinstance(arr, list)
    if isinstance(arr, list): 
        arr = numpy.array(arr)
    percentiles = numpy.round(numpy.percentile(arr, pvalues, axis = 0), decimals = 2).tolist()
    pvalues = [col_prefix + '_' + str(p) for p in pvalues]
    d = dict(zip(pvalues, percentiles))
    return d

def get_mean_variance(arr, col_prefix=''): 
    d = {}
    d[col_prefix + '_mean'] = numpy.round(numpy.mean(arr, axis = None), 2)
    d[col_prefix + '_std'] = numpy.round(numpy.std(arr, axis = None), 2)
    return d

def get_genre_from_track(sp, trackid, limit=1): 
    track = sp.track(trackid)
    artist = sp.artist(track["artists"][0]["external_urls"]["spotify"])
    genres = artist["genres"]
    if len(genres): 
        return genres[0:limit]
    else: 
        return []

def get_audio_df(sp, trackids, numerical_features, categorical_features): 

    feature_df = pandas.DataFrame(sp.audio_features(trackids))
    feature_df = feature_df[numerical_features + categorical_features ]
    feature_df[categorical_features] = feature_df[categorical_features].astype(str)
    feature_df = pandas.get_dummies(feature_df, drop_first = True, columns = categorical_features)
    feature_df['id'] = trackids
    return feature_df

def gen_basic_audio_features(sp, sample_trackid): 
    numerical_features= ['danceability','energy','loudness','speechiness','acousticness','instrumentalness','liveness','valence','tempo','duration_ms']
    categorical_features = ['key', 'mode']
    audio_feats = sp.audio_features(sample_trackid)[0]
    feature = {}
    for feat in numerical_features: 
        feature[feat] = audio_feats[feat]
    for feat in categorical_features: 
        val = '_fulltrack_' + str(audio_feats[feat])
        feature[feat+val] = 1
    return feature


def get_extensive_audio_features(sp, sample_trackid, pvalues= [10,25,50,75,90], perform_dsp = True, return_basic_features = False): 
    '''
    Get a single track and retrieve audio features that are in addition to the basic features.
    '''
    pitches = 'C C# D D# E F F# G G# A A# B'.split(' ')
    timbres = ['timbre_'+str(a) for a in range(12)]

    features = {'id': sample_trackid}
    
    if return_basic_features: 
        features.update(gen_basic_audio_features(sp, sample_trackid))
    
    sample_audio_analysis = sp.audio_analysis(sample_trackid)

    # processing a single track 
    num_sections = len(sample_audio_analysis['sections'])
    
    loudness = [sample_audio_analysis['sections'][a]['loudness'] for a in range(num_sections)]
    tempo = [sample_audio_analysis['sections'][a]['tempo'] for a in range(num_sections)]
    features.update(get_stats(numpy.array(loudness), 'loudness'))
    features.update(get_stats(numpy.array(tempo), 'tempo'))

    key = ['key_'+str(sample_audio_analysis['sections'][a]['key']) for a in range(num_sections)]
    mode = ['mode_'+str(sample_audio_analysis['sections'][a]['mode']) for a in range(num_sections)]
    key_counter = dict(Counter(key))
    _sum = sum(key_counter.values())
    key_counter = {a:round(b/_sum*100)/100. for a,b in key_counter.items()}
    mode_counter = dict(Counter(mode))
    _sum = sum(mode_counter.values())
    mode_counter = {a:round(b/_sum*100)/100. for a,b in mode_counter.items()}

    features.update(key_counter)
    features.update(mode_counter)


    # pitches and timbre
    num_segments = len(sample_audio_analysis['segments'])
    pitch_data = []
    timbre_data = []
    for a in range(num_segments): 
        pitch_data.append(sample_audio_analysis['segments'][a]['pitches'])
        timbre_data.append(sample_audio_analysis['segments'][a]['timbre'])
    pitch_df = pandas.DataFrame(data = numpy.array(pitch_data), columns = pitches)
    timbre_df = pandas.DataFrame(data = numpy.array(timbre_data), columns = timbres)

    for p in pitches: 
        features.update(get_stats(pitch_df[p].values, p, pvalues = [10,25,50,75,90]))
    for t in timbres: 
        features.update(get_stats(timbre_df[t].values, t, pvalues = [10,25,50,75,90]))

    if perform_dsp: 
        sample_track = sp.track(sample_trackid)
        audio_file = wget.download(sample_track['preview_url'])
        audio, sr  = librosa.load(audio_file)
        os.remove(audio_file)

        zero_crossings = librosa.feature.zero_crossing_rate(audio)
        spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)
        rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)

        features.update(get_mean_variance(zero_crossings, col_prefix='zero_crossings'))
        features.update(get_mean_variance(spectral_centroids, col_prefix='spectral_centroids'))
        features.update(get_mean_variance(rolloff, col_prefix='rolloff'))
        
    return features
    

def gen_extensive_audio_features(sp, trackids, pvalues= [10,25,50,75,90], perform_dsp = True, return_basic_features = False): 
    features_all_tracks = []
    for ind, t_id in enumerate(trackids): 
        print('processing track ', t_id, '{f} out of {e}'.format(f=ind, e=len(trackids)))
        features_all_tracks.append(get_extensive_audio_features(sp, t_id, pvalues= [10,25,50,75,90], perform_dsp = perform_dsp, return_basic_features = return_basic_features))

    df_audio_extra = pandas.DataFrame(features_all_tracks)
    return df_audio_extra



