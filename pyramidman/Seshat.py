import queue
from .audio_parameters import AudioParameters
from .audio_utils import calibrate_microphone
from .queue_utils import listen, listen_in_a_thread, put_data_in_queue_closure, consumer_process_in_thread
import speech_recognition as sr
from .deepspeech_tools import transcribe,  DeepSpeechArgs


class Transcriber:
    """Class that transcribes the information.
    It constains all the information necesary to listen to sentences 
    and store them in a queue, and transcribe them and make the transcriptions
    available.
    """

    def __init__(self):
        # Internal variables
        self._listening = False
        self._transcribing = False

        self._audios_queue = queue.Queue()
        self._transcriptions_queue = queue.Queue()

        self._stop_listen_in_background_func = None
        self._stop_transcribing_in_background_func = None

        self.item_index = 0
        # Tuple, time, metadata.the Maybe priority queue.
        self._transcriptions = []

    """ Getting methods"""

    def get_audios_queue(self):
        return self._audios_queue

    def get_transcriptions_queue(self):
        return self._transcriptions_queue

    """ Setting methods"""

    def set_recording_variables(self, recordings_folder, audio_parameters,
                                microphone, audio_filter, recognizer):
        self.recordings_folder = recordings_folder
        self.audio_parameters = audio_parameters

        self.microphone = microphone
        self.audio_filter = audio_filter
        self.recognizer = recognizer

    def set_transcriber(self, transcriber):
        self.transcriber = transcriber

    def set_automatic_default_recording_variables(self, recordings_folder="../audios/temp/"):
        # Set everything automatically
        self.recordings_folder = recordings_folder

        audio_params = AudioParameters()
        audio_params.set_sysdefault_microphone_index()
        audio_params.set_default_input_parameters()

        mic = audio_params.get_microphone()
        r = sr.Recognizer()

        calibrate_microphone(mic, r, duration=1, warmup_duration=3)

        self.audio_params = audio_params
        self.microphone = mic
        self.recognizer = r
        self.audio_filter = lambda x: x

    def set_automatic_default_transcribing_variables(self):
        # Set everything automatically
        args = DeepSpeechArgs()
        def transcriber(x): return transcribe(args, x)
        self.transcriber = transcriber

    """ LISTENING METHODS """

    def is_listening(self):
        return self._listening

    def start_listening_in_background(self, phrase_time_limit=20, timeout=5):
        if self.is_listening():
            print("Already listening")
        else:
            self._audios_queue = queue.Queue()

            def processing_audio(audio):
                """ This function stores the audio in disk and returns the created filename"""
                filename_audio = f'{self.recordings_folder}{self.item_index}.wav'
                with open(filename_audio, "wb") as f:
                    f.write(audio.get_wav_data())
                self.item_index += 1
                return filename_audio

            put_audio_data_in_queue_callback = put_data_in_queue_closure(
                self._audios_queue, processing_audio)
            self._stop_listen_in_background_func = listen_in_a_thread(
                self.recognizer, self.microphone, put_audio_data_in_queue_callback, phrase_time_limit, timeout, self.audio_filter)
            self._listening = True

    def stop_listening_in_background(self, wait_for_stop=True):
        if self.is_listening():
            self._stop_listen_in_background_func(wait_for_stop)
            # self._audios_queue = None
            self._listening = False
        else:
            print("We are not listening")

    """ TRANSCRIBING METHODS """

    def is_transcribing(self):
        return self._transcribing

    def transcribe(self, audio):
        """This function just transcribes what is being given as input
        """
        return self.transcriber(audio)

    def start_transcribing_in_background(self):
        """This function transcribes the audios in the queue and writes the transcriptions to another queue.
        That queue will be analyzed by the main thread to decide what to do.
        - It takes them from the internal audios_queue

        """
        if self.is_transcribing():
            print("Already transcribing")
        else:
            self._transcriptions_queue = queue.Queue()
            put_transcriptions_in_queue_callback = put_data_in_queue_closure(
                self._transcriptions_queue, self.transcriber)
            self._stop_transcribing_in_background_func = consumer_process_in_thread(
                self._audios_queue, put_transcriptions_in_queue_callback)
            self._transcribing = True

    def stop_transcribing_in_background(self, wait_for_stop=True):
        if self.is_transcribing():
            self._stop_transcribing_in_background_func(wait_for_stop)
            # self._transcriptions_queue = None
            self._transcribing = False
        else:
            print("We are not listening")
