from .Seshat import Transcriber
from .speech_commands import SpeechCommandsHandler
from .queue_utils import consumer_process_in_thread
from .utils import create_folder_if_needed
from pyramidman.Thoth import Papyrus
from pyramidman.email import Email, EmailConfig
import datetime as dt
from typing import List


class MeetingFacilitator():
    """Class to handle the logic of meeting facilitation.
    It basically initializes some basic information about the meeting, and then
    - It starts the listening in a new thread.
    - The sentences recorded are then transcribed by another thread.
    - If an event is triggered: (i.e command or long silence), another thread is created to handle it.
    """

    def __init__(self, meeting_name,  date: str = None, attendants: List[str] = None):

        self.meeting_name = meeting_name

        if date is None:
            self.date = str(dt.datetime.now())
        else:
            self.date = date

        self.attendants = attendants

        self.audios_folder = "../meetings/" + meeting_name + "/audios/"
        self.reports_folder = "..meetings/" + meeting_name + "/reports/"

        create_folder_if_needed(self.reports_folder)
        create_folder_if_needed(self.audios_folder)

        self.transcriber = None
        self.speech_command_handler = None

        self._stop_command_handler_in_background_func = None
        self._is_handling_commands = False

        # It will hold all the transcriptions for further processing
        self._trainscriptions_list = []

    def set_automatic_default_transcriber(self):
        transcriber = Transcriber()
        transcriber.set_automatic_default_recording_variables(
            recordings_folder=self.audios_folder)
        transcriber.set_automatic_default_transcribing_variables()
        self.transcriber = transcriber

    def set_default_speech_command_handler(self):
        speech_command_handler = SpeechCommandsHandler(mode="active")
        self.speech_command_handler = speech_command_handler
        self.add_meeting_commands_handlers()

    def set_email_config(self, email_config):
        self.email_config = email_config

    """ Starting Actions"""

    def start_command_handler_in_thread(self):
        """Creates a consumer thread that reads in the transcriptions and executes the
        corresponding commands
        """
        def command_consumer(x):
            self._trainscriptions_list.append(x)
            return self.speech_command_handler.process(x["sentence"])
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
            phrase_time_limit=15, timeout=0)
        self.transcriber.start_transcribing_in_background()
        self.start_command_handler_in_thread()

    def stop(self):
        """Maybe we need to stop them from end to beginning to avoid locks?
        """
        self.stop_command_handler_in_thread()
        self.transcriber.stop_transcribing_in_background()
        self.transcriber.stop_listening_in_background()

    def send_meeting_summary_email(self):
        email_config = self.email_config
        email = Email(email_config.user, email_config.pwd,
                      email_config.recipients)
        email.create_msgRoot(subject=email_config.subject)
        email.add_HTML(email_config.body)

        self.make_report()
        email.add_file(self.reports_folder + "report.docx")

        email.send_email()

    def make_report(self):
        papyrus = Papyrus(self.meeting_name, report_type="meeting",
                          date=self.date, attendants=self.attendants)

        transcription = self.process_transcriptions()
        papyrus.set_transcription(transcription)
        papyrus.create_document(self.reports_folder + "report.docx")

    def process_transcriptions(self):
        """Process the transcriptions and creates a joint document. It basically joins the words
        and hopefully adds commas and dots properly (and uppercases) properly.
        """

        all_text = ""
        for transcription in self._trainscriptions_list:
            all_text += transcription["sentence"].capitalize() + "."

        return all_text

    def add_meeting_commands_handlers(self):

        summary_email = {"name": "summary_email",
                         "sentences": ["who wants coffee"],
                         "function": self.send_meeting_summary_email,
                         "args": None}

        self.speech_command_handler.add_command(summary_email)
