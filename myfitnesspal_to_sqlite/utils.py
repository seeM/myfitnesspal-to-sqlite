FTS_CONFIG = {
    "diary_entries": ["notes"],
    "food_entry_items": ["brand", "name"],
    "exercise_entry_items": ["name"],
    "measurement_entry_items": ["name"],
}

FOREIGN_KEYS = (
    ("food_entry_items", "diary_entry", "diary_entries", "id"),
    ("exercise_entry_items", "diary_entry", "diary_entries", "id"),
    ("measurement_entry_items", "diary_entry", "diary_entries", "id"),
    ("goals", "diary_entry", "diary_entries", "id"),
)

VIEWS = {
    "daily": (
        {"diary_entries", "food_entry_items", "exercise_entry_items", "measurement_entry_items", "goals"},
        """
        select d.date,
               d.complete,
               d.water,
               d.notes,
               dm.breakfast_calories,
               dm.breakfast_carbohydrates,
               dm.breakfast_fat,
               dm.breakfast_protein,
               dm.breakfast_sodium,
               dm.breakfast_sugar,
               dm.lunch_calories,
               dm.lunch_carbohydrates,
               dm.lunch_fat,
               dm.lunch_protein,
               dm.lunch_sodium,
               dm.lunch_sugar,
               dm.dinner_calories,
               dm.dinner_carbohydrates,
               dm.dinner_fat,
               dm.dinner_protein,
               dm.dinner_sodium,
               dm.dinner_sugar,
               dm.snacks_calories,
               dm.snacks_carbohydrates,
               dm.snacks_fat,
               dm.snacks_protein,
               dm.snacks_sodium,
               dm.snacks_sugar,
               dt.total_calories,
               dt.total_carbohydrates,
               dt.total_fat,
               dt.total_protein,
               dt.total_sodium,
               dt.total_sugar,
               g.calories as goal_calories,
               g.carbohydrates as goal_carbohydrates,
               g.fat as goal_fat,
               g.protein as goal_protein,
               g.sodium as goal_sodium,
               g.sugar as goal_sugar,
               dm2.weight,
               de.total_exercise_minutes,
               de.total_calories_burned
        from diary_entries d
        left join (
            select d.date,
                   sum(case when meal = 'breakfast' then calories end) as breakfast_calories,
                   sum(case when meal = 'breakfast' then carbohydrates end) as breakfast_carbohydrates,
                   sum(case when meal = 'breakfast' then fat end) as breakfast_fat,
                   sum(case when meal = 'breakfast' then protein end) as breakfast_protein,
                   sum(case when meal = 'breakfast' then sodium end) as breakfast_sodium,
                   sum(case when meal = 'breakfast' then sugar end) as breakfast_sugar,
                   sum(case when meal = 'lunch' then calories end) as lunch_calories,
                   sum(case when meal = 'lunch' then carbohydrates end) as lunch_carbohydrates,
                   sum(case when meal = 'lunch' then fat end) as lunch_fat,
                   sum(case when meal = 'lunch' then protein end) as lunch_protein,
                   sum(case when meal = 'lunch' then sodium end) as lunch_sodium,
                   sum(case when meal = 'lunch' then sugar end) as lunch_sugar,
                   sum(case when meal = 'dinner' then calories end) as dinner_calories,
                   sum(case when meal = 'dinner' then carbohydrates end) as dinner_carbohydrates,
                   sum(case when meal = 'dinner' then fat end) as dinner_fat,
                   sum(case when meal = 'dinner' then protein end) as dinner_protein,
                   sum(case when meal = 'dinner' then sodium end) as dinner_sodium,
                   sum(case when meal = 'dinner' then sugar end) as dinner_sugar,
                   sum(case when meal = 'snacks' then calories end) as snacks_calories,
                   sum(case when meal = 'snacks' then carbohydrates end) as snacks_carbohydrates,
                   sum(case when meal = 'snacks' then fat end) as snacks_fat,
                   sum(case when meal = 'snacks' then protein end) as snacks_protein,
                   sum(case when meal = 'snacks' then sodium end) as snacks_sodium,
                   sum(case when meal = 'snacks' then sugar end) as snacks_sugar
            from food_entry_items f
            left join diary_entries d on d.id = f.diary_entry
            group by d.date
        ) dm on dm.date = d.date
        left join (
            select d.date,
                   sum(f.calories) as total_calories,
                   sum(f.carbohydrates) as total_carbohydrates,
                   sum(f.fat) as total_fat,
                   sum(f.protein) as total_protein,
                   sum(f.sodium) as total_sodium,
                   sum(f.sugar) as total_sugar
            from food_entry_items f
            left join diary_entries d on d.id = f.diary_entry
            group by d.date
        ) dt on dt.date = d.date
        left join goals g on g.diary_entry = d.id
        left join (
            select d.date,
                   avg(case when m.name = 'Weight' then value end) as weight
            from measurement_entry_items m
            left join diary_entries d on d.id = m.diary_entry
            group by d.date
        ) dm2 on dm2.date = d.date
        left join (
            select d.date,
                   sum(e.minutes) as total_exercise_minutes,
                   sum(e.calories_burned) as total_calories_burned
            from exercise_entry_items e
            left join diary_entries d
            on d.id = e.diary_entry
            group by d.date
        ) de on de.date = d.date
        """,
    ),
}


def fetch_diary_entry(date, client, measurements):
    raw = client.get_date(date)
    raw_measurements = {}
    for m in measurements:
        measurement_entry = client.get_measurements(m, date, date)
        if date in measurement_entry:
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


def ensure_foreign_keys(db):
    for expected_foreign_key in FOREIGN_KEYS:
        table, column, table2, column2 = expected_foreign_key
        if (
            expected_foreign_key not in db[table].foreign_keys
            and
            # Ensure all tables and columns exist
            db[table].exists()
            and db[table2].exists()
            and column in db[table].columns_dict
            and column2 in db[table2].columns_dict
        ):
            db[table].add_foreign_key(column, table2, column2)


def ensure_db_shape(db):
    "Ensure FTS is configured and expected FKS, views and (soon) indexes are present"
    # Foreign keys:
    ensure_foreign_keys(db)
    db.index_foreign_keys()

    # FTS:
    existing_tables = set(db.table_names())
    for table, columns in FTS_CONFIG.items():
        if "{}_fts".format(table) in existing_tables:
            continue
        if table not in existing_tables:
            continue
        db[table].enable_fts(columns, create_triggers=True)

    # Views:
    existing_views = set(db.view_names())
    existing_tables = set(db.table_names())
    for view, (tables, sql) in VIEWS.items():
        # Do all of the tables exist?
        if not tables.issubset(existing_tables):
            continue
        db.create_view(view, sql, replace=True)
