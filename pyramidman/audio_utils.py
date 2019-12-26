"""A set of utilities to handle audio.

Returns:
    [type] -- [description]
"""

import pyaudio
import sounddevice as sd
import speech_recognition as sr


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


def calibrate_microphone(mic: sr.Microphone, r: sr.Recognizer, duration = 5, dynamic_energy_threshold=True):
    print(f"Calibrating microphone for {duration} seconds.")
    with mic as source:
        # listen for "duration" seconds and create the ambient noise energy level
        r.adjust_for_ambient_noise(source, duration=duration)
        r.dynamic_energy_threshold = dynamic_energy_threshold

    print("Calibrated")


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


def empty_stream(source):
    ## Empty the buffer first
    source.stream.pyaudio_stream.get_read_available()

    while True:
        available_bits = source.stream.pyaudio_stream.get_read_available()
        ns = int(source.SAMPLE_RATE * 0.1)
        n_read = len(source.stream.read(ns))
        
        print("Samples to read:", ns, "Bytes read: ", n_read, "Available bits: ", available_bits)
        if(available_bits < source.CHUNK):
            break
    