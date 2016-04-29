from __future__ import division

import nltk
from PIL import Image, ImageDraw, ImageFont

import os
import sys
from collections import namedtuple

Element = namedtuple('Element', ['token', 'tag'])


def layout(sentence):
    all_lines = []
    text = sentence.strip()
    tokens = nltk.word_tokenize(text)
    tagged_tokens = nltk.pos_tag(tokens)
    line = []
    for token, tag in tagged_tokens:
        if token == 'i':
            # should probably be uppercase
            token = 'I'
        element = Element(token, tag)
        if tag.startswith('JJ') or (tag == 'PRP' and line and line[-1].tag != 'CC'):
            # adjective, start on new line
            if line:
                all_lines.append(' '.join(e.token for e in line))
                line = []
            line.append(element)
        elif tag.startswith('NN'):
            # noun, end line if prefixed by adjective, otherwise put on single
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


def create_image(layout):
    img = Image.new('RGB', (1000, 1750))
    draw = ImageDraw.Draw(img)
    font_size = 100
    offset = 0
    font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    font_location = os.path.join(font_dir, 'DroidSansMono.ttf')
    font = ImageFont.truetype(font_location, font_size)
    width,height = draw.textsize('h', font=font)
    size_to_width_ratio = font_size/width
    size_to_height_ratio = font_size/height
    for line in layout:
        font_size = 1000/len(line)*size_to_width_ratio
        font = ImageFont.truetype(font_location, int(font_size))
        draw.text((0, offset), line.upper(), font=font, fill=(255, 255, 255))
        offset += font_size / size_to_height_ratio
    img.save('testimg.png')
    img.show()


def main():
    with open('sample-texts.txt') as fh:
        for text in fh:
            lines = layout(text)
            print '\n'.join(lines)

if __name__ == '__main__':
    sentence = ' '.join(sys.argv[1:])
    create_image(layout(sentence))
    # main()
