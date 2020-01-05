import pyaudio
import speech_recognition as sr
from .audio_utils import get_sysdefault_microphone_index, get_microphone_info

class AudioParameters:
    def __init__(self):
        self.chunk = 1024*4  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.subtype = None  # subtype = "PCM_24". Not needed in most cases
        self.channels = 1
        self.sample_rate = 48000  # Record at 48000 samples per second
        self.input_device_index = 0

    def set_sysdefault_microphone_index(self):
        """ Sets the system default microfone index as the microfone
        """
        self.input_device_index = get_sysdefault_microphone_index()

    def get_input_device_info(self):
        """ Returns a dictionary with the information of the selected input
        """
        return get_microphone_info(self.input_device_index)

    def set_default_input_parameters(self):
        """ Sets the parameters to the default values of the selected microphone
        """
        properties = self.get_input_device_info()
        self.sample_rate = int(properties["default_samplerate"])

    def get_microphone(self):
        """ Returns a Microphone object from the given object parameters.
        """
        mic = sr.Microphone(device_index=self.input_device_index,
                            sample_rate=self.sample_rate, chunk_size=self.chunk)

        return mic
