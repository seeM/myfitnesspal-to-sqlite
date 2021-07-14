from datetime import datetime
import myfitnesspal
import sqlite_utils
import click
from .utils import (
    fetch_diary_entry,
    fetch_measurement_entries,
    save_diary_entry,
    save_measurement_entries,
)


@click.group()
@click.version_option()
def cli():
    "Save data from MyFitnessPal to a SQLite database"


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.argument(
    "user",
    type=str,
    required=True,
)
@click.argument(
    "date",
    type=str,
    required=True,
)
def diary(db_path, user, date):
    "Save food, exercise, and goal diary entries for a given user and date"
    date = datetime.fromisoformat(date).date()

    db = sqlite_utils.Database(db_path)
    client = myfitnesspal.Client(user)

    diary_entry = fetch_diary_entry(date, client)
    save_diary_entry(db, diary_entry)


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.argument(
    "user",
    type=str,
    required=True,
)
@click.argument(
    "measurement",
    type=str,
    required=True,
)
@click.argument(
    "start_date",
    type=str,
    required=True,
)
@click.argument(
    "end_date",
    type=str,
    required=True,
)
def measurements(db_path, user, measurement, start_date, end_date):
    "Save measurements for a given user and date interval"
    start_date = datetime.fromisoformat(start_date).date()
    end_date = datetime.fromisoformat(end_date).date()

    db = sqlite_utils.Database(db_path)
    client = myfitnesspal.Client(user)

    measurement_entries = fetch_measurement_entries(
        measurement,
        start_date,
        end_date,
        client,
    )
    save_measurement_entries(db, measurement_entries, measurement)
