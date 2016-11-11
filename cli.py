#!/usr/bin/env python
from sys import stdin

from notes.api import NotesAPI


def main():
    command = stdin.readline().rstrip().lower()
    getattr(NotesAPI(), command)(stdin.readline().rstrip())


if __name__ == '__main__':
    main()
