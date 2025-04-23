# music/utils/recommendations.py

import numpy as np
from music.models import TrackFeature

def fetch_all_embeddings():
    """
    Fetches all track features embeddings from the database.
    Returns a tuple: (track_ids_list, embeddings_matrix)
    """
    track_features = TrackFeature.objects.all()
    track_ids = []
    embeddings = []

    for feature in track_features:
        if feature.embedding:
            track_ids.append(feature.track.id)
            embeddings.append(np.array(feature.embedding, dtype=np.float32))

    return track_ids, np.array(embeddings)

def compute_cosine_similarity(query_embedding, all_embeddings):
    """
    Computes cosine similarity between a query embedding and all stored embeddings.
    """
    query_norm = np.linalg.norm(query_embedding)
    all_norms = np.linalg.norm(all_embeddings, axis=1)

    similarities = np.dot(all_embeddings, query_embedding) / (all_norms * query_norm + 1e-10)
    return similarities

def get_top_k_similar_tracks(track_id, k=5):
    """
    Given a track_id, returns the top k most similar track IDs based on embedding similarity.
    """
    track_ids, embeddings = fetch_all_embeddings()

    if track_id not in track_ids:
        return []  # Track not found

    track_index = track_ids.index(track_id)
    query_embedding = embeddings[track_index]

    similarities = compute_cosine_similarity(query_embedding, embeddings)
    sorted_indices = np.argsort(similarities)[::-1]

    # Exclude the track itself
    recommended_indices = [i for i in sorted_indices if i != track_index][:k]
    recommended_track_ids = [track_ids[i] for i in recommended_indices]

    return recommended_track_ids
