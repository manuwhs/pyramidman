"""A set of utilities to handle audio.

Returns:
    [type] -- [description]
"""

import pyaudio
import sounddevice as sd
import speech_recognition as sr
import time 
import numpy as np

def get_microphone_info(index: int):
    """Returns the information of the given microphone index.
    """
    return sd.query_devices(index, 'input')


def get_available_microphones() -> dict:
    """Returns a dictionary with the avialable system dictionaries.
    """
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    device_dict = {}
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            device_name = p.get_device_info_by_host_api_device_index(
                0, i).get("name")
            # print ("Input Device id ", i, " - ", device_name )
            device_dict[str(i)] = device_name
    return device_dict


def get_all_devices_str() -> str:
    """Returns a string with the available sound devices.
    """
    return sd.query_devices()


def get_sysdefault_microphone_index():
    """ It returns the index of the sysdefault microphone
    """
    device_dict = get_available_microphones()
    for k in device_dict.keys():
        if device_dict[k] == "sysdefault":
            return int(k)
    print("No system default microphone found")
    return None


def calibrate_microphone(mic: sr.Microphone, r: sr.Recognizer, duration = 5, warmup_duration = 0):

    print(f"Calibrating microphone for {duration} seconds.")
    with mic as source:
        if warmup_duration > 0:
            time.sleep(warmup_duration)
            empty_stream(source, time_step = 0.1)
            
        # listen for "duration" seconds and create the ambient noise energy level
        r.adjust_for_ambient_noise(source, duration=duration)

    print("Calibrated energy threshold: ", r.energy_threshold)


def stereo_to_mono(signal):
    """
    This function converts the input signal
    (stored in a numpy array) to MONO (if it is STEREO)
    """

    if signal.ndim == 2:
        if signal.shape[1] == 1:
            signal = signal.flatten()
        else:
            if signal.shape[1] == 2:
                signal = (signal[:, 1] / 2) + (signal[:, 0] / 2)
    return signal


def empty_stream(source, time_step = 0.1):
    """ Empties the buffer of the stream by continuously reading it until it is empty.
    """
    source.stream.pyaudio_stream.get_read_available()

    while True:
        available_bits = source.stream.pyaudio_stream.get_read_available()
        ns = int(source.SAMPLE_RATE * time_step)
        n_read = len(source.stream.read(ns))
        
        # print("Samples to read:", ns, "Bytes read: ", n_read, "Available bits: ", available_bits)
        if(available_bits < source.CHUNK):
            break

def sample_noise(audio_params, r, source, duration = 1, warmup = 2):
    """ This function returns the """
    
    with source as source:
        audio = r.record(source, duration = duration, offset = warmup)
       
    data = np.frombuffer(audio.frame_data, np.int16).astype(float)
    # select section of data that is noise
    initial_noise_duration = 1
    noise_data = data[:int(audio_params.sample_rate/initial_noise_duration)]

    return noise_data
