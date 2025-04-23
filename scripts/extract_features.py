#!/usr/bin/env python3
"""
extract_features.py

Standalone script to extract audio features using librosa.
Usage:
    python extract_features.py /path/to/audio/file.mp3
"""

import argparse
import json
import os

import librosa
import numpy as np

def extract_features(file_path):
    """
    Extract audio features from a given file path.

    Returns a dictionary with:
      - tempo (BPM)
      - energy (RMS)
      - zero_crossing_rate
      - spectral_centroid
      - spectral_rolloff
      - chroma_stft mean values
    """
    # Load audio
    y, sr = librosa.load(file_path, sr=None)

    # Tempo (BPM)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    # Energy (RMS)
    energy = float(np.mean(librosa.feature.rms(y=y)))

    # Zero Crossing Rate
    zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)))

    # Spectral Centroid
    spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))

    # Spectral Rolloff
    spectral_rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))

    # Chroma STFT
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = [float(np.mean(chroma[i])) for i in range(chroma.shape[0])]

    features = {
        'tempo': tempo,
        'energy': energy,
        'zero_crossing_rate': zcr,
        'spectral_centroid': spectral_centroid,
        'spectral_rolloff': spectral_rolloff,
        'chroma_mean': chroma_mean,
    }
    return features

def main():
    parser = argparse.ArgumentParser(description="Extract audio features from a file.")
    parser.add_argument('file_path', type=str, help="Path to the audio file")
    args = parser.parse_args()
    file_path = args.file_path

    if not os.path.isfile(file_path):
        print(f"Error: file '{file_path}' does not exist.")
        return

    features = extract_features(file_path)
    print(json.dumps(features, indent=2))

if __name__ == "__main__":
    main()
