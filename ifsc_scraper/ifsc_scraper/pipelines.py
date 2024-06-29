# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3
from .items import EventItem, CategoryItem, AthleteItem, EntryItem

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class IfscScraperPipeline:
    def __init__(self):
        # Create a connection to the database
        self.con = sqlite3.connect("ifsc_results.db")

        # Create a cursor object
        self.cur = self.con.cursor()

        # Create the tables
        self.create_tables()

    def create_tables(self):
        # Create a table for storing event info if necessary
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY,
                event_name TEXT,
                event_date TEXT,
                event_location TEXT
            );
            """
        )

        # Create a table for storing category info if necessary
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY,
                event_id INTEGER,
                category_discipline TEXT,
                category_name TEXT,
                FOREIGN KEY (event_id) REFERENCES events (event_id)
            );
            """
        )

        # Create a table for storing athlete info if necessary
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS athletes (
                athlete_id INTEGER PRIMARY KEY,
                athlete_firstname TEXT,
                athlete_lastname TEXT,
                athlete_country TEXT,
                athlete_birthday TEXT,
                athlete_gender TEXT,
                athlete_paraclimbing_sport_class TEXT,
                athlete_height INTEGER,
                athlete_speed_personal_best_score REAL,
                athlete_speed_personal_best_date TEXT,
                athlete_speed_personal_best_round TEXT
            );
            """
        )

        # Create a table for storing athlete event entry info if necessary
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                category_id INTEGER,
                athlete_id INTEGER,
                athlete_rank INTEGER,
                athlete_age INTEGER,
                athlete_years_active INTEGER,
                athlete_prior_participations INTEGER,
                entry_round_scores TEXT,
                FOREIGN KEY (category_id) REFERENCES categories (category_id),
                FOREIGN KEY (athlete_id) REFERENCES athletes (athlete_id),
                PRIMARY KEY (category_id, athlete_id)
            );
            """
        )

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if isinstance(item, EventItem):
            self.cur.execute(
                """
                INSERT OR IGNORE INTO events (event_id, event_name, event_date, event_location)
                VALUES (?, ?, ?, ?);
                """,
                (
                    adapter.get("event_id"),
                    adapter.get("name"),
                    adapter.get("date"),
                    adapter.get("location")
                )
            )
            self.con.commit()

        elif isinstance(item, CategoryItem):
            self.cur.execute(
                """
                INSERT OR IGNORE INTO categories (category_id, event_id, category_discipline, category_name)
                VALUES (?, ?, ?, ?);
                """,
                (
                    adapter.get("category_id"),
                    adapter.get("event_id"),
                    adapter.get("discipline"),
                    adapter.get("name"),
                )
            )
            self.con.commit()

        elif isinstance(item, AthleteItem):
            self.cur.execute(
                """
                INSERT INTO athletes (
                athlete_id, athlete_firstname, athlete_lastname, athlete_country, athlete_birthday,
                athlete_gender, athlete_paraclimbing_sport_class, athlete_height, athlete_speed_personal_best_score,
                athlete_speed_personal_best_date, athlete_speed_personal_best_round
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (athlete_id) DO UPDATE SET
                athlete_firstname=excluded.athlete_firstname,
                athlete_lastname=excluded.athlete_lastname,
                athlete_country=excluded.athlete_country,
                athlete_gender=excluded.athlete_gender,
                athlete_paraclimbing_sport_class=excluded.athlete_paraclimbing_sport_class,
                athlete_height=excluded.athlete_height,
                athlete_speed_personal_best_score=excluded.athlete_speed_personal_best_score,
                athlete_speed_personal_best_date=excluded.athlete_speed_personal_best_date,
                athlete_speed_personal_best_round=excluded.athlete_speed_personal_best_round;
                """,
                (
                    adapter.get("athlete_id"),
                    adapter.get("firstname"),
                    adapter.get("lastname"),
                    adapter.get("country"),
                    adapter.get("birthday"),
                    adapter.get("gender"),
                    adapter.get("paraclimbing_sport_class"),
                    adapter.get("height"),
                    adapter.get("speed_personal_best_score"),
                    adapter.get("speed_personal_best_date"),
                    adapter.get("speed_personal_best_round")
                )
            )
            self.con.commit()

        elif isinstance(item, EntryItem):
            self.cur.execute(
                """
                INSERT OR IGNORE INTO entries (
                category_id, athlete_id, athlete_rank, athlete_age, athlete_years_active,
                athlete_prior_participations, entry_round_scores
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    adapter.get("category_id"),
                    adapter.get("athlete_id"),
                    adapter.get("rank"),
                    adapter.get("age"),
                    adapter.get("years_active"),
                    adapter.get("prior_participations"),
                    adapter.get("round_scores")
                )
            )
            self.con.commit()

        return item

    def close_spider(self, spider):
        # Close the cursor and the connection
        self.cur.close()
        self.con.close()
