# Running the Note-taking Prototype

The solution here was implemented using Python 2.7, and I'm not bothering with
tox or any other means of trying and validating multi-version support, as I
presume that Python ecosystem hygiene is not a critical evaluation criterion.
If `python --version` reveals a local `python` version 2.x is available, then
you're good. Otherwise, you might find that [tox](https://tox.readthedocs.io/en/latest/)
is the most straightforward way of getting Python 2.7 on your machine and
running tests.

That being said, here's how you set things up:

    pip install -r requirements.txt
    pip install -e .

The second command [is needed](http://doc.pytest.org/en/latest/goodpractices.html#choosing-a-test-layout-import-rules)
to make the `notes` package easy to access from tests in the "test" directory.

To run unit tests:

    py.test

To execute commands as described below on any Linux, Unix or OS X shell:

    ./cli.py

The script's execute attribute should have been set by git. If you need me to
make it work on Windows, write me and I'll take a stab


# Intro

Hi, and thanks for taking the time to hack on this exercise with us.

We would like to build the next generation of note taking! But first, we'd like
to create a prototype of some of the API functions in the form of a simple
application. The prototype should be able to create, update, delete and search
notes based on commands from standard input and write the output to standard
output.

The application will start and wait for [commands](#input-format) from standard
input. For example:

    $ ./notesapp
    ... user enters ...
    CREATE
    { "id": "12345678", "tag": ["alfa","bravo"], "content": "Hello World" }

It should be also possible to automate the input:

    $ cat simple_cases.txt | ./notesapp

You are free to implement it in your programming language of choice. You are
also free to utilize a data store of your choice.

Please feel free to ask any of us questions, at any time. Questions are
encouraged. Use of the internet is encouraged. We just want to see you write
some code and talk to you about it afterwards.

# Input Format

The prototype must support 4 commands:

CREATE

UPDATE

DELETE

SEARCH

The CREATE, UPDATE, and DELETE commands indicate modifications to the set of
notes that can be searched.

# CREATE

The CREATE command indicates that a note should be added to the set of
searchable notes. It will be followed by a single line containing a JSON
document with the following format:

```
{ "id": "12345678", "tag": ["alfa","bravo"], "content": "Hello World" }
```
The `id` element contains the unique identifier for the note. This will be used
later to update the note, delete the note, and indicate that the note matches a search.

Zero or more tag elements indicate the names of tags assigned to the note. Tag
names will not include the ':' character.

The content element contains the plain-text content of the note. The content
will consist entirely of ASCII characters.

# UPDATE

The UPDATE command is used to indicate that a note needs to be updated and will
be followed by a JSON document with the same format as documented above, with an ID that corresponds to a note previously added via the CREATE command.

# DELETE

The DELETE command is used to remove a note. It will be followed by a single
line containing the ID of the note to remove.

# SEARCH

The SEARCH command will be followed by a single line containing a search query.

The prototype must support the following search functions:

## Tag matches (with the "tag:" operator).

tag:potato matches the tag "potato"

tag:pot* matches the tags "pot" and "potato"

## Text content (exact and prefix matches) search.

potato matches "Sweet Potato Pie" does not match "Mash four potatoes together"

pot* matches both "Pot: Kettle; Kettle: Pot" and "Sweet Potato Pie"

we're matches "We're going to the circus!"

# Output Format

The CREATE, UPDATE, and DELETE commands should produce no output.

The SEARCH command should output a single line consisting of a comma separated
list of note IDs that match the search.

A note matches a search if it matches all of the provided search terms. If no
notes match the search an empty line should be output.

# Testing

Provide a file containing commands which cover as much of the functionality as
practical. A short test case file will be provided as a sample.
