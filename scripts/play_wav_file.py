from pyramidman.audio_parameters import AudioParameters
from pyramidman.basic_audio_IO import play_audio

audio_params = AudioParameters()
audio_params.set_sysdefault_microphone_index()
audio_params.set_default_input_parameters()
filepath  = "../audios/standard/sep.wav"
play_audio(audio_params, filepath)
