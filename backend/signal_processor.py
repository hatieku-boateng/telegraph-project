"""Signal detection and processing utilities."""

import time
import numpy as np
from typing import Tuple

# Default timing parameters (seconds)
DOT_DURATION = 0.15        # Max duration for a dot
LETTER_GAP = 0.40          # Silence duration to finalize a letter
WORD_GAP = 1.00            # Silence duration to insert a word space

# Microphone parameters
GAIN = 100                 # Software amplification
SPIKE_FACTOR = 3.0         # Tap detection threshold multiplier
NOISE_SMOOTH = 0.997       # Noise floor adaptation rate
SAMPLE_RATE = 44100        # Audio sample rate

# Block size for ML feature extraction
BLOCK_SIZE = 1024


def measure_duration(start_time: float) -> float:
    """Return elapsed seconds since start_time."""
    return time.time() - start_time


def classify_signal(duration: float, dot_threshold: float = DOT_DURATION) -> str:
    """Classify a press duration as dot or dash.
    
    Args:
        duration: Press duration in seconds
        dot_threshold: Maximum duration for a dot
        
    Returns:
        '.' for dot, '-' for dash
    """
    return "." if duration < dot_threshold else "-"


def extract_features(block: np.ndarray) -> np.ndarray:
    """Extract 6 audio features from a single frame for ML classification.
    
    Args:
        block: Audio frame as numpy array
        
    Returns:
        Feature vector: [rms, peak, crest_factor, zcr, spectral_centroid, attack]
    """
    block = block.flatten()
    rms = np.sqrt(np.mean(block ** 2)) + 1e-10
    peak = np.max(np.abs(block))
    crest_factor = peak / rms
    zcr = np.sum(np.abs(np.diff(np.sign(block)))) / (2 * len(block))
    
    # Spectral centroid
    fft_mag = np.abs(np.fft.rfft(block))
    freqs = np.fft.rfftfreq(len(block), d=1.0 / SAMPLE_RATE)
    spectral_centroid = np.sum(freqs * fft_mag) / (np.sum(fft_mag) + 1e-10)
    
    # Attack: ratio of first-quarter energy to total energy
    q = len(block) // 4
    attack = np.sqrt(np.mean(block[:q] ** 2)) / rms if q > 0 else 1.0
    
    return np.array([rms, peak, crest_factor, zcr, spectral_centroid, attack])


class AdaptiveThreshold:
    """Adaptive threshold detector for microphone input."""
    
    def __init__(self, gain: float = GAIN, spike_factor: float = SPIKE_FACTOR, 
                 noise_smooth: float = NOISE_SMOOTH):
        self.gain = gain
        self.spike_factor = spike_factor
        self.noise_smooth = noise_smooth
        self.noise_floor = 0.01
        self.current_threshold = 0.03
    
    def process(self, audio_frame: np.ndarray) -> Tuple[float, float, bool]:
        """Process audio frame and detect spike.
        
        Args:
            audio_frame: Audio data (raw or amplified)
            
        Returns:
            (volume, threshold, is_spike) tuple
        """
        amplified = audio_frame * self.gain
        volume = np.linalg.norm(amplified) / len(amplified) ** 0.5
        
        # Update noise floor during silence
        self.noise_floor = self.noise_smooth * self.noise_floor + (1 - self.noise_smooth) * volume
        self.current_threshold = self.noise_floor * self.spike_factor
        
        is_spike = volume > self.current_threshold
        return volume, self.current_threshold, is_spike
    
    def reset(self):
        """Reset the adaptive threshold."""
        self.noise_floor = 0.01
        self.current_threshold = 0.03
