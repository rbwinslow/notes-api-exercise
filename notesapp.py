#!/usr/bin/env python
from sys import stdin

from notes.api import NotesAPI


def main():
    api = NotesAPI()
    _api_call(api)
    while not stdin.isatty():
        if not _api_call(api):
            break


def _api_call(api):
    command = stdin.readline().rstrip().lower()
    if command:
        getattr(api, command)(stdin.readline().rstrip())
        return True


if __name__ == '__main__':
    main()
