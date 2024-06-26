import scrapy
import requests
import json
from scrapy.spiders import Spider
from ..items import EventItem, CategoryItem, AthleteItem, EntryItem

# URLs of the website
domain_name = "ifsc-climbing.org"
base_url = f"https://{domain_name}"
api_url = f"{base_url}/api/dapi"

# Passed parameters abbreviations and their full names
league_names = {
    "wc": "World Cups and World Championships",
    "y": "IFSC Youth",
    "pc": "IFSC Paraclimbing (L)",
    "aa": "IFSC Asia Adults",
    "ay": "IFSC Asia Youth",
    "ea": "IFSC Europe Adults",
    "ey": "IFSC Europe Youth",
    "pa": "IFSC Panam",
    "oc": "IFSC Oceania",
    "g": "Games",
    "oe": "Other events",
    "m": "Masters and Promotional Events"
}

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

    def __init__(self, years, leagues, disciplines, categories, *args, **kwargs):
        super(IfscClimbingOrgSpider, self).__init__(*args, **kwargs)
        self.years = years.split(',')
        self.leagues = [league_names[league] for league in leagues.split(',')]
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
        for event in json_data['items']:
            event_url = event['url']
            event_name = event['title']
            event_date = event['fields']['dateFrom'][0:10]
            yield scrapy.Request(
                f"{event_url}result/index",
                callback=self.parse_event,
                cb_kwargs={"date": event_date}
            )

# Gather the full result URLs for the given event, discipline kinds and categories
    def parse_event(self, response, date):
        text_data = response.text

        # Extract the event page URL from the response
        start_str = "pageName\\\",\\\""
        end_str = "\\\","
        start_index = text_data.find(start_str)
        end_index = text_data.find(end_str, start_index + len(start_str))
        event_page = text_data[start_index + len(start_str):end_index]
        event_url = f"https://www.{domain_name}/{event_page}"

        # Extract the event ID from the response
        start_str = "eventId\\\":\\\""
        end_str = "\\\","
        start_index = text_data.find(start_str)
        end_index = text_data.find(end_str, start_index + len(start_str))
        event_id = text_data[start_index + len(start_str):end_index]

        # Extract the discipline & category IDs from the response
        start_str = "navigationItems\\\":"
        end_str = ",\\\"defaultDisciplinePath"
        start_index = text_data.find(start_str)
        end_index = text_data.find(end_str, start_index + len(start_str))
        event_data = text_data[start_index + len(start_str):end_index].replace("\\", "")
        event_data = json.loads(event_data)

        for category_id, category_data in event_data.items():
            if category_data['discipline'] in self.disciplines and category_data['category'] in self.categories:
                payload = [{"event_id": event_id, "id": category_id}]
                yield scrapy.Request(
                    event_url,
                    callback=self.parse_results,
                    method="POST",
                    headers={"Next-Action": "efa2fa106f24654dd09188f3c815302653521600"},
                    body=json.dumps(payload),
                    cb_kwargs={"date": date, "category_id": category_id},
                )

# Gather data from the full results of the given event
    def parse_results(self, response, date, category_id):
        data = response.text
        separator_index = data.find("1:")
        data = data[separator_index + 2:].strip()
        event_data = json.loads(data)["data"]