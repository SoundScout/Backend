# music/utils/recommendation_engine.py

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from music.models import TrackFeature, Interaction
from users.models import User

def generate_user_recommendations(user_id, top_n=10):
    """
    Given a user ID, recommend top_n tracks based on their liked tracks.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return []

    # Get tracks the user liked
    liked_interactions = Interaction.objects.filter(user=user, interaction_type='like').select_related('track')
    liked_track_ids = liked_interactions.values_list('track__id', flat=True)

    if not liked_track_ids:
        return []  # No likes yet

    # Get embeddings of liked tracks
    liked_embeddings = []
    for track_feature in TrackFeature.objects.filter(track_id__in=liked_track_ids):
        if track_feature.embedding:
            liked_embeddings.append(np.array(track_feature.embedding))

    if not liked_embeddings:
        return []

    liked_embeddings = np.vstack(liked_embeddings)

    # Get all candidate tracks (excluding liked tracks)
    candidate_tracks = TrackFeature.objects.exclude(track_id__in=liked_track_ids)

    candidates = []
    candidate_embeddings = []
    for track_feature in candidate_tracks:
        if track_feature.embedding:
            candidates.append(track_feature.track)
            candidate_embeddings.append(np.array(track_feature.embedding))

    if not candidate_embeddings:
        return []

    candidate_embeddings = np.vstack(candidate_embeddings)

    # Calculate cosine similarity between liked embeddings and candidate embeddings
    similarities = cosine_similarity(candidate_embeddings, liked_embeddings)

    # Average similarity scores across all liked tracks
    avg_similarities = np.mean(similarities, axis=1)

    # Sort candidates by similarity
    top_indices = np.argsort(avg_similarities)[::-1][:top_n]

    recommended_tracks = [candidates[i] for i in top_indices]

    return recommended_tracks
