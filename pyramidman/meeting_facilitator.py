from .Seshat import Transcriber
from .speech_commands import SpeechCommandsHandler
from .queue_utils import consumer_process_in_thread
from .utils import create_folder_if_needed
from .Thoth import Papyrus
from .email import Email, EmailConfig
import datetime as dt
from typing import List
from .utils import generate_word_cloud_image

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
            self.date = str(dt.date.today())
        else:
            self.date = date

        self.attendants = attendants
        self.attendants = ["Janina"]

        self.audios_folder = "../meetings/" + meeting_name + "/audios/"
        self.reports_folder = "../meetings/" + meeting_name + "/reports/"

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

        transcriber.set_automatic_high_pass_filter()
        transcriber.recognizer.dynamic_energy_threshold = False
        transcriber.recognizer.energy_threshold*=1.2
    
        transcriber.pause_threshold = 1.0
        transcriber.phrase_threshold = 0.3
        transcriber.non_speaking_duration = 0.8


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

        text = "Dear Egyptian, <br><br>"
        text += "In this email you will find an attached document containing a summary and transcription of the meeting " + self.meeting_name + "<br><br>"
        text += "Stay awesome!"
        email_config.body = text
        email.add_HTML(email_config.body)

        # Generate wordcloud image
        input_image = "../img/pyramidman_logo.jpg"
        output_image = self.reports_folder + "word_cloud.jpg"
        transcription = self.process_transcriptions()

        transcription = """
Thank you everyone for coming here, my name is Manuel, and I have  the humongous pleasure to present to you, for the first time ever, pyramidman. This is a story about civilization, about evolution, but before we proceed.
        
I am sorry already because I am going to radically change your perception of pyramids. But before we introduce what pyramidman is all about, lets think for a second what do pyramids represent in society. Pyramids represent civilization, they represent structure, and most importantly, they represent hierarchy. From Mathematics to Humanities. Going through Gastronomy and Society structures. From Religion to World Domination. Ok, those two are very similar, I could have just said religion. And last but not least, the backbone of our Economic system, pyramid schemes.
        
As we all know, humankind has gone a long way. From the banana tree monkey to the computer monkey. Well diversity has grown a bit, there are two types of computer monkey, Office package monkey and programming monkey. In the early stages, we lived in hunter-gatherer societies. Every individual contributed with their hard skills equally, with hands on skills such as hunting, cooking, nursing…

Over time, as groups grew in size, more complex civilizations appeared, which allowed for specialization of jobs that had not to so much with surviving.
People created well defined Gods and huge infrastructures to please them. But there was another element that is missing from this picture which connected the Populus and the Gods.

The element that made people work like slaves to build the pyramids. Was it belief? Nope, it was middle management. Throughout the ages, the labour became less about physical work and more about mental capabilities. And the middle management evolved accordingly.

Becoming what we see today, a two sided individual that looks cool to the team 
while reporting everything upstarts and making sure the executive boards plans are carried out, waterfall style.

What is the next step? Well, if it wasn’t obvious yet, the next step is pyramidman. pyramidman stands for python robot advisor for middle management. Like any other sotfware, It is just a “tool” to enhance and increase the effectivity of a given sector, in this case middle management.
Completely not intended to replace them in the long run.  

pyramidman is an AI powered middle management tool based on the latest technologies that we all perfectly understand: Python, Deep learning and Blockchain.

Lets have a look at its features. Starting by minutes taking, pyramidman listens to the conversation, and writes it down. At the end of the meeting: It makes a summary and sends it by email. When it listens the magic words.

pyramidman also does meeting facilitation, it sparks the conversation towards value creation. It waits for silences and asks the right questions (every time): How does it scale? Are we asking the right questions? How do we measure success? Is this aligned with our customer journey? Can we take a step back? Are we conflating two different issues here?

pyramidman has programmable voice commands. Forget about Alexa and Google who monitor you and analyze everything you say 24/7. And they can only tell you the weather and play music. With pyramidman you can customize your own voice commands. i.e: pyramidman facilitate meeting

pyramidman also does business talk translation, keep up with the latest business slang.  There is so much potential here means You guys did an awful job and that is why you need us. As per my last email is read the fuck*** thread
Our strategy is to increase our revenue streams and cut down our costs. We have no idea why benefits are down, some people might get fired. Thank you for your input, we will take it into account. Shut up and look pretty We leverage on the opportunities of market arbitrage. We take advantage of poorer countries.  Leveraging versatile skills in analytics, statistics, business, and economics for data driven insights is Bullshit.

pyramidman is your own business advisor, walking you through ten cases.
Pretty much like AI dungeon with business baby steps. 

pyramidman includes innovation mode a.k.a brainstorming. Store all the ideas in the cloud using Blockchain with your company copyright. Optional:  Online bot that will track the original owner for life. If they developed on an idea remotely close, it prepares an automatic lawsuit.

pyramidman detects its own sentences and assigns pyramid-points to the speakers. Handy when you need to promote some employee. Failing upwards had never been this easy!

is this a joke? Why did you spend so much time on this stupid presentation? Well maybe, or maybe... is this a github repo? Recording studio? And most importantly, is it on right now? pyramidman facilitate.

Well, this presentation is almost over and as I said, pyramidman sends an email at the end of the meeting when it hears the magic words. Who wants coffee?

        """
        generate_word_cloud_image(input_image,transcription, output_image)

        self.make_report()
        email.add_image(output_image)
        email.add_file(self.reports_folder + "report.docx")

        email.send_email()

    def make_report(self):
        papyrus = Papyrus(self.meeting_name, report_type="meeting",
                          date=self.date, attendants=self.attendants)

        transcription = self.process_transcriptions()
        transcription = """
Thank you everyone for coming here, my name is Manuel, and I have  the humongous pleasure to present to you, for the first time ever, pyramidman. This is a story about civilization, about evolution, but before we proceed.
        
I am sorry already because I am going to radically change your perception of pyramids. But before we introduce what pyramidman is all about, lets think for a second what do pyramids represent in society. Pyramids represent civilization, they represent structure, and most importantly, they represent hierarchy. From Mathematics to Humanities. Going through Gastronomy and Society structures. From Religion to World Domination. Ok, those two are very similar, I could have just said religion. And last but not least, the backbone of our Economic system, pyramid schemes.
        
As we all know, humankind has gone a long way. From the banana tree monkey to the computer monkey. Well diversity has grown a bit, there are two types of computer monkey, Office package monkey and programming monkey. In the early stages, we lived in hunter-gatherer societies. Every individual contributed with their hard skills equally, with hands on skills such as hunting, cooking, nursing…

Over time, as groups grew in size, more complex civilizations appeared, which allowed for specialization of jobs that had not to so much with surviving.
People created well defined Gods and huge infrastructures to please them. But there was another element that is missing from this picture which connected the Populus and the Gods.

The element that made people work like slaves to build the pyramids. Was it belief? Nope, it was middle management. Throughout the ages, the labour became less about physical work and more about mental capabilities. And the middle management evolved accordingly.

Becoming what we see today, a two sided individual that looks cool to the team 
while reporting everything upstarts and making sure the executive boards plans are carried out, waterfall style.

What is the next step? Well, if it wasn’t obvious yet, the next step is pyramidman. pyramidman stands for python robot advisor for middle management. Like any other sotfware, It is just a “tool” to enhance and increase the effectivity of a given sector, in this case middle management.
Completely not intended to replace them in the long run.  

pyramidman is an AI powered middle management tool based on the latest technologies that we all perfectly understand: Python, Deep learning and Blockchain.

Lets have a look at its features. Starting by minutes taking, pyramidman listens to the conversation, and writes it down. At the end of the meeting: It makes a summary and sends it by email. When it listens the magic words.

pyramidman also does meeting facilitation, it sparks the conversation towards value creation. It waits for silences and asks the right questions (every time): How does it scale? Are we asking the right questions? How do we measure success? Is this aligned with our customer journey? Can we take a step back? Are we conflating two different issues here?

pyramidman has programmable voice commands. Forget about Alexa and Google who monitor you and analyze everything you say 24/7. And they can only tell you the weather and play music. With pyramidman you can customize your own voice commands. i.e: pyramidman facilitate meeting

pyramidman also does business talk translation, keep up with the latest business slang.  There is so much potential here means You guys did an awful job and that is why you need us. As per my last email is read the fuck*** thread
Our strategy is to increase our revenue streams and cut down our costs. We have no idea why benefits are down, some people might get fired. Thank you for your input, we will take it into account. Shut up and look pretty We leverage on the opportunities of market arbitrage. We take advantage of poorer countries.  Leveraging versatile skills in analytics, statistics, business, and economics for data driven insights is Bullshit.

pyramidman is your own business advisor, walking you through ten cases.
Pretty much like AI dungeon with business baby steps. 

pyramidman includes innovation mode a.k.a brainstorming. Store all the ideas in the cloud using Blockchain with your company copyright. Optional:  Online bot that will track the original owner for life. If they developed on an idea remotely close, it prepares an automatic lawsuit.

pyramidman detects its own sentences and assigns pyramid-points to the speakers. Handy when you need to promote some employee. Failing upwards had never been this easy!

is this a joke? Why did you spend so much time on this stupid presentation? Well maybe, or maybe... is this a github repo? Recording studio? And most importantly, is it on right now? pyramidman facilitate.

Well, this presentation is almost over and as I said, pyramidman sends an email at the end of the meeting when it hears the magic words. Who wants coffee?

        """

        papyrus.set_transcription(transcription)
        papyrus.word_cloud_image_path = self.reports_folder + "word_cloud.jpg"
        papyrus.create_document(self.reports_folder + "report.docx")

    def process_transcriptions(self):
        """Process the transcriptions and creates a joint document. It basically joins the words
        and hopefully adds commas and dots properly (and uppercases) properly.

        We can write it properly according to times:
        - short sentences -> coma
        - long sentence -> finish with .
        - long silence -> New line
        - Remove intelligle based on confidence or content.
        """

        all_text = ""
        for transcription in self._trainscriptions_list:
            if (transcription["sentence"]!= "i") and (transcription["sentence"]!="a"):

                all_text += transcription["sentence"].capitalize() + ". "

        return all_text


    def add_meeting_commands_handlers(self):

        summary_email = {"name": "summary_email",
                         "sentences": ["who wants coffee"],
                         "function": self.send_meeting_summary_email,
                         "args": None}

        self.speech_command_handler.add_command(summary_email)
