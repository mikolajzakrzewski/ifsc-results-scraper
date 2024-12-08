import unicodedata

import scrapy
import json
import re

from unidecode import unidecode
from bs4 import BeautifulSoup
from scrapy.spiders import Spider
from ..items import EventItem, AthleteItem, EntryItem, FileEntryItem

# URLs of the website
domain_name = "ifsc-climbing.org"
base_url = f"https://www.{domain_name}"
api_url = f"{base_url}/api/dapi"

# Dictionaries for mapping the discipline and category names
discipline_names = {
    "l": "lead",
    "s": "speed",
    "b": "boulder",
    "c": "combined",
    "bl": "boulder&lead"
}

category_names = {
    "m": "men",
    "w": "women",
    "yam": "youth a male",
    "yaf": "youth a female",
    "ybm": "youth b male",
    "ybf": "youth b female",
    "jm": "juniors male",
    "jf": "juniors female"
}


# Spider class for scraping the results from the IFSC result service
class IfscClimbingOrgSpider(Spider):
    name = "ifsc_climbing_org"
    allowed_domains = [domain_name]

    # Custom settings for exporting the results to a CSV file
    custom_settings = {
        'FEEDS': {
            'scraped_data/results_%(name)s_%(time)s.csv': {
                'format': 'csv',
                'encoding': 'utf8',
                'store_empty': True,
                'item_classes': [FileEntryItem, 'ifsc_scraper.items.FileEntryItem'],
                'fields': [
                    'event',
                    'event_start_date',
                    'event_end_date',
                    'discipline',
                    'category',
                    'athlete_id',
                    'rank',
                    'firstname',
                    'lastname',
                    'country',
                    'birthday',
                    'gender',
                    'paraclimbing_sport_class',
                    'height',
                    'age',
                    'years_active',
                    'prior_participations',
                    'qualification_rank',
                    'qualification_score',
                    'semi_final_rank',
                    'semi_final_score',
                    'final_rank',
                    'final_score'
                ],
                'item_export_kwargs': {
                    'export_empty_fields': True
                }
            }
        }
    }

    def __init__(self, years, disciplines, categories, *args, **kwargs):
        super(IfscClimbingOrgSpider, self).__init__(*args, **kwargs)
        self.years = years.split(',')
        self.disciplines = [discipline_names[discipline] for discipline in disciplines.split(',')]
        self.categories = [category_names[category] for category in categories.split(',')]
        self.start_urls = [
            f"{api_url}/events/all?dateFrom=$range({year}-01-01,{year}-12-31)&limit=100"
            for year in self.years
        ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse_year
            )

    # Gather the event IDs for the given year, leagues and discipline kinds
    def parse_year(self, response):
        normalized_data = unicodedata.normalize("NFKD", response.text)
        json_data = json.loads(normalized_data)

        # Extract the events' information from the JSON data
        for event in json_data['items']:
            event_url = event['url']
            event_name = event['title']
            event_start_date = event['fields']['dateFrom'][0:10]
            event_end_date = event['fields']['dateTo'][0:10]
            event_location = event['fields'].get('location', None)
            yield scrapy.Request(
                f"{event_url}result/index",
                callback=self.parse_event,
                cb_kwargs={"event_name": event_name, "event_start_date": event_start_date,
                           "event_end_date": event_end_date, "event_location": event_location}
            )

    # Gather the full result URLs for the given event, discipline kinds and categories
    def parse_event(self, response, event_name, event_start_date, event_end_date, event_location):
        normalized_data = unicodedata.normalize("NFKD", response.text)
        unicodedata.normalize("NFKD", normalized_data)

        # Extract the event page URL from the response
        event_url = response.url

        # Extract the event ID from the response
        start_str = "eventId\\\":\\\""
        end_str = "\\\","
        start_index = normalized_data.find(start_str)
        end_index = normalized_data.find(end_str, start_index + len(start_str))
        if start_index != -1 and end_index != -1:
            event_id = normalized_data[start_index + len(start_str):end_index]
        else:
            return

        # Extract the discipline and category IDs from the response
        start_str = "navigationItems\\\":"
        end_str = ",\\\"defaultDisciplinePath"
        start_index = normalized_data.find(start_str)
        end_index = normalized_data.find(end_str, start_index + len(start_str))
        event_data = normalized_data[start_index + len(start_str):end_index].replace("\\", "")
        event_data = json.loads(event_data)

        # Create a variable to check if the event item has already been yielded
        event_yielded = False

        for category_id, category_data in event_data.items():
            if category_data['discipline'] in self.disciplines and category_data['category'] in self.categories:
                if not event_yielded:
                    yield EventItem(
                        event_id=event_id,
                        name=event_name,
                        start_date=event_start_date,
                        end_date=event_end_date,
                        location=event_location
                    )
                    event_yielded = True

                # Create headers and a payload for the POST request
                headers = {
                    "Next-Action": "efa2fa106f24654dd09188f3c815302653521600"
                }
                payload = [{"event_id": event_id, "id": category_id}]

                yield scrapy.Request(
                    event_url,
                    callback=self.parse_results,
                    method="POST",
                    headers=headers,
                    body=json.dumps(payload),
                    cb_kwargs={"event_id": event_id, "event_start_date": event_start_date,
                               "event_end_date": event_end_date, "event_name": event_name,
                               "discipline": category_data['discipline'], "category": category_data['category']}
                )

    # Gather data from the full results of the given event
    def parse_results(self, response, event_id, event_start_date, event_end_date, event_name, discipline, category):
        normalized_data = unicodedata.normalize("NFKD", response.text)

        # Extract the part of the response that contains the ranking data
        separator_index = normalized_data.find("1:")
        normalized_data = normalized_data[separator_index + 2:].strip()
        ranking = json.loads(normalized_data)["data"]["ranking"]

        # Extract the athletes' information from the ranking data
        if ranking is not None:
            for athlete in ranking:
                athlete_id = athlete["athlete_id"]
                rank = athlete["rank"]
                round_scores = [
                    {"round_name": round_type["round_name"],
                     "rank": round_type["rank"],
                     "score": round_type["score"]}
                    for round_type in athlete["rounds"]
                ]

                # Convert the athlete's name to a URL-friendly format
                name = athlete["firstname"] + " " + athlete["lastname"].strip()
                name = unidecode(name)
                name = name.lower()
                name = re.sub(r"[^a-z]", "-", name)

                # Combine the athlete's name with the athlete's ID to form the athlete's URL
                athlete_url = f"{base_url}/athlete/{athlete_id}/{name}"
                yield scrapy.Request(
                    athlete_url,
                    callback=self.parse_athlete,
                    cb_kwargs={"event_id": event_id, "event_start_date": event_start_date,
                               "event_end_date": event_end_date, "event_name": event_name, "discipline": discipline,
                               "category": category, "rank": rank, "round_scores": round_scores}
                )

    def parse_athlete(self, response, event_id, event_start_date, event_end_date, event_name, discipline, category,
                      rank, round_scores):
        # Extract the part of the response that contains the athlete's information
        normalized_data = unicodedata.normalize("NFKD", response.text)
        soup = BeautifulSoup(normalized_data, 'html.parser')
        script_tags = soup.find_all('script')

        # Search for the script tag containing the athlete's information (example search text: 'firstname')
        search_text = 'firstname'
        script_text = [script.string for script in script_tags if script.string and search_text in script.string]
        script_text = script_text[0]
        script_text = script_text.replace("\\", "")

        # Extract the athlete's information from the script text
        match = re.search(r'{"athlete":{.*', script_text)
        if match:
            script_text = match.group()

            # Remove trailing characters from the text to get the JSON data
            opening_braces = script_text.count('{')
            closing_braces = script_text.count('}')
            closing_brace_index = closing_braces - opening_braces
            reversed_script_text = script_text[::-1]
            for i in range(closing_brace_index):
                closing_brace_index = reversed_script_text.find('}')
                script_text = script_text[:-closing_brace_index]

            athlete_info = json.loads(script_text)["athlete"]

            # Extract the athlete's information from the JSON data
            athlete_id = athlete_info["id"]
            firstname = athlete_info["firstname"]
            lastname = athlete_info["lastname"]
            country = athlete_info["country"]
            birthday = athlete_info["birthday"]
            gender = athlete_info["gender"]
            paraclimbing_sport_class = athlete_info["paraclimbing_sport_class"]
            height = athlete_info["height"]
            if athlete_info["speed_personal_best"] is None:
                speed_personal_best_score = None
                speed_personal_best_date = None
                speed_personal_best_round = None
            else:
                speed_personal_best_score = athlete_info["speed_personal_best"]["time"]
                speed_personal_best_date = athlete_info["speed_personal_best"]["date"]
                speed_personal_best_round = athlete_info["speed_personal_best"]["round_name"]

            # Create an athlete item and save it to the database
            yield AthleteItem(
                athlete_id=athlete_id,
                firstname=firstname,
                lastname=lastname,
                country=country,
                birthday=birthday,
                gender=gender,
                paraclimbing_sport_class=paraclimbing_sport_class,
                height=height,
                speed_personal_best_score=speed_personal_best_score,
                speed_personal_best_date=speed_personal_best_date,
                speed_personal_best_round=speed_personal_best_round
            )

            # Climbers' age is rounded down to the nearest year (general rule in climbing competitions)
            event_year = event_start_date[0:4]
            if birthday is None:
                age = None
            else:
                age = int(event_year) - int(birthday[0:4])

            # Calculate the number of years the athlete has been active in the IFSC based on the first documented result
            first_activity_year = int(athlete_info["all_results"][-1]["season"])
            years_active = int(event_year) - first_activity_year
            prior_participations = 0
            for result in reversed(athlete_info["all_results"]):
                if result["date"] > event_start_date:
                    break
                else:
                    prior_participations += 1

            qualification_data = next(
                (entry_round for entry_round in round_scores if entry_round["round_name"] == "Qualification"), {}
            )
            semi_final_data = next(
                (entry_round for entry_round in round_scores if entry_round["round_name"] == "Semi-Final"), {}
            )
            final_data = next(
                (entry_round for entry_round in round_scores if entry_round["round_name"] == "Final"), {}
            )

            # Create an entry item and save it to the database
            yield EntryItem(
                event_id=event_id,
                discipline=discipline,
                category=category,
                athlete_id=athlete_id,
                rank=rank,
                age=age,
                years_active=years_active,
                prior_participations=prior_participations,
                qualification_rank=qualification_data.get("rank", None),
                qualification_score=qualification_data.get("score", None),
                semi_final_rank=semi_final_data.get("rank", None),
                semi_final_score=semi_final_data.get("score", None),
                final_rank=final_data.get("rank", None),
                final_score=final_data.get("score", None)
            )

            # Create a file entry item and save it to a file
            yield FileEntryItem(
                event=event_name,
                event_start_date=event_start_date,
                event_end_date=event_end_date,
                discipline=discipline,
                category=category,
                athlete_id=athlete_id,
                rank=rank,
                firstname=firstname,
                lastname=lastname,
                country=country,
                birthday=birthday,
                gender=gender,
                paraclimbing_sport_class=paraclimbing_sport_class,
                height=height,
                age=age,
                years_active=years_active,
                prior_participations=prior_participations,
                qualification_rank=qualification_data.get("rank", None),
                qualification_score=qualification_data.get("score", None),
                semi_final_rank=semi_final_data.get("rank", None),
                semi_final_score=semi_final_data.get("score", None),
                final_rank=final_data.get("rank", None),
                final_score=final_data.get("score", None)
            )
