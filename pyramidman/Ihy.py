"""Ihy is the ancient Egyptian God of music.
Here we will create the higher order functions to play with sound using
a rather ugly UI implemented with plotly and ipywidgets.
"""

from .hieroglyph import plot_timeseries_range_slider, create_tabs, plot_spectrogram
from .signal_processing import get_spectrogram
from IPython.display import display
from scipy.io import wavfile
import numpy as np

def get_audio_analysis_charts_wav_file(filename: str):
    sample_rate, samples = wavfile.read(filename)
    audio_array = samples

    x = np.array(range(audio_array.size))/sample_rate
    y = audio_array

    timeseries_chart = plot_timeseries_range_slider(x, y, "Timeseries sound")
    spectrogram_chart = plot_spectrogram(
        *get_spectrogram(samples, sample_rate, N=512))

    return timeseries_chart, spectrogram_chart

def get_audio_menu_wav_file(filename: str):

    timeseries_chart, spectrogram_chart = get_audio_analysis_charts_wav_file(filename)
    children = [timeseries_chart, spectrogram_chart]
    tab_names = ["timeseries", "spectrogram"]
    tabs = create_tabs(children, tab_names)
    return tabs

