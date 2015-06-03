#!/usr/bin/python3
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
# A small utility to create Trello boards for scrum. See notes.rst.

import argparse

from trello import *
from storyparser import parse_stories
import pprint
import sys
import time
# Needed:
# - name of a file containing stories (see storyparser)
# - trello API key and security token (see trello)
# - Name of the organization in trello
# - name for the new board

parser = argparse.ArgumentParser(
    description="Create a Trello board for "
    "the certification team scrum iteration.",
    epilog="To obtain the API key and security token, see notes.rst")
parser.add_argument("key", type=str, help='Trello API key')
parser.add_argument("token", type=str, help='Trello API security token')
parser.add_argument("file", type=str,
                    help='File containing stories with tasks')
parser.add_argument("--org", type=str,
                    help='Name of the organization as known by Trello.',
                    default='canonical')
parser.add_argument("--name", type=str, help='Name of the board.',
                    default="Iteration starting {}".format(
                        time.strftime("%Y-%m-%d")))
parser.add_argument("--parse-only",
                    help="Whether to only parse and show stories",
                    action='store_true', default=False)

args = parser.parse_args()

# Colors arranged by priority
colors = ['red', 'orange', 'yellow', 'purple', 'green', 'blue']
stories = None
# Reado stories
try:
    with open(args.file) as file:
        stories = parse_stories(file)
        assert(None not in stories)
except (FileNotFoundError, IOError):
    print(sys.exc_info()[1])
if args.parse_only:
    pp = pprint.PrettyPrinter().pprint
    pp(stories)
    raise SystemExit
t = Trello(args.key, args.token)


# Create a new :board with :name under :organization
try:
    org = t.get_organization(args.org)
    board = org.create_board(args.name)
except TrelloApiError as e:
    print("Unable to read/write Trello data. Maybe the credentials"
          " are expired? Error was: {}".format(e))
    raise SystemExit

# Set meaningful names for the labels
label_names = {
    'red': "Priority 1 (high)",
    'orange': "Priority 2",
    'yellow': 'Priority 3',
    'purple': 'Priority 4',
    'blue': 'Priority 5',
    'green': 'Priority 6 (low)'}
for label, name in label_names.items():
    board.set_label_name(label, name)

# Add all members of organization to board.
member_ids_in_board = [m.id for m in board.members]
for member in org.members:
    # Actually, only add those not already there.  The creator will already be
    # there and be an admin, and trello will complain if we try to switch him
    # to a normal user by just re-adding him.
    if member.id not in member_ids_in_board:
        print("Adding {} to board".format(member))
        board.add_member(member, type="normal")
# Close all existing pre-created lists
board.close_all_list()
# Add a set of predefined :lists, one is the :initial_list
initial_list = None
for listname in ["New", "In progress", "Started", "Blocked", "Done"]:
    a_list = board.create_list(listname, "bottom")
    print("Created list {}".format(a_list))
    if listname == "New":
        initial_list = a_list

for idx, story in enumerate(stories):
    label = None
    try:
        label = colors[idx]
    except:
        pass
    name = "{story_number} - {story_description}".format(**story)
    if 'story_fields' in story:
        desc = "\n".join(["{}: {}".format(k, story['story_fields'][k])
                          for k in story['story_fields'].keys()])
    card = initial_list.create_card(name, desc, label=label)
    print("  Added story {}".format(story['story_number']))
    checklist = card.create_checklist(desc, name="Story tasks")
    for task in story['story_tasks']:
        checklist.create_item(task)
        print("    Added task {}".format(task[:50]))
