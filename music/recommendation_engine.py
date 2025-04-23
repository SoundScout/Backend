# music/recommendation_engine.py

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from users.models import UserPreference
from music.models import Track, TrackFeature
from playlists.models import Recommendation

def generate_user_vector(user):
    """
    Create a user profile vector based on preferences.
    """
    preference = getattr(user, 'preference', None)
    if not preference:
        return None

    # Genre and mood one-hot encoding
    all_genres = ["Pop", "Rock", "Hip-Hop", "Electronic", "Jazz", "Classical", "Metal", "Country", "Reggae", "Blues"]
    all_moods = ["Happy", "Sad", "Energetic", "Calm", "Angry", "Romantic", "Melancholic", "Chill"]

    genre_vector = np.array([1 if genre in preference.favorite_genres else 0 for genre in all_genres])
    mood_vector = np.array([1 if mood in preference.favorite_moods else 0 for mood in all_moods])

    # Numeric features
    numeric_vector = np.array([
        preference.average_tempo or 0,
        preference.average_danceability or 0,
        preference.average_energy or 0,
        preference.average_valence or 0,
    ])

    full_vector = np.concatenate((genre_vector, mood_vector, numeric_vector))

    return full_vector.reshape(1, -1)  # Reshape to 2D

def generate_track_vector(track):
    """
    Create a track feature vector.
    """
    # Fetch track features
    try:
        features = TrackFeature.objects.get(track=track)
    except TrackFeature.DoesNotExist:
        return None

    all_genres = ["Pop", "Rock", "Hip-Hop", "Electronic", "Jazz", "Classical", "Metal", "Country", "Reggae", "Blues"]
    all_moods = ["Happy", "Sad", "Energetic", "Calm", "Angry", "Romantic", "Melancholic", "Chill"]

    genre_vector = np.array([1 if track.genre == genre else 0 for genre in all_genres])
    mood_vector = np.array([1 if track.mood == mood else 0 for mood in all_moods])

    numeric_vector = np.array([
        features.tempo or 0,
        features.danceability or 0,
        features.energy or 0,
        features.valence or 0,
    ])

    full_vector = np.concatenate((genre_vector, mood_vector, numeric_vector))

    return full_vector.reshape(1, -1)

def recommend_tracks_for_user(user, num_recommendations=10):
    """
    Recommend tracks for a given user based on content similarity.
    """

    user_vector = generate_user_vector(user)
    if user_vector is None:
        return []

    all_tracks = Track.objects.filter(approval_status='approved')  # Only approved tracks

    track_similarities = []

    for track in all_tracks:
        track_vector = generate_track_vector(track)
        if track_vector is not None:
            similarity = cosine_similarity(user_vector, track_vector)[0][0]
            track_similarities.append((track, similarity))

    # Sort tracks by similarity score, descending
    track_similarities.sort(key=lambda x: x[1], reverse=True)

    recommended_tracks = [track for track, sim in track_similarities[:num_recommendations]]

    # Save recommendations into the database
    Recommendation.objects.filter(user=user).delete()  # Clear old recommendations
    for track in recommended_tracks:
        Recommendation.objects.create(user=user, track=track)

    return recommended_tracks
