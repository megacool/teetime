from __future__ import division

import nltk
import tempfile
import wikipedia
import random
import requests
from PIL import Image, ImageDraw, ImageFont

import os
import sys
import warnings
from collections import namedtuple

from .colors import dominant_colors

warnings.simplefilter("ignore")


Element = namedtuple('Element', ['token', 'tag'])

def create_typography(sentence, colors=True):
    layout = _layout(sentence)
    return create_image(layout, colors=colors)


def _layout(sentence):
    all_lines = []
    text = sentence.strip()
    tagged_tokens = nltk.pos_tag(text.split())
    line = []
    for token, tag in tagged_tokens:
        if token == 'i':
            # should probably be uppercase
            token = 'I'
        element = Element(token, tag)
        previous_adverb = line and line[-1].tag == 'RB'
        adverb_adjective = tag.startswith('JJ') and not previous_adverb
        pronoun = tag == 'PRP' and line and line[-1].tag not in ('IN', 'CC')
        previous_to = line and line[-1].tag == 'TO'
        if (adverb_adjective) or pronoun or tag == 'CC' or tag == 'TO':
            # start on new line
            if line:
                all_lines.append(' '.join(e.token for e in line))
                line = []
            line.append(element)
        elif tag.startswith('JJ') and previous_adverb:
            # end line
            line.append(element)
            all_lines.append(' '.join(e.token for e in line))
            line = []
        elif tag.startswith('VB') and previous_to:
            # end line
            line.append(element)
            all_lines.append(' '.join(e.token for e in line))
            line = []
        elif tag.startswith('NN'):
            # end line if prefixed by adjective, otherwise put on single
            if line and line[-1].tag.startswith('JJ'):
                line.append(element)
                all_lines.append(' '.join(e.token for e in line))
                line = []
            else:
                if line:
                    all_lines.append(' '.join(e.token for e in line))
                line = [element]
        elif tag == ',':
            if line:
                line[-1] = Element(line[-1].token + ',', line[-1].tag)
        else:
            line.append(element)

    if line:
        all_lines.append(' '.join(e.token for e in line))
    return all_lines


def create_image(layout, colors=True):
    font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    font_location = os.path.join(font_dir, 'MinstrelPosterNF.ttf')

    desired_width = 1000
    bottom_margin = 50
    height = get_total_height_of_image(desired_width, layout, font_location)

    img = Image.new('RGB', (desired_width, height + bottom_margin))
    draw = ImageDraw.Draw(img)
    offset = 0
    for line in layout:
        font, height = get_font_for_line_of_width(line, font_location, desired_width)
        color = (255, 255, 255)
        if len(line.split()) == 1 and colors:
            _color = get_colors_for_word(line, 1)
            if _color:
                color = tuple(_color[0])
                print 'Setting color of %s to %s' % (line, color)
        draw.text((0, offset), line, font=font, fill=color)
        offset += height
    image_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(image_file, 'png')
    return image_file.name


def get_total_height_of_image(width, layout, font_location):
    height = 0
    for line in layout:
        _, line_height = get_font_for_line_of_width(line, font_location, width)
        height += line_height
    return int(height)


def get_font_for_line_of_width(line, font_location, desired_width):
    image = Image.new('RGB', (10, 10))
    draw = ImageDraw.Draw(image)
    test_font_size = 100
    font = ImageFont.truetype(font_location, test_font_size)
    width, height = draw.textsize(line, font=font)
    size_to_width_ratio = test_font_size/width
    font_size = desired_width*size_to_width_ratio
    resulting_height = font_size/(test_font_size/height)
    font = ImageFont.truetype(font_location, int(font_size))
    return (font, resulting_height)


def get_colors_for_word(word, n=3, recurse=True):
    try:
        result = wikipedia.page(word)
    except wikipedia.exceptions.DisambiguationError as exception:
        # print 'Ambiguous word, alternatives were: %s' % exception.options
        if recurse:
            options = exception.options
            random.shuffle(options)
            for alternative in options:
                print 'Trying %s' % alternative
                color = get_colors_for_word(alternative, recurse=False)
                if color:
                    return color
        return None
    except wikipedia.exceptions.PageError as exception:
        return None

    images = result.images

    if not images:
        return None

    image = get_acceptable_image(images)
    if not image:
        return None
    min_image_size = 5*2**10
    response = requests.get(image, stream=True)
    response.raise_for_status()
    image_size = response.headers['content-length']
    if image_size < min_image_size:
        return None

    image_extension = image.rsplit('.', 1)[1]
    image_file = tempfile.NamedTemporaryFile(suffix='.%s' % image_extension, delete=False)
    with image_file as fh:
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                fh.write(chunk)

    img = Image.open(image_file.name)
    colors = dominant_colors(img, n)
    os.remove(image_file.name)
    return colors


def get_acceptable_image(images):
    for image in images:
        image_extension = image.rsplit('.', 1)[1]
        if image_extension in ('jpg', 'png'):
            return image
