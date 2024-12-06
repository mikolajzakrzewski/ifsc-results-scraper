# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3
from .items import EventItem, AthleteItem, EntryItem

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class IfscScraperPipeline:
    def __init__(self):
        # Create a connection to the database
        self.con = sqlite3.connect("scraped_data/ifsc_results.db")

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
                name TEXT,
                start_date TEXT,
                end_date TEXT,
                location TEXT
            );
            """
        )

        # Create a table for storing athlete info if necessary
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS athletes (
                athlete_id INTEGER PRIMARY KEY,
                firstname TEXT,
                lastname TEXT,
                country TEXT,
                birthday TEXT,
                gender TEXT,
                paraclimbing_sport_class TEXT,
                height INTEGER,
                speed_personal_best_score REAL,
                speed_personal_best_date TEXT,
                speed_personal_best_round TEXT
            );
            """
        )

        # Create a table for storing athlete event entry info if necessary
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                event_id INTEGER,
                discipline TEXT,
                category TEXT,
                athlete_id INTEGER,
                rank INTEGER,
                age INTEGER,
                years_active INTEGER,
                prior_participations INTEGER,
                qualification_rank INTEGER,
                qualification_score REAL,
                semi_final_rank INTEGER,
                semi_final_score REAL,
                final_rank INTEGER,
                final_score REAL,
                FOREIGN KEY (event_id) REFERENCES events (event_id),
                FOREIGN KEY (athlete_id) REFERENCES athletes (athlete_id),
                PRIMARY KEY (event_id, athlete_id)
            );
            """
        )

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Insert the item into the appropriate database table based on the item type
        if isinstance(item, EventItem):
            self.cur.execute(
                """
                INSERT OR IGNORE INTO events (event_id, name, start_date, end_date, location)
                VALUES (?, ?, ?, ?, ?);
                """,
                (
                    adapter.get("event_id"),
                    adapter.get("name"),
                    adapter.get("start_date"),
                    adapter.get("end_date"),
                    adapter.get("location")
                )
            )
            self.con.commit()

        elif isinstance(item, AthleteItem):

            # Athlete info may change over time, so ON CONFLICT DO UPDATE is used to update the athlete info
            self.cur.execute(
                """
                INSERT INTO athletes (
                athlete_id, firstname, lastname, country, birthday, gender, paraclimbing_sport_class, height,
                speed_personal_best_score, speed_personal_best_date, speed_personal_best_round
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (athlete_id) DO UPDATE SET
                firstname=excluded.firstname,
                lastname=excluded.lastname,
                country=excluded.country,
                gender=excluded.gender,
                paraclimbing_sport_class=excluded.paraclimbing_sport_class,
                height=excluded.height,
                speed_personal_best_score=excluded.speed_personal_best_score,
                speed_personal_best_date=excluded.speed_personal_best_date,
                speed_personal_best_round=excluded.speed_personal_best_round;
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
                event_id, discipline, category, athlete_id, rank, age, years_active, prior_participations,
                qualification_rank, qualification_score, semi_final_rank, semi_final_score, final_rank, final_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    adapter.get("event_id"),
                    adapter.get("discipline"),
                    adapter.get("category"),
                    adapter.get("athlete_id"),
                    adapter.get("rank"),
                    adapter.get("age"),
                    adapter.get("years_active"),
                    adapter.get("prior_participations"),
                    adapter.get("qualification_rank"),
                    adapter.get("qualification_score"),
                    adapter.get("semi_final_rank"),
                    adapter.get("semi_final_score"),
                    adapter.get("final_rank"),
                    adapter.get("final_score")
                )
            )
            self.con.commit()

        return item

    def close_spider(self, spider):
        # Close the cursor and the connection
        self.cur.close()
        self.con.close()
