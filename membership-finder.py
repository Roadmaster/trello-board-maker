#!/usr/bin/python
# Copyright 2015 Canonical Ltd.
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
# This utility tells you which members of a given organization in Trello
# do NOT have a membership in the Launchpad.net ~canonical group.

import argparse

from trello import *
import pprint
import sys
from launchpadlib.launchpad import Launchpad
# Needed:
# - trello API key and security token (see trello)
# - Name of the organization in trello

parser = argparse.ArgumentParser(
    description="Identify members of the given organization which"
                " are not in the given launchpad group",
    epilog="To obtain the API key and security token, see notes.rst")
parser.add_argument("key", type=str, help='Trello API key')
parser.add_argument("token", type=str, help='Trello API security token')
parser.add_argument("--org", type=str,
                    help='Name of the organization as known by Trello.',
                    default='canonical')
parser.add_argument("--team", type=str,
                    help='Name of the team as known by launchpad.',
                    default='canonical')

args = parser.parse_args()


t = Trello(args.key, args.token)
lp = Launchpad.login_with("trello-team-checker", "production")

try:
    org = t.get_organization(args.org)
except TrelloApiError as e:
    print("Unable to read/write Trello data. Maybe the credentials"
          " are expired? Error was: {}".format(e))
    raise SystemExit

for member in org.members:
    in_team = False
    fullname = member._data['fullName']
    lp_members = lp.people.findPerson(text=fullname)
    if not lp_members:
        print(u"    not found in launchpad?".format(fullname))
    else:
        for lp_member in lp_members:
            for membership in lp_member.memberships_details:
                if membership.team.name == args.team:
                    in_team = True
    print(u"{} in {}: {}".format(fullname, args.team, in_team))
