from scipy import signal
import numpy as np


def get_spectrogram(samples: np.ndarray, sample_rate: int, N: int = 512):
    """It computes the spectogram of the samples passed as input.
    
    Arguments:
        samples {np.ndarray} -- [description]
        sample_rate {int} -- [description]
    
    Keyword Arguments:
        N {int} -- [description] (default: {512})
    
    Returns:
        [type] -- [description]
    """
    w = signal.blackman(N)
    freqs, bins, spectrogram = signal.spectrogram(
        samples, sample_rate, window=w, nfft=N)
    return freqs, bins, spectrogram
