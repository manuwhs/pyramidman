""" Basic blocking functions that read and play audio. No threads used.
"""


import pyaudio
import wave
import sys

import sounddevice as sd
import speech_recognition as sr


def play_audio(audio_parameters,  filename="output.wav"):
    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(audio_parameters.chunk)

    while data != b'':
        stream.write(data)
        data = wf.readframes(audio_parameters.chunk)
        # print(data)
    stream.stop_stream()
    stream.close()
    p.terminate()


def record_audio(audio_parameters, seconds=3, filename="output.wav"):
    p = pyaudio.PyAudio()  # Create an interface to PortAudio
    print('Recording')

    stream = p.open(format=audio_parameters.sample_format,
                    channels=audio_parameters.channels,
                    rate=audio_parameters.sample_rate,
                    frames_per_buffer=audio_parameters.chunk*5,
                    input=True,
                    input_device_index=audio_parameters.input_device_index)

    frames = []  # Initialize array to store frames

    # Store data in chunks for 3 seconds
    n_chunks = int(audio_parameters.sample_rate /
                   audio_parameters.chunk * seconds)
    for i in range(0, n_chunks):
        data = stream.read(audio_parameters.chunk, exception_on_overflow=False)
        frames.append(data)
        # print(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print('Finished recording')

    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(audio_parameters.channels)
    wf.setsampwidth(p.get_sample_size(audio_parameters.sample_format))
    wf.setframerate(audio_parameters.sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()
