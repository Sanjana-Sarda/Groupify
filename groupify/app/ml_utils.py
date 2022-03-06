

def genre_consistency(sp,predicted_playlist_genres,user_genres):
    genre_consistency= len(predicted_playlist_genres.intersection(user_genres))/len(predicted_playlist_genres)
    return genre_consistency

def song_newness(sp, predicted_playlist):
    number_of_new_tracks=0
    for track in predicted_playlist:
        if not sp.current_user_saved_tracks_contains([track]) and track not in get_recently_played_track_ids(sp):
            number_of_new_tracks+=1
    return number_of_new_tracks*100/len(predicted_playlist)