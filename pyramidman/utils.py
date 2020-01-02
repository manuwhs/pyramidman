from os import listdir
from os.path import isfile, join
import os


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


def get_folder_files(folder):
    onlyfiles = [f for f in listdir(folder) if isfile(join(folder, f))]
    return onlyfiles


def create_folder_if_needed(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
