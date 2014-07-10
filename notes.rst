=====
Notes
=====

What is this?
=============

It's a set of utilities to take a text document (see format below) containing
user stories and their tasks, and produce a Trello board with a card for each
story, with tasks as checklist items, and several lists to reflect story
progress/status.

The certification team at Canonical uses this to keep track of work in 2-week
long iterations.

Scrum with trello will use an external backlog, and the planning meeting
will still capture the stories and the tasks in a google doc. This is
more agile than using Trello directly and has worked well in the past.

Source text document
====================

The google doc is easy to export to plaintext and reformat to match the
required format, which is:

- Each story is delimited by a newline (one blank line before story
  title).
- The title should be of the form::

    ^Story \d+ - .*

- Each line after the title should contain either one task, or a
  key:value pair. Accepted key/value pairs are:
  
    - size: [s, m, l, xl]
    - definition-of-done: (long text explaining the DOD)
    - demo-lead: Who will demo the story.

Importance is determined by order: stories at the top are more
important.

This document will be exported to Trello with one card per story. Size,
DOD, demo-lead will be added in the story's description.


Trello board
============

Will be set to "org" permissions so anyone in the given organization can
work with it.

Four lists will be added: "New", "In progress", "Started", "Blocked",
"Done". All stories will initially be added to the "New" list. Since
Trello doesn't keep relative card ordering, priority will be encoded in
colored labels, with redder colors being higher importance. We can
encode 6 importances here, stories 7 and over will not be given a color,
but they're usually pretty low in priority.

A few simple rules on how to operate this:

    - As a rule, to pick stories, choose the "redder" ones, from either
      "new" or "in progress".
    - To work on a story, add yourself to it, and move it from "new" to
      "in progress".
    - If you're not actively working on a story, move it to "Started"
      and remove yourself from it.
    - If you're blocked, move it to "blocked" and don't remove yourself
      from it.
    - When done, move to "done" and remove yourself from it.

Problems
========

Our main problems with Trello were:

    - Loss of relative priorities. This is mitigated by use of colored
      labels to encode priority. Always go for the "redder" stories:
      red, orange, yellow :) then go for purple, blue and green.
    - Visibility of what's being worked on and by whom. At a glance you
      can see stories that haven't been started (in "New"), stories that
      are actively being worked on ("in progress"), stories that were
      stopped and could use a hand ("started"), blockers as usual, and
      finished work. Using one card per story also creates a smaller
      board which is easier to see on one screen.
    - Creating new boards was labor-intensive. Trello's API allows
      auto-creating the board from a simple text file (which we're
      already using as an intermediate step), so with our new tools this
      actually becomes an advantage over the current spreadsheet
      approach.


