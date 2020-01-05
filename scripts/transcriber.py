from pyramidman.audio_parameters import AudioParameters
from pyramidman.basic_audio_IO import play_audio
from pyramidman.deepspeech_tools import DeepSpeechArgs, transcribe
import sys

import argparse
import pickle
import json

def main(args):
    parser = argparse.ArgumentParser(description='Transcribe long audio files using webRTC VAD or use the streaming interface')
    parser.add_argument('--aggressive', type=int, choices=range(4), required=False,
                        help='Determines how aggressive filtering out non-speech is. (Interger between 0-3)')
    parser.add_argument('--audio', required=False,
                        help='Path to the audio file to run (WAV format)')

    args = parser.parse_args()

    deepspeech_args = DeepSpeechArgs()

    transcription = transcribe(deepspeech_args, args.audio)

    # not pickleable or jsonable
    del transcription["characters"]

    print(json.dumps(transcription))
    #print(json.dumps(transcription))  


if __name__ == '__main__':
    main(sys.argv[1:])