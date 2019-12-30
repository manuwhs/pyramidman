
import queue
import sys
import tempfile
import threading

import numpy  # Make sure NumPy is loaded before it is used in the callback
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from speech_recognition import WaitTimeoutError

from .audio_parameters import AudioParameters
from .utils import int_or_str
from .listener import listen


def record_with_queue(audio_params: AudioParameters, filename: str):
    """Records audio using the parameters in AudioParameters.
    It saves it in the file specified in filename. It stops recording when stopped.

    Arguments:
        audio_params {AudioParameters} -- [description]
        filename {str} -- [description]
    """
    q = queue.Queue()

    def audio_callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        q.put(indata.copy())

    try:
        # Make sure the file is opened before recording anything:
        with sf.SoundFile(filename, mode='x', samplerate=audio_params.sample_rate,
                          channels=audio_params.channels, subtype=audio_params.subtype) as file:

            with sd.InputStream(samplerate=audio_params.sample_rate, device=audio_params.input_device_index,
                                channels=audio_params.channels, callback=audio_callback):

                print("Recording: Interrupt execution to stop")

                while True:
                    # constantly check if there is a new chunck to save.
                    file.write(q.get())

    except KeyboardInterrupt:
        print('\nRecording finished: ')
    except Exception as e:
        print('\nRecording finished: ')


def put_audio_data_in_queue_callback_closure(recognizer: sr.Recognizer, audio: sr.AudioData, q: queue.Queue):
    """ Closure that generates a function that puts the audio data in the desired queue.
    """

    def put_audio_data_in_queue_callback(recognizer: sr.Recognizer, audio: sr.AudioData):
        """
        This function receives the audio from the recognizer and puts it inside a queue
        to be processed by another thread.
        """
        q.put(audio)

    return put_audio_data_in_queue_callback


def listen_in_a_thread(r: sr.Recognizer, source, callback, phrase_time_limit=None, timeout=2,
                       chunk_preprocessing=lambda x: x):
    """
    Spawns a thread to repeatedly record phrases from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance and call ``callback`` with that ``AudioData`` instance as soon as each phrase are detected.
    Returns a function object that, when called, requests that the background listener thread stop. The background thread is a daemon and will not stop the program from exiting if there are no other non-daemon threads. The function accepts one parameter, ``wait_for_stop``: if truthy, the function will wait for the background listener to stop before returning, otherwise it will return immediately and the background listener thread might still be running for a second or two afterwards. Additionally, if you are using a truthy value for ``wait_for_stop``, you must call the function from the same thread you originally called ``listen_in_background`` from.
    Phrase recognition uses the exact same mechanism as ``recognizer_instance.listen(source)``. The ``phrase_time_limit`` parameter works in the same way as the ``phrase_time_limit`` parameter for ``recognizer_instance.listen(source)``, as well.
    The ``callback`` parameter is a function that should accept two parameters - the ``recognizer_instance``, and an ``AudioData`` instance representing the captured audio. Note that ``callback`` function will be called from a non-main thread.
    """
    running = [True]

    def threaded_listen():
        """This thread will contantly used the blocking function to listen in the micropohone
        There is only one thread that listens all the time.

        Yo creo que se cala porque hay otros eventos de exception que no estamos contemplando y se ca
        Lo que pasaba era que lo imprimia en otras celdas porque soy un puto idiota.
        """
        with source as s:
            while running[0]:
                try:  # listen for 1 second, then check again if the stop function has been called
                    # print("Listening")
                    audio = listen(
                        r, s, timeout, phrase_time_limit, chunk_preprocessing)
                    # print("Stop listening")

                    if running[0]:
                        callback(r, audio)

                except WaitTimeoutError:  # listening timed out, just try again
                    pass
                    # print("Waiting Timeout Error")

    def stopper(wait_for_stop=True):
        running[0] = False
        if wait_for_stop:
            # block until the background thread is done, which can take around 1 second
            listener_thread.join()

    listener_thread = threading.Thread(target=threaded_listen)
    listener_thread.daemon = True
    listener_thread.start()

    return stopper
