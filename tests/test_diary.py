import json
from myfitnesspal_to_sqlite import utils
import pathlib
import pytest
import sqlite_utils
from sqlite_utils.db import ForeignKey


@pytest.fixture
def diary_entry():
    return json.load(open(pathlib.Path(__file__).parent / "diary_entry.json"))


@pytest.fixture
def db(diary_entry):
    db = sqlite_utils.Database(memory=True)
    utils.save_diary_entry(db, diary_entry)
    return db


def test_tables(db):
    assert {
        "diary_entries",
        "food_entry_items",
        "exercise_entry_items",
        "goals",
    } == set(db.table_names())
    assert {
        ForeignKey(
            table="food_entry_items",
            column="diary_entry",
            other_table="diary_entries",
            other_column="id",
        ),
    } == set(db["food_entry_items"].foreign_keys)
    assert {
        ForeignKey(
            table="exercise_entry_items",
            column="diary_entry",
            other_table="diary_entries",
            other_column="id",
        ),
    } == set(db["exercise_entry_items"].foreign_keys)
    assert {
        ForeignKey(
            table="goals",
            column="diary_entry",
            other_table="diary_entries",
            other_column="id",
        ),
    } == set(db["goals"].foreign_keys)


def test_diary_entries(db):
    diary_entry_rows = list(db["diary_entries"].rows)
    assert [
        {
            "id": 1,
            "date": "2021-07-08",
            "complete": 1,
            "water": 750.0,
            "notes": "",
        },
    ] == diary_entry_rows


def test_food_entry_items(db):
    food_entry_item_rows = list(db["food_entry_items"].rows)
    assert [
        {
            "id": 1,
            "diary_entry": 1,
            "meal": "snacks",
            "brand": "Cadbury's",
            "name": "Chocolate",
            "quantity": 1.0,
            "unit": "square",
            "calories": 120.0,
            "carbohydrates": 13.0,
            "fat": 7.0,
            "protein": 1.0,
            "sodium": 27.0,
            "sugar": 13.0,
        },
        {
            "id": 2,
            "diary_entry": 1,
            "meal": "snacks",
            "brand": "Cadbury's",
            "name": "Chocolate",
            "quantity": 1.0,
            "unit": "square",
            "calories": 120.0,
            "carbohydrates": 13.0,
            "fat": 7.0,
            "protein": 1.0,
            "sodium": 27.0,
            "sugar": 13.0,
        },
        {
            "id": 3,
            "diary_entry": 1,
            "meal": "snacks",
            "brand": "Cadbury's",
            "name": "Chocolate - Coconut",
            "quantity": 1.0,
            "unit": "square",
            "calories": 120.0,
            "carbohydrates": 13.0,
            "fat": 7.0,
            "protein": 1.0,
            "sodium": 27.0,
            "sugar": 13.0,
        },
    ] == food_entry_item_rows


def test_exercise_entry_items(db):
    exercise_entry_item_rows = list(db["exercise_entry_items"].rows)
    assert [
        {
            "id": 1,
            "diary_entry": 1,
            "type": "cardiovascular",
            "name": "Rock climbing, ascending rock",
            "calories_burned": 424.0,
            "minutes": 30.0,
        }
    ] == exercise_entry_item_rows


def test_goals(db):
    goal_rows = list(db["goals"].rows)
    assert [
            {
                "id": 1,
                "diary_entry": 1,
                "calories": 2014.0,
                "carbohydrates": 252.0,
                "fat": 67.0,
                "protein": 101.0,
                "sodium": 2300.0,
                "sugar": 76.0,
            }
    ] == goal_rows
