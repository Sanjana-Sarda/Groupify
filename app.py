from .funcs import *


checkjson('userdata')
number_of_users=len(readjson('userdata'))
songs_of_all_users=[]
for user in number_of_users:
    songs_of_all_users.append(get_user_top_tracks(user))



song_audio_features=fetch_audio_features(songs_of_all_users)

mean_song_audio_features=mean_of_song_features(song_audio_features)

normalized_songs=normalize_songs_with_common_user_features(songs_of_all_users,mean_song_audio_features)

create_playlist(sp, username, 'JS Blend2', 'Test playlist created using python!')



