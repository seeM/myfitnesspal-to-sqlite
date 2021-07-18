from datetime import datetime
import myfitnesspal
import sqlite_utils
import click
from . import utils


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
@click.option(
    "--measurement",
    multiple=True,
    required=True,
)
def diary(db_path, user, date, measurement):
    "Save food, exercise, goal, and measurement entries for a given user and date"
    date = datetime.fromisoformat(date).date()

    db = sqlite_utils.Database(db_path)
    client = myfitnesspal.Client(user)
    diary_entry = utils.fetch_diary_entry(date, client, measurement)

    utils.save_diary_entry(db, diary_entry)
    utils.ensure_db_shape(db)
