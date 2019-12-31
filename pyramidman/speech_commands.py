
from random import randint
from .basic_audio_IO import play_audio  
from .utils import  get_folder_files
from .audio_parameters import AudioParameters

def process_command(command):
    function = command["function"]
    args = command["args"]
    function(*args)


def is_command_detected(command, sentence):
    for command_sentence in command["sentences"]:
        index_start_command = sentence.find(command_sentence)
        if index_start_command >= 0:
            return index_start_command

    return False


def play_generic_sentence(audio_params, folder="../audios/temp/"):
    """Plays a .wav file from the given folder, selected at random.
    """
    print("playing")
    files_in_folder = get_folder_files(folder)
    file_to_play = folder + files_in_folder[randint(0, len(files_in_folder))]
    play_audio(audio_params, file_to_play)


class SpeechCommandsHandler():

    def __init__(self, mode = "active"):
        self.keyword = "pyramid man"
        self.mode = mode    # "silent"
        self.commands = []
        self.add_custom_commands()

    def add_command(self, command):
        self.commands.append(command)

    def add_custom_commands(self):
        music_player = {"name": "music_player",
                        "sentences": ["play music"],
                        "function": play_generic_sentence,
                        "args": [AudioParameters()]}
        self.add_command(music_player)

    def is_keyword_detected(self, sentence):
        index_start_keyword = sentence.find(self.keyword)
        if index_start_keyword > 0:
            return index_start_keyword
        return False

    def process(self, sentence):
        if self.mode == "active":
            if self.is_keyword_detected(sentence):
                print("keyword detected")
                for command in self.commands:
                    if is_command_detected(command, sentence):
                        # TODO: Create thread and put the sentence there.
                        process_command(command)


