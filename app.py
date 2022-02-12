from .funcs import *


checkjson('userdata')
number_of_users=len(readjson('userdata'))
songs_of_all_users=[]
#for user in number_of_users


song_audio_features=fetch_audio_features(all_user_songs)

mean_of_song_features=mean_of_song_features(song_audio_features)

normalized_songs=normalize_songs_with_common_user_featurs(songs_of_all_users,mean_of_song_features)



