#!/usr/bin/python3
#
# Copyright 2014 Canonical Ltd.
# Written by:
#   Daniel Manrique <roadmr@ubuntu.com>
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <http://www.gnu.org/licenses/>.
#
# A parser for stories and tasks.
# - Each story is delimited by a newline (one blank line before story
#   title).
# - The title should be of the form::
#
#     ^Story \d+ - .*
#
# - Each line after the title should contain either one task, or a
#   key:value pair. Accepted key/value pairs are:
#
#     - size: [s, m, l, xl]
#     - definition-of-done: (long text explaining the DOD)
#     - demo-lead: Who will demo the story.
#
# Importance is determined by order: stories at the top are more
# important.
#
# This document will be exported to Trello with one card per story. Size,
# DOD, demo-lead will be added in the story's description.


import sys
import re
import pprint

def parse_stories(stream):
    stories = []
    buffer = []
    for line in stream.readlines():
        if (re.match("^ *$", line)):
            # proces teh bufer
            stories.append(parse_story(buffer))
            buffer = []
        else:
            buffer.append(line)
    # End of file! Parse one last time
    if buffer:
        stories.append(parse_story(buffer))
    return stories

def parse_story(lines):
    """
        Parses a list of lines containing a story definition,
        returns a dictionary containing:
        - story_number: a string
        - story_description: a string
        - story_tasks: a list
        - story_fields: a list of fields of metadata
    """
    fields = ["size", "definition-of-done", "demo-lead"]
    lines = [line.strip() for line in lines]
    if not lines:
        return None
    matches = re.match("Story (?P<number>\d+) - (?P<description>.+)", lines[0])
    if matches:
        number = matches.group('number')
        description = matches.group('description')
    else:
        number = 0
        description = lines[0]
    result = {"story_number": number, "story_description": description,
              'story_tasks': [], "story_fields": {}}
    for l in lines[1:]:
        field_matches = re.match(r"(?P<field_name>.+?): (?P<field_data>.+)", l)
        matched_known_field = False
        if field_matches:
            for field in fields:
                if field == field_matches.group('field_name'):
                    result['story_fields'][field] = field_matches.group('field_data')
                    matched_known_field = True
                continue
        if not matched_known_field:
            result['story_tasks'].append(l)
    return result

if __name__ == "__main__":
    #  MAIN STUFF HERE
    if len(sys.argv) < 2:
        sys.exit(1)

    filename = sys.argv[1]

    with open(filename) as file:
        stories = parse_stories(file)
        pprint.PrettyPrinter().pprint(stories)

