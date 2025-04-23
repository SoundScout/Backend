import librosa
import numpy as np

def extract_features(file_path):
    """
    Extracts audio features from an audio file using librosa.

    Returns a dictionary ready to save into TrackFeature model.
    """
    try:
        y, sr = librosa.load(file_path, sr=None, mono=True)

        # Extract features
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        danceability = np.mean(librosa.feature.tempogram(y=y, sr=sr))
        energy = np.mean(librosa.feature.rms(y=y))
        valence = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr))
        speechiness = np.mean(librosa.feature.mfcc(y=y, sr=sr))
        instrumentalness = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
        acousticness = np.mean(librosa.feature.zero_crossing_rate(y))
        liveness = np.mean(librosa.feature.spectral_flatness(y=y))

        # Decide mood (very basic initial version)
        mood = predict_mood(energy, valence)

        return {
            'danceability': danceability,
            'energy': energy,
            'valence': valence,
            'tempo': tempo,
            'speechiness': speechiness,
            'instrumentalness': instrumentalness,
            'acousticness': acousticness,
            'liveness': liveness,
            'mood': mood,
        }

    except Exception as e:
        print(f"Feature extraction error: {e}")
        return {}

def predict_mood(energy, valence):
    """
    Rough mood prediction based on energy and valence values.
    """
    if energy > 0.6 and valence > 0.5:
        return 'happy'
    elif energy < 0.4 and valence < 0.4:
        return 'sad'
    elif energy > 0.7:
        return 'energetic'
    elif valence > 0.6:
        return 'romantic'
    else:
        return 'chill'
