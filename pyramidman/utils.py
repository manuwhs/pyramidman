from os import listdir
from os.path import isfile, join
import os
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image
import numpy as np


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

def generate_word_cloud_image(input_image, text, output_image):
    """ Create that word cloud broh"""
    mask = np.array(Image.open(input_image))
    # stopwords=stopwords,
    wordcloud = WordCloud( background_color="white", max_words=1000, mask=mask).generate(text)

    image_colors = ImageColorGenerator(mask)
    wordcloud.recolor(color_func=image_colors)
    wordcloud.to_file(output_image)