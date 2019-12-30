#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import argparse
import numpy as np
import shlex
import subprocess
import sys
import wave
import json

from deepspeech import Model, printVersions
from timeit import default_timer as timer

try:
    from shhlex import quote
except ImportError:
    from pipes import quote


class DeepSpeechArgs():

    def __init__(self, folder="../models/deepspeech/"):
        self.model = folder + "deepspeech-0.6.0-models/output_graph.pbmm"
        self.lm = folder + "deepspeech-0.6.0-models/lm.binary"
        self.trie = folder + "deepspeech-0.6.0-models/trie"

        self.beam_width = 500
        self.lm_alpha = 0.75
        self.lm_beta = 1.85


def convert_samplerate(audio_path, desired_sample_rate):
    sox_cmd = 'sox {} --type raw --bits 16 --channels 1 --rate {} --encoding signed-integer --endian little --compression 0.0 --no-dither - '.format(
        quote(audio_path), desired_sample_rate)
    try:
        output = subprocess.check_output(
            shlex.split(sox_cmd), stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError('SoX returned non-zero status: {}'.format(e.stderr))
    except OSError as e:
        raise OSError(e.errno, 'SoX not found, use {}hz files or install it: {}'.format(
            desired_sample_rate, e.strerror))

    return desired_sample_rate, np.frombuffer(output, np.int16)


def metadata_to_string(metadata):
    return ''.join(item.character for item in metadata.items)


def words_from_metadata(metadata):
    word = ""
    word_list = []
    word_start_time = 0

    # Loop through each character
    for i in range(0, metadata.num_items):
        item = metadata.items[i]
        # Append character to word if it's not a space
        if item.character != " ":
            word = word + item.character
            if len(word) == 1:
                # Log the start time of the new word
                word_start_time = item.start_time

        # Word boundary is either a space or the last character in the array
        if item.character == " " or i == metadata.num_items - 1:
            word_duration = item.start_time - word_start_time

            if word_duration < 0:
                word_duration = 0

            each_word = dict()
            each_word["word"] = word
            each_word["start_time "] = round(word_start_time, 4)
            each_word["duration"] = round(word_duration, 4)

            word_list.append(each_word)
            # Reset
            word = ""
            word_start_time = 0

    return word_list


def metadata_json_output(metadata):
    json_result = dict()
    json_result["words"] = words_from_metadata(metadata)
    json_result["confidence"] = metadata.confidence
    return json.dumps(json_result)


class VersionAction(argparse.Action):
    def __init__(self, *args, **kwargs):
        super(VersionAction, self).__init__(nargs=0, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        printVersions()
        exit(0)


def transcribe(args, filepath="audio/2830-3980-0043.wav", verbose=0):

    if verbose > 0:
        print('Loading model from file {}'.format(args.model), file=sys.stderr)
        model_load_start = timer()
    ds = Model(args.model, args.beam_width)
    if verbose > 0:
        model_load_end = timer() - model_load_start
        print('Loaded model in {:.3}s.'.format(
            model_load_end), file=sys.stderr)

    desired_sample_rate = ds.sampleRate()
    if args.lm and args.trie:
        if verbose > 0:
            print('Loading language model from files {} {}'.format(
                args.lm, args.trie), file=sys.stderr)
            lm_load_start = timer()
        ds.enableDecoderWithLM(args.lm, args.trie, args.lm_alpha, args.lm_beta)
        if verbose > 0:
            lm_load_end = timer() - lm_load_start
            print('Loaded language model in {:.3}s.'.format(
                lm_load_end), file=sys.stderr)

    fin = wave.open(filepath, 'rb')
    fs = fin.getframerate()
    if fs != desired_sample_rate:
        if verbose > 0:
            print('Warning: original sample rate ({}) is different than {}hz. Resampling might produce erratic speech recognition.'.format(
                fs, desired_sample_rate), file=sys.stderr)
        fs, audio = convert_samplerate(filepath, desired_sample_rate)
    else:
        audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)

    audio_length = fin.getnframes() * (1/fs)
    fin.close()

    if verbose > 0:
        print('Running inference.', file=sys.stderr)
        inference_start = timer()
    audio_metadata = ds.sttWithMetadata(audio)
    if verbose > 0:
        inference_end = timer() - inference_start
        print('Inference took %0.3fs for %0.3fs audio file.' %
              (inference_end, audio_length), file=sys.stderr)

    dict_result = dict()
    dict_result["sentence"] = "".join(
        item.character for item in audio_metadata.items)
    dict_result["words"] = words_from_metadata(audio_metadata)
    dict_result["characters"] = audio_metadata
    dict_result["confidence"] = audio_metadata.confidence

    return dict_result
