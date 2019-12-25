
import speech_recognition as sr
import pyaudio
from .audio_parameters import AudioParameters



def recognizer_func(recognizer: sr.Recognizer, audio: sr.AudioData):
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        print("Decoding")
        print("Google Speech Recognition thinks you said:  " + recognizer.recognize_sphinx(audio))

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


def recognize_speech_from_mic(audio_params: AudioParameters, duration: float = 3):
    """Transcribe speech from recorded from a microphone generated from an object
    of the AudioParameters class.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """
    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone

    mic = audio_params.get_microphone()
    recognizer = sr.Recognizer()

    with mic as source:
        # analyze the audio source for 1 second
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.record(source, duration=duration)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #   update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_sphinx(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable/unresponsive"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response
