import audioop
import collections
import math

import speech_recognition as sr
from speech_recognition import WaitTimeoutError

import datetime as dt 

def is_timeout_expired(timeout, elapsed_time):
    # handle waiting too long for phrase by raising an exception
    if timeout and elapsed_time > timeout:
        raise WaitTimeoutError(
            "listening timed out while waiting for phrase to start")


def is_speaking_detected(r, source, buffer):
    """ detect whether speaking has started on audio input
    energy of the audio signal
    Compute the root of the mean power of the signal.
    This is the mean power of the buffer so far.
    """
    energy = audioop.rms(buffer, source.SAMPLE_WIDTH)
    return energy > r.energy_threshold


def update_energy_threshold(r, source, buffer, seconds_per_buffer):
    # account for different chunk sizes and rates
    # dynamically adjust the energy threshold using asymmetric weighted average
    energy = audioop.rms(buffer, source.SAMPLE_WIDTH)
    damping = r.dynamic_energy_adjustment_damping ** seconds_per_buffer
    target_energy = energy * r.dynamic_energy_ratio
    r.energy_threshold = r.energy_threshold * \
        damping + target_energy * (1 - damping)


# Create a counter in a beautiful way.
def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


@static_vars(count=0)
def pause_counter(r, buffer, source):
    # check if speaking has stopped for longer than the pause threshold on the audio input
    # unit energy of the audio signal within the buffer
    energy = audioop.rms(buffer, source.SAMPLE_WIDTH)
    if energy > r.energy_threshold:
        pause_counter.count = 0
    else:
        pause_counter.count += 1

    return pause_counter.count    # end of the phrase


def listen(r: sr.Recognizer, source: sr.Microphone,
           timeout=None, phrase_time_limit=None,
           chunk_preprocessing=lambda x: x):
    """
    Blocking function 

    Records a single phrase from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance, which it returns.

    This is done by waiting until the audio has an energy above ``recognizer_instance.energy_threshold`` (the user has started speaking), and then recording until it encounters ``recognizer_instance.pause_threshold`` seconds of non-speaking or there is no more audio input. The ending silence is not included.

    The ``timeout`` parameter is the maximum number of seconds that this will wait for a phrase to start before giving up and throwing an ``speech_recognition.WaitTimeoutError`` exception. If ``timeout`` is ``None``, there will be no wait timeout.

    The ``phrase_time_limit`` parameter is the maximum number of seconds that this will allow a phrase to continue before stopping and returning the part of the phrase processed before the time limit was reached. The resulting audio will be the phrase cut off at the time limit. If ``phrase_timeout`` is ``None``, there will be no phrase time limit.

    This operation will always complete within ``timeout + phrase_timeout`` seconds if both are numbers, either by returning the audio data, or by raising a ``speech_recognition.WaitTimeoutError`` exception.
    """
    assert isinstance(source, sr.AudioSource), "Source must be an audio source"
    assert source.stream is not None, "Audio source must be entered before listening, see documentation for ``AudioSource``; are you using ``source`` outside of a ``with`` statement?"
    assert r.pause_threshold >= r.non_speaking_duration >= 0

    # A buffer is one of the chunks
    seconds_per_buffer = float(source.CHUNK) / source.SAMPLE_RATE

    # Number of buffers (chunks) of non-speaking audio during a phrase,
    # before the phrase should be considered complete.
    pause_buffer_count = int(math.ceil(r.pause_threshold / seconds_per_buffer))

    # minimum number of buffers of speaking audio before we consider the speaking audio a phrase
    phrase_buffer_count = int(
        math.ceil(r.phrase_threshold / seconds_per_buffer))

    # maximum number of buffers of non-speaking audio to retain before and after a phrase
    non_speaking_buffer_count = int(
        math.ceil(r.non_speaking_duration / seconds_per_buffer))

    # read audio input for phrases until there is a phrase that is long enough
    elapsed_time = 0  # number of seconds of audio read
    buffer = b""  # an empty buffer means that the stream has ended and there is no data left to read

    while True:
        frames = collections.deque()

        # store audio input until the phrase starts
        while True:
            # Read the data from the buffer.
            # It needs to be read in blocking mode apparently.
            # Maybe the micro puts the data all the time in a buffer and we read from it.
            buffer = source.stream.read(source.CHUNK)
            if len(buffer) == 0:
                t_start = dt.datetime.now()
                break  # reached end of the stream (we process it fa)

            buffer = chunk_preprocessing(buffer)
            # Add the time to the acculated time and append the new data to the accumulation
            elapsed_time += seconds_per_buffer
            frames.append(buffer)

            is_timeout_expired(timeout, elapsed_time)

            # ensure we only keep the needed amount of non-speaking buffers
            if len(frames) > non_speaking_buffer_count:
                frames.popleft()
            if is_speaking_detected(r, source, buffer):
                t_start = dt.datetime.now()
                break
            if r.dynamic_energy_threshold:
                update_energy_threshold(r, source, buffer, seconds_per_buffer)

        # read audio input until the phrase ends
        pause_count, phrase_count = 0, 0
        phrase_start_time = elapsed_time

        while True:
            buffer = source.stream.read(source.CHUNK)
            if len(buffer) == 0:
                break  # reached end of the stream
            buffer = chunk_preprocessing(buffer)
            elapsed_time += seconds_per_buffer
            phrase_count += 1
            frames.append(buffer)

            if phrase_time_limit and elapsed_time - phrase_start_time > phrase_time_limit:
                break
            pause_count = pause_counter(r, buffer, source)

            if pause_count > pause_buffer_count:
                break

        # check how long the detected phrase is, and retry listening if the phrase is too short
        phrase_count -= pause_count  # exclude the buffers for the pause before the phrase
        if phrase_count >= phrase_buffer_count or len(buffer) == 0:
            break  # phrase is long enough or we've reached the end of the stream, so stop listening

    # obtain frame data
    for i in range(pause_count - non_speaking_buffer_count):
        frames.pop()  # remove extra non-speaking frames at the end
    frame_data = b"".join(frames)

    return sr.AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
