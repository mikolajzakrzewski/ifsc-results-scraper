import json
import scrapy
import requests
from scrapy.spiders import Spider

# URLs of the result service and its API
domain_name = "ifsc.results.info"
base_url = f"https://{domain_name}"
api_url = f"{base_url}/api/v1"

# Year IDs used by the result service for years 1990-2024
year_ids = {
    "1990": 3,
    "1991": 4,
    "1992": 5,
    "1993": 6,
    "1994": 7,
    "1995": 8,
    "1996": 9,
    "1997": 10,
    "1998": 11,
    "1999": 12,
    "2000": 13,
    "2001": 14,
    "2002": 15,
    "2003": 16,
    "2004": 17,
    "2005": 18,
    "2006": 19,
    "2007": 20,
    "2008": 21,
    "2009": 22,
    "2010": 23,
    "2011": 24,
    "2012": 25,
    "2013": 26,
    "2014": 27,
    "2015": 28,
    "2016": 29,
    "2017": 30,
    "2018": 31,
    "2019": 32,
    "2020": 2,
    "2021": 33,
    "2022": 34,
    "2023": 35,
    "2024": 36,
}

# TODO: Make the following parameters configurable
league_name = "World Cups and World Championships"
discipline_kind = "speed"
category_name = "Men"


# Spider class for scraping the results from the IFSC result service
class IfscResultsInfoSpider(Spider):
    name = "ifsc_results_info"
    allowed_domains = [domain_name]
    start_urls = [f"{api_url}/seasons/{year_ids['2008']}"]
    # start_urls = [f"{api_url}seasons/{year_id}" for year_id in year_ids.values()]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse_year,
                headers={"Referer": base_url}
            )

# Gather the event IDs for the given year, leagues and discipline kinds
    def parse_year(self, response):
        json_data = json.loads(response.text)
        league = next(league for league in json_data["leagues"]
                      if league["name"] == league_name)
        league_url = league["url"]
        league_season_id = league_url[league_url.rfind("/") + 1:len(league_url)]
        event_ids = []
        for event in json_data["events"]:
            if next(
                    (discipline for discipline in event["disciplines"] if discipline["kind"] == discipline_kind), None
            ) is not None and str(event["league_season_id"]) == league_season_id:
                event_ids.append(event["event_id"])

        for event_id in event_ids:
            yield scrapy.Request(
                f"{api_url}/events/{event_id}",
                callback=self.parse_event,
                cb_kwargs={"year": json_data["name"]},
                headers={"Referer": base_url},
            )

# Gather the full result URLs for the given event, discipline kinds and categories
    def parse_event(self, response, year):
        json_data = json.loads(response.text)
        full_result_urls = []
        for d_cat in json_data["d_cats"]:
            if d_cat["discipline_kind"] == discipline_kind and d_cat["category_name"] == category_name:
                full_result_urls.append(d_cat["full_results_url"])

        for full_result_url in full_result_urls:
            yield scrapy.Request(
                base_url + full_result_url,
                callback=self.parse_results,
                cb_kwargs={"year": year},
                headers={"Referer": base_url},
            )

# Gather data from the full results of the given event
    def parse_results(self, response, year):
        json_data = json.loads(response.text)
        event = json_data["event"]
        for athlete in json_data["ranking"]:
            athlete_id = athlete["athlete_id"]
            rank = athlete["rank"]
            round_scores = {}
            for round_type in athlete["rounds"]:
                round_name = round_type["round_name"]
                round_scores[round_name] = round_type["score"]

            # Gather basic personal information about the athlete
            firstname = athlete["firstname"]
            lastname = athlete["lastname"]
            country = athlete["country"]

            # Gather additional information from the athlete's API endpoint
            athlete_info = json.loads(
                requests.get(f"{api_url}/athletes/{athlete_id}", headers={'referer': base_url}).text
            )

            # Climbers' age is rounded down to the nearest year (general rule in climbing competitions)
            if athlete_info["birthday"] is None:
                age = None
            else:
                age = int(year) - int(athlete_info["birthday"][0:4])

            height = athlete_info["height"]
            # Note: since it is only possible to determine a climber's current height,
            #       the parameter may be inaccurate for young climbers

            # Calculate the number of years the athlete has been active in the IFSC based on the first documented result
            first_activity_year = int(athlete_info["all_results"][-1]["season"])
            years_active = int(year) - first_activity_year

            yield {
                "year": year,
                "event": event,
                "athlete_id": athlete_id,
                "rank": rank,
                "firstname": firstname,
                "lastname": lastname,
                "age": age,
                "height": height,
                "years_active": years_active,
                "country": country,
                "round_scores": round_scores,
            }
