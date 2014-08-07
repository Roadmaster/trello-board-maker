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
# A small wrapper around Trello's REST API.
#
# See documentation for the API here:
# https://trello.com/docs/gettingstarted/
# To obtain the key:
# log into trello, then go to https://trello.com/1/appKey/generate
# To request the token:
# https://trello.com/1/authorize?key=$KEY&name=$APPNAME&expiration=30days&response_type=token&scope=read,write

import requests

# Organization -> member
# Board -> list -> card -> checklist -> task

class Trello():
    def __init__(self, key, token, base_url="https://api.trello.com/1"):
        self._key = key
        self._token = token
        self._base_url = base_url

    # TODO: All the run methods need to print result.content if
    # the return code is not 200.
    def do_get(self, rest_path, params=None):
        url_params = {"base_url": self._base_url,
                      "rest_path": rest_path,
                      "key": self._key,
                      "token": self._token}
        url = "{base_url}/{rest_path}?key={key}&token={token}".format(**url_params)
        if params:
            for (name,value) in params.items():
                url = url + "&{}={}".format(name,value)
        result = requests.get(url)
        return result.json()

    def do_put(self, rest_path, put_vars=None):
        params = {"key": self._key,
                  "token": self._token}
        params.update(put_vars)

        url_components={"base_url": self._base_url,
                        "rest_path": rest_path}
        url = "{base_url}/{rest_path}".format(**url_components)
        result = requests.put(url, params=params)
        return result.json()

    def do_post(self, rest_path, post_vars=None):
        url_params={"base_url": self._base_url,
                    "rest_path": rest_path,
                    "key": self._key,
                    "token": self._token}
        url = "{base_url}/{rest_path}?key={key}&token={token}".format(**url_params)
        result = requests.post(url, params=post_vars)
        return result.json()

    def get_organization(self, identifier):
        org_url = "organizations/{}".format(identifier)
        org = self.do_get(org_url)
        return Organization(self, org)


class TrelloBase():
    """
    Generic class for trello things.
    Specific properties should be overridden, otherwise all we have is
    a getter with basically just dictionary access.
    """
    def __init__(self, trello, init_dict):
        self._trello = trello
        self._data = init_dict

    def __repr__(self):
        return "<{} attrs:{!r}>".format(
            self.__class__.__name__, self._data)

    # generic dict property access
    def __getattr__(self, attribute):
        if attribute in self._data:
            return self._data[attribute]
        else:
            raise AttributeError


class Organization(TrelloBase):
    @property
    def members(self):
        members_url="organizations/{org_id}/members".format(org_id=self.id)
        params={'fields': 'all'}
        members_data = self._trello.do_get(members_url, params)
        members = []
        for member in members_data:
            members.append(Member(self._trello, member))
        return members

    def create_board(self, board_name):
        "create a board"
        create_url = "boards"
        params = {'name': board_name,
                  'idOrganization': self.id,
                  'prefs_permissionLevel': 'private'}
        board_data = self._trello.do_post(create_url, params)
        board = Board(self._trello, board_data)
        return board


class Member(TrelloBase):
    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__,
                                  self._data['username'])

    @property
    def id(self):
        return self._data['id']

    @property
    def member_type(self):
        return self._data.get('memberType', None)


class List(TrelloBase):
    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__,
                                  self._data['name'])

    def close(self):
        close_url = "lists/{list_id}/closed".format(list_id=self._data['id'])
        params={'value': 'true'}
        result = self._trello.do_put(close_url, params)


    def create_card(self, card_name, description="", label=""):
        create_url = "lists/{list_id}/cards".format(list_id=self._data['id'])
        params = {'name': card_name, 'desc': description, 'labels': label}
        card_data = self._trello.do_post(create_url, params)
        card = Card(self._trello, card_data)
        return card

class Checklist(TrelloBase):
    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__,
                                  self._data['name'])

    def create_item(self, name):
        params = {"name": name}
        create_url = "checklists/{checklist_id}/checkItems".format(checklist_id=self._data['id'])
        item_data = self._trello.do_post(create_url, params)
        item = Item(self._trello, item_data)
        return item


class Item(TrelloBase):
    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__,
                                  self._data['name'])


class Card(TrelloBase):
    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__,
                                  self._data['name'])

    def create_checklist(self, task_name, name=""):
        create_url = "checklists"
        params = {'name': name, 'idBoard': self._data['idBoard'], 'idCard': self._data['id']}
        checklist_data = self._trello.do_post(create_url, params)
        checklist = Checklist(self._trello, checklist_data)
        return checklist


class Board(TrelloBase):
    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__,
                                  self._data['name'])

    def add_member(self, member, type="normal"):
        add_url="boards/{board_id}/members/{member_id}".format(
                board_id = self._data['id'],
                member_id = member.id
                )
        params = {'type': 'normal'}
        member_data = self._trello.do_put(add_url, params)

    @property
    def members(self):
        members_url="boards/{board_id}/members".format(board_id=self._data['id'])
        members_data = self._trello.do_get(members_url)
        members = []
        for a_member in members_data:
            members.append(Member(self._trello, a_member))
        return members

    def create_list(self, list_name, pos="top"):
        "create a list"
        create_url = "boards/{board_id}/lists".format(board_id=self._data['id'])
        params = {'name': list_name, 'pos': pos}
        list_data = self._trello.do_post(create_url, params)
        list = List(self._trello, list_data)
        return list

    @property
    def lists(self):
        lists_url="boards/{board_id}/lists".format(board_id=self._data['id'])
        lists_data = self._trello.do_get(lists_url)
        lists = []
        for a_list in lists_data:
            lists.append(List(self._trello, a_list))
        return lists

    def close_all_list(self):
        for a_list in self.lists:
            a_list.close()

    def set_label_name(self, color, name):
        label_url="boards/{board_id}/labelNames/{color}".format(
                board_id = self._data['id'],
                color=color
                )
        params = {'value': name}
        label_data = self._trello.do_put(label_url, params)


