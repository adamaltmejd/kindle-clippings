#!/usr/local/bin/python
# -*- coding: utf-8 -*-

"""
Kindle Clippings converter.

Fork of (https://github.com/lxyu/kindle-clippings)

This script will fetch My Clippings data and output it into different txt files
for each book.
"""

import collections
import json
import os
from datetime import datetime

BOUNDARY = u"==========\r\n"
DATA_FILE = u"clips.json"
INPUT_FILE = u"My Clippings.txt"
OUTPUT_DIR = u"output"


def get_sections(filename):
    """Read the sections, split by BOUNDARY."""
    with open(filename, 'r') as f:
        content = f.read().decode('utf-8')

    content = content.replace(u'\ufeff', u'') # remove BOM char
    return filter(None, content.split(BOUNDARY)) # filter out empty lines


def get_clip(section):
    """Fetch each clip."""
    clip = {}

    lines = [l.strip() for l in section.splitlines() if l]

    try:
        pos = lines[1].split(' | Added on ')[0]
        if 'on page' in pos.lower():
            pages = pos.split(' | ')[0][pos.lower().find('on page') + 8:]
            location = pos.split(' | ')[1][9:]
            id = int(location.split('-')[0])
            pos = u'Page: %s (Location: %s)' % (pages, location)
        elif 'location' in pos.lower():
            location = pos[pos.lower().find('location') + 9:]
            id = int(location.split('-')[0])
            pos = u'Location: %s' % location

        clip['title'] = lines[0]
        clip['id'] = id
        clip['pos'] = pos

        try:
            clip['date'] = datetime.strptime(
                lines[1].split(' | Added on ')[1],
                '%A, %B %d, %Y %I:%M:%S %p'
            ).isoformat()
        except:
            clip['date'] = '<error>'

        clip['content'] = u'' if(len(lines) < 3) else lines[2]

        return clip
    except:
        print(u'Error fetching clip in section:\n\n' + section.encode('utf-8'))


def export_txt(clips):
    """Export each book's clips to single text."""
    for book in clips:
        lines = ['# ' + book.encode('utf-8')]
        for id in sorted(clips[book]):
            heading = '### ' + clips[book][id][0] + '\n'
            date = 'Saved on: ' + clips[book][id][1][0:10] + '\n'
            content = ('\n>\t' + clips[book][id][2]
                       if(len(clips[book][id][2]) > 0) else '_Bookmark_')
            text = heading + date + content
            lines.append(text.encode('utf-8'))

        filename = os.path.join(OUTPUT_DIR, '%s.md' % book)
        with open(filename, 'w') as f:
            f.write('\n\n'.join(lines))


def load_clips():
    """Load previous clips from DATA_FILE."""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (IOError, ValueError):
        return {}


def save_clips(clips):
    """Save new clips to DATA_FILE."""
    with open(DATA_FILE, 'wb') as f:
        json.dump(clips, f)


def main():
    """Main task."""

    # Load old clips
    clips = collections.defaultdict(dict)
    clips.update(load_clips())

    # Extract clips
    sections = get_sections(INPUT_FILE)
    for section in sections:
        clip = get_clip(section)
        if clip:
            clips[clip['title']][clip['id']] = [clip['pos'], clip['date'],
                                                clip['content']]

    # save/export clips
    save_clips(clips)
    export_txt(clips)


if __name__ == '__main__':
    main()
