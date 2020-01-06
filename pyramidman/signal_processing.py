from scipy import signal
import numpy as np


from scipy.signal import butter, lfilter, freqz


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

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y
