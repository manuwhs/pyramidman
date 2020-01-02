from .Seshat import Transcriber
from .speech_commands import SpeechCommandsHandler
from .queue_utils import consumer_process_in_thread


class MeetingFacilitator():
    """Class to handle the logic of meeting facilitation.
    It basically initializes some basic information about the meeting, and then 
    - It starts the listening in a new thread. 
    - The sentences recorded are then transcribed by another thread.
    - If an event is triggered: (i.e command or long silence), another thread is created to handle it.
    """

    def __init__(self, meeting_name):
        self.meeting_name = meeting_name

        self.transcriber = None
        self.speech_command_handler = None

        self._stop_command_handler_in_background_func = None
        self._is_handling_commands = False

    def set_automatic_default_transcriber(self):
        transcriber = Transcriber()
        transcriber.set_automatic_default_recording_variables(
            recordings_folder="../audios/temp/")
        transcriber.set_automatic_default_transcribing_variables()
        self.transcriber = transcriber

    def set_default_speech_command_handler(self):
        speech_command_handler = SpeechCommandsHandler(mode="active")
        self.speech_command_handler = speech_command_handler

    def start_command_handler_in_thread(self):
        """Creates a consumer thread that reads in the transcriptions and executes the 
        corresponding commands
        """
        def command_consumer(x): return self.speech_command_handler.process(x["sentence"])
        self._stop_command_handler_in_background_func = consumer_process_in_thread(
            self.transcriber.get_transcriptions_queue(), command_consumer)
        self._is_handling_commands = True

    def stop_command_handler_in_thread(self):
        """Creates a consumer thread that reads in the transcriptions and executes the 
        corresponding commands
        """
        self._stop_command_handler_in_background_func()
        self._is_handling_commands = False

    def start(self):
        """It starts listening and transcribing 
        """
        self.transcriber.start_listening_in_background(
            phrase_time_limit=30, timeout=0)
        self.transcriber.start_transcribing_in_background()
        self.start_command_handler_in_thread()

    def stop(self):
        """Maybe we need to stop them from end to beginning to avoid locks?
        """
        self.stop_command_handler_in_thread()
        self.transcriber.stop_transcribing_in_background()
        self.transcriber.stop_listening_in_background()
