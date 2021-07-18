def fetch_diary_entry(date, client, measurements):
    raw = client.get_date(date)
    raw_measurements = {}
    for m in measurements:
        measurement_entry = client.get_measurements(m, date, date)
        raw_measurements[m] = measurement_entry[date]

    meals = {
        meal.name: [
            {
                "short_name": entry.short_name,
                "name": entry.name,
                "nutrition_information": entry.nutrition_information,
                "quantity": entry.quantity,
                "unit": entry.unit,
            }
            for entry in meal.entries
        ]
        for meal in raw.meals
    }
    exercises = {
        exercise.name: [
            {
                "name": entry.name,
                "nutrition_information": entry.nutrition_information,
            }
            for entry in exercise.entries
        ]
        for exercise in raw.exercises
    }
    return {
        "date": raw.date,
        "complete": raw.complete,
        "water": raw.water,
        "notes": raw.notes,
        "goals": raw.goals,
        "totals": raw.totals,
        "meals": meals,
        "exercises": exercises,
        "measurements": raw_measurements,
    }


def save_diary_entry(db, diary_entry):
    original = diary_entry

    # Delete existing diary entries and related
    existing = list(db["diary_entries"].rows_where("date = ?", [original["date"]]))
    if existing:
        existing_id = existing[0]["id"]
        db["measurements"].delete_where("diary_entry = ?", [existing_id])
        db["goals"].delete_where("diary_entry = ?", [existing_id])
        db["exercise_entry_items"].delete_where("diary_entry = ?", [existing_id])
        db["food_entry_items"].delete_where("diary_entry = ?", [existing_id])
        db["diary_entries"].delete_where("id = ?", [existing_id])

    # Save diary entry
    diary_entry = {
        "date": original["date"],
        "notes": original["notes"],
        "complete": original["complete"],
        "water": original["water"],
    }
    diary_entry_id = (
        db["diary_entries"]
        .insert(
            diary_entry,
            pk="id",
            alter=True,
            column_order=["id", "date", "complete", "water", "notes"],
            columns={"notes": str},
        )
        .last_pk
    )

    # Save food items
    for meal, entries in original["meals"].items():
        for entry in entries:
            short_name = entry.get("short_name") or entry["name"].split(", ", 1)[0]
            if " - " in short_name:
                brand, name = short_name.split(" - ", 1)
            else:
                brand = None
                name = short_name
            food_entry_item = {
                "diary_entry": diary_entry_id,
                "meal": meal,
                "brand": brand,
                "name": name,
                "quantity": entry["quantity"],
                "unit": entry["unit"],
                **entry["nutrition_information"],
            }
            db["food_entry_items"].insert(
                food_entry_item,
                pk="id",
                alter=True,
                column_order=[
                    "id",
                    "diary_entry",
                    "meal",
                    "brand",
                    "name",
                    "quantity",
                    "unit",
                    *sorted(entry["nutrition_information"].keys()),
                ],
                foreign_keys=[("diary_entry", "diary_entries")],
            )

    # Save exercise items
    for exercise, entries in original["exercises"].items():
        for entry in entries:
            nutrition_information = {
                k.replace(" ", "_"): v
                for k, v in entry["nutrition_information"].items()
            }
            exercise_entry_item = {
                "diary_entry": diary_entry_id,
                "type": exercise,
                "name": entry["name"],
                **nutrition_information,
            }
            db["exercise_entry_items"].insert(
                exercise_entry_item,
                pk="id",
                alter=True,
                column_order=[
                    "id",
                    "diary_entry",
                    "type",
                    "name",
                    *sorted(entry["nutrition_information"].keys()),
                ],
                foreign_keys=[("diary_entry", "diary_entries")],
            )

    # Save goals
    nutrition_information = {k: v for k, v in original["goals"].items()}
    goals = {"diary_entry": diary_entry_id, **nutrition_information}
    db["goals"].insert(
        goals,
        pk="id",
        alter=True,
        column_order=[
            "id",
            "diary_entry",
            *sorted(nutrition_information.keys()),
        ],
        foreign_keys=[("diary_entry", "diary_entries")],
    )

    # Save measurement items
    measurement_entry_items = [
        {"diary_entry": diary_entry_id, "name": m, "value": v}
        for m, v in original["measurements"].items()
    ]
    db["measurement_entry_items"].insert_all(
        measurement_entry_items,
        pk="id",
        alter=True,
        replace=True,
        column_order=[
            "id",
            "diary_entry",
            "name",
            "value",
        ],
        foreign_keys=[("diary_entry", "diary_entries")],
    )
