import scrapy
import json
import re
from unidecode import unidecode
from scrapy.spiders import Spider
from ..items import EventItem, CategoryItem, AthleteItem, EntryItem

# URLs of the website
domain_name = "ifsc-climbing.org"
base_url = f"https://www.{domain_name}"
api_url = f"{base_url}/api/dapi"

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
        json_data = json.loads(response.text)
        print(json_data)
        for event in json_data['items']:
            event_url = event['url']
            event_name = event['title']
            event_date = event['fields']['dateFrom'][0:10]
            event_location = event['fields']['location']
            yield scrapy.Request(
                f"{event_url}result/index",
                callback=self.parse_event,
                cb_kwargs={"event_name": event_name, "event_date": event_date, "event_location": event_location}
            )

# Gather the full result URLs for the given event, discipline kinds and categories
    def parse_event(self, response, event_name, event_date, event_location):
        text_data = response.text

        # Extract the event page URL from the response
        event_url = response.url

        # Extract the event ID from the response
        start_str = "eventId\\\":\\\""
        end_str = "\\\","
        start_index = text_data.find(start_str)
        end_index = text_data.find(end_str, start_index + len(start_str))
        # TODO: dont save events that dont fit the criteria
        if start_index != -1 and end_index != -1:
            event_id = text_data[start_index + len(start_str):end_index]
            yield EventItem(
                event_id=event_id,
                name=event_name,
                date=event_date,
                location=event_location
            )

        # Extract the discipline & category IDs from the response
        start_str = "navigationItems\\\":"
        end_str = ",\\\"defaultDisciplinePath"
        start_index = text_data.find(start_str)
        end_index = text_data.find(end_str, start_index + len(start_str))
        event_data = text_data[start_index + len(start_str):end_index].replace("\\", "")
        event_data = json.loads(event_data)

        for category_id, category_data in event_data.items():
            if category_data['discipline'] in self.disciplines and category_data['category'] in self.categories:
                headers = {
                    "Next-Action": "efa2fa106f24654dd09188f3c815302653521600"
                }
                payload = [{"event_id": event_id, "id": category_id}]
                yield CategoryItem(
                    event_id=event_id,
                    category_id=category_id,
                    discipline=category_data['discipline'],
                    name=category_data['category']
                )

                yield scrapy.Request(
                    event_url,
                    callback=self.parse_results,
                    method="POST",
                    headers=headers,
                    body=json.dumps(payload),
                    cb_kwargs={"event_date": event_date, "category_id": category_id},
                )

# Gather data from the full results of the given event
    def parse_results(self, response, event_date, category_id):
        response.encoding = 'utf-8'
        data = response.text
        separator_index = data.find("1:")
        data = data[separator_index + 2:].strip()
        ranking = json.loads(data)["data"]["ranking"]
        for athlete in ranking:
            athlete_id = athlete["athlete_id"]
            rank = athlete["rank"]

            # Convert the athlete's name to a URL-friendly format
            name = athlete["firstname"] + " " + athlete["lastname"].strip()
            name = unidecode(name)
            name = name.lower()
            name = re.sub(r"[^a-z]", "-", name)

            # Combine the athlete's name with the athlete's ID to form the athlete's URL
            athlete_url = f"{base_url}/athlete/{athlete_id}/{name}"
            # yield scrapy.Request(
            #     athlete_url,
            #     callback=self.parse_athlete,
            #     cb_kwargs={"rank": rank, "event_date": event_date, "category_id": category_id}
            # )

    def parse_athlete(self, response, rank, event_date, category_id):
        response.encoding = 'utf-8'
        data = response.text
        pass

    def parse_entry(self, response, rank, event_date, category_id):
        pass
