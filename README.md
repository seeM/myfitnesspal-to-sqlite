# myfitnesspal-to-sqlite

[![PyPI](https://img.shields.io/pypi/v/myfitnesspal-to-sqlite.svg)](https://pypi.org/project/myfitnesspal-to-sqlite/)
[![Changelog](https://img.shields.io/github/v/release/seem/myfitnesspal-to-sqlite?include_prereleases&label=changelog)](https://github.com/seem/myfitnesspal-to-sqlite/releases)
[![Tests](https://github.com/seem/myfitnesspal-to-sqlite/workflows/Test/badge.svg)](https://github.com/seem/myfitnesspal-to-sqlite/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/seem/myfitnesspal-to-sqlite/blob/master/LICENSE)

Save data from MyFitnessPal to a SQLite database.

## Installation

Install this tool using `pip`:

    $ pip install myfitnesspal-to-sqlite

## Authentication

This tool relies on `python-myfitnesspal`, which allows [authentication via the system keyring](https://github.com/coddingtonbear/python-myfitnesspal#authentication).

Install `python-myfitnesspal` using `pip`:

    $ pip install myfitnesspal

Store your MyFitnessPal password in the system keyring:

    $ myfitnesspal store_password my_user

Note that all commands assume that your password is stored in the system keyring.

## Fetching diary entries

The `diary` command retrieves food, exercise, goal and measurement entries for a given user and date.

    $ myfitnesspal-to-sqlite diary myfitnesspal.db my_user 2021-07-14

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd myfitnesspal-to-sqlite
    python -mvenv venv
    source venv/bin/activate

Or if you are using `pipenv`:

    pipenv shell

Now install the dependencies and tests:

    pip install -e '.[test]'

To run the tests:

    pytest
