"""Machine learning model management for tap detection."""

import os
import pickle
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
from sklearn.ensemble import RandomForestClassifier

from signal_processor import extract_features, BLOCK_SIZE, SAMPLE_RATE


class TapDetector:
    """ML-based tap detector for microphone input."""
    
    def __init__(self, model_path: str = "tap_model.pkl"):
        self.model_path = model_path
        self.model: Optional[RandomForestClassifier] = None
        self.is_trained = False
        self._load_model()
    
    def _load_model(self):
        """Load the trained model from disk if it exists."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self.model = pickle.load(f)
                self.is_trained = True
            except Exception as e:
                print(f"Warning: Could not load model: {e}")
                self.model = None
                self.is_trained = False
    
    def train(self, bg_audio: np.ndarray, tap_audio: np.ndarray) -> float:
        """Train the tap detector on background noise and tap samples.
        
        Args:
            bg_audio: Background noise audio (numpy array)
            tap_audio: Tap audio samples (numpy array)
            
        Returns:
            Training accuracy
        """
        X, y = [], []
        
        # Extract features from background noise (label 0)
        for i in range(0, len(bg_audio) - BLOCK_SIZE, BLOCK_SIZE):
            block = bg_audio[i:i + BLOCK_SIZE]
            X.append(extract_features(block))
            y.append(0)
        
        # Compute background RMS
        bg_rms_values = [
            np.sqrt(np.mean(bg_audio[i:i + BLOCK_SIZE] ** 2))
            for i in range(0, len(bg_audio) - BLOCK_SIZE, BLOCK_SIZE)
        ]
        bg_rms = np.mean(bg_rms_values)
        
        # Extract features from taps (label 1 if loud, 0 if quiet)
        for i in range(0, len(tap_audio) - BLOCK_SIZE, BLOCK_SIZE):
            block = tap_audio[i:i + BLOCK_SIZE]
            block_rms = np.sqrt(np.mean(block ** 2))
            X.append(extract_features(block))
            y.append(1 if block_rms > bg_rms * 2 else 0)
        
        X = np.array(X)
        y = np.array(y)
        
        # Train Random Forest
        self.model = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42)
        self.model.fit(X, y)
        accuracy = self.model.score(X, y)
        self.is_trained = True
        
        # Save model
        self.save()
        
        return accuracy
    
    def predict(self, audio_frame: np.ndarray) -> Tuple[float, bool]:
        """Predict whether an audio frame contains a tap.
        
        Args:
            audio_frame: Audio frame (numpy array, should be roughly BLOCK_SIZE long)
            
        Returns:
            (tap_probability, is_tap) tuple
        """
        if not self.is_trained or self.model is None:
            return 0.0, False
        
        # Pad or trim to BLOCK_SIZE
        if len(audio_frame) < BLOCK_SIZE:
            audio_frame = np.pad(audio_frame, (0, BLOCK_SIZE - len(audio_frame)))
        else:
            audio_frame = audio_frame[:BLOCK_SIZE]
        
        feats = extract_features(audio_frame).reshape(1, -1)
        tap_prob = self.model.predict_proba(feats)[0][1]
        is_tap = tap_prob > 0.1  # Threshold of 10%
        
        return tap_prob, is_tap
    
    def save(self):
        """Save the trained model to disk."""
        if self.model is None:
            raise ValueError("No model to save")
        
        os.makedirs(os.path.dirname(self.model_path) or ".", exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump(self.model, f)
    
    def reset(self):
        """Reset the model."""
        self.model = None
        self.is_trained = False


# Global tap detector instance
_tap_detector: Optional[TapDetector] = None


def get_tap_detector() -> TapDetector:
    """Get or create the global tap detector instance."""
    global _tap_detector
    if _tap_detector is None:
        _tap_detector = TapDetector()
    return _tap_detector
