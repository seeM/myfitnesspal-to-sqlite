import json
from myfitnesspal_to_sqlite import utils
import pathlib
import pytest
import sqlite_utils
from sqlite_utils.db import ForeignKey


@pytest.fixture
def measurement_entries():
    return json.load(open(pathlib.Path(__file__).parent / "measurement_entries.json"))


@pytest.fixture
def db(measurement_entries):
    db = sqlite_utils.Database(memory=True)
    for measurement, entries in measurement_entries.items():
        utils.save_measurement_entries(db, entries, measurement)
    return db


def test_tables(db):
    assert {"measurement_entries"} == set(db.table_names())


def test_measurement_entries(db):
    measurement_entry_rows = list(db["measurement_entries"].rows)
    assert [
        {"measurement": "Weight", "date": "2021-07-11", "value": 78.3},
        {"measurement": "Weight", "date": "2021-07-09", "value": 77.1},
        {"measurement": "Weight", "date": "2021-07-08", "value": 77.8},
    ] == measurement_entry_rows
