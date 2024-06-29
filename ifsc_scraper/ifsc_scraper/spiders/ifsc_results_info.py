# import scrapy
# import requests
# import json
# from scrapy.spiders import Spider
# from ..items import EventItem, CategoryItem, AthleteItem, EntryItem, FileEntryItem
#
# # URLs of the result service and its API
# domain_name = "ifsc.results.info"
# base_url = f"https://{domain_name}"
# api_url = f"{base_url}/api/v1"
#
# # Year IDs used by the result service for years 1990-2024
# year_ids = {
#     "1990": 3,
#     "1991": 4,
#     "1992": 5,
#     "1993": 6,
#     "1994": 7,
#     "1995": 8,
#     "1996": 9,
#     "1997": 10,
#     "1998": 11,
#     "1999": 12,
#     "2000": 13,
#     "2001": 14,
#     "2002": 15,
#     "2003": 16,
#     "2004": 17,
#     "2005": 18,
#     "2006": 19,
#     "2007": 20,
#     "2008": 21,
#     "2009": 22,
#     "2010": 23,
#     "2011": 24,
#     "2012": 25,
#     "2013": 26,
#     "2014": 27,
#     "2015": 28,
#     "2016": 29,
#     "2017": 30,
#     "2018": 31,
#     "2019": 32,
#     "2020": 2,
#     "2021": 33,
#     "2022": 34,
#     "2023": 35,
#     "2024": 36,
# }
#
# # Passed parameters abbreviations and their full names
# league_names = {
#     "wc": "World Cups and World Championships",
#     "y": "IFSC Youth",
#     "pc": "IFSC Paraclimbing (L)",
#     "aa": "IFSC Asia Adults",
#     "ay": "IFSC Asia Youth",
#     "ea": "IFSC Europe Adults",
#     "ey": "IFSC Europe Youth",
#     "pa": "IFSC Panam",
#     "oc": "IFSC Oceania",
#     "g": "Games",
#     "oe": "Other events",
#     "m": "Masters and Promotional Events"
# }
#
# discipline_names = {
#     "l": "lead",
#     "s": "speed",
#     "b": "boulder",
#     "c": "combined",
#     "bl": "boulder&lead"
# }
#
# category_names = {
#     "m": "Men",
#     "w": "Women",
#     "yam": "Youth A Male",
#     "yaf": "Youth A Female",
#     "ybm": "Youth B Male",
#     "ybf": "Youth B Female",
#     "jm": "Juniors Male",
#     "jf": "Juniors Female"
# }
#
#
# # Spider class for scraping the results from the IFSC result service
# class IfscResultsInfoSpider(Spider):
#     name = "ifsc_results_info"
#     allowed_domains = [domain_name]
#     custom_settings = {
#         'FEEDS': {
#             'results_%(name)s_%(time)s.csv': {
#                 'format': 'csv',
#                 'encoding': 'utf8',
#                 'store_empty': False,
#                 'item_classes': [FileEntryItem, 'ifsc_scraper.items.FileEntryItem'],
#                 'fields': [
#                     'date',
#                     'event',
#                     'athlete_id',
#                     'rank',
#                     'firstname',
#                     'lastname',
#                     'country',
#                     'birthday',
#                     'gender',
#                     'height',
#                     'age',
#                     'years_active',
#                     'prior_participations',
#                     'round_scores'
#                 ],
#                 'item_export_kwargs': {
#                     'export_empty_fields': True
#                 }
#             }
#         }
#     }
#
#     def __init__(self, years, leagues, disciplines, categories, *args, **kwargs):
#         super(IfscResultsInfoSpider, self).__init__(*args, **kwargs)
#         self.years = years.split(',')
#         self.leagues = [league_names[league] for league in leagues.split(',')]
#         self.disciplines = [discipline_names[discipline] for discipline in disciplines.split(',')]
#         self.categories = [category_names[category] for category in categories.split(',')]
#         self.start_urls = [f"{api_url}/seasons/{year_ids[year]}" for year in self.years]
#
#     def start_requests(self):
#         for url in self.start_urls:
#             yield scrapy.Request(
#                 url,
#                 callback=self.parse_year,
#                 headers={"Referer": base_url}
#             )
#
# # Gather the event IDs for the given year, leagues and discipline kinds
#     def parse_year(self, response):
#         json_data = json.loads(response.text)
#         for league_name in self.leagues:
#             league = next((league for league in json_data["leagues"] if league["name"] == league_name), None)
#
#             if league:
#                 league_url = league["url"]
#                 league_season_id = league_url[league_url.rfind("/") + 1:len(league_url)]
#                 for event in json_data["events"]:
#                     if next(
#                             (discipline for discipline in event["disciplines"] if
#                              discipline["kind"] in self.disciplines), None
#                     ) is not None and str(event["league_season_id"]) == league_season_id:
#                         event_id = event["event_id"]
#                         yield scrapy.Request(
#                             f"{api_url}/events/{event_id}",
#                             callback=self.parse_event,
#                             headers={"Referer": base_url},
#                         )
#
# # Gather the full result URLs for the given event, discipline kinds and categories
#     def parse_event(self, response):
#         json_data = json.loads(response.text)
#         date = json_data["starts_at"][0:10]
#
#         # Save the event information to the database
#         event_id = json_data["id"]
#         event_name = json_data["name"]
#         event_date = date
#         event_country = json_data["country"]
#
#         # Create an event item and save it to the database
#         yield EventItem(
#             event_id=event_id,
#             name=event_name,
#             date=event_date,
#             location=event_country
#         )
#
#         # Save the categories' information to the database
#         for d_cat in json_data["d_cats"]:
#             if d_cat["discipline_kind"] in self.disciplines and d_cat["category_name"] in self.categories:
#                 full_result_url = d_cat["full_results_url"]
#                 category_id = d_cat["dcat_id"]
#                 event_id = event_id
#                 category_discipline = d_cat["discipline_kind"]
#                 category_name = d_cat["category_name"]
#
#                 # Create a category item and save it to the database
#                 yield CategoryItem(
#                     category_id=category_id,
#                     event_id=event_id,
#                     discipline=category_discipline,
#                     name=category_name
#                 )
#
#                 # Process the full result URL
#                 yield scrapy.Request(
#                     base_url + full_result_url,
#                     callback=self.parse_results,
#                     cb_kwargs={"date": date, "category_id": category_id},
#                     headers={"Referer": base_url},
#                 )
#
# # Gather data from the full results of the given event
#     def parse_results(self, response, date, category_id):
#         year = date[0:4]
#         json_data = json.loads(response.text)
#         event_name = json_data["event"]
#         for athlete in json_data["ranking"]:
#             athlete_id = athlete["athlete_id"]
#             rank = athlete["rank"]
#
#             round_scores = [
#                 {"round_name": round_type["round_name"],
#                  "rank": round_type["rank"],
#                  "score": round_type["score"]}
#                 for round_type in athlete["rounds"]]
#
#             round_scores_json = json.dumps(round_scores)
#
#             # Gather information from the athlete's API endpoint
#             athlete_info = json.loads(
#                 requests.get(f"{api_url}/athletes/{athlete_id}", headers={'Referer': base_url}).text
#             )
#
#             firstname = athlete_info["firstname"]
#             lastname = athlete_info["lastname"]
#             country = athlete_info["country"]
#             birthday = athlete_info["birthday"]
#             gender = athlete_info["gender"]
#             paraclimbing_sport_class = athlete_info["paraclimbing_sport_class"]
#             height = athlete_info["height"]
#             # Note: since it is only possible to determine a climber's current height,
#             #       the parameter may be inaccurate for young climbers
#
#             speed_personal_best_score = athlete_info["speed_personal_best"]["time"]
#             speed_personal_best_date = athlete_info["speed_personal_best"]["date"]
#             speed_personal_best_round = athlete_info["speed_personal_best"]["round_name"]
#
#             # Create an athlete item and save it to the database
#             yield AthleteItem(
#                 athlete_id=athlete_id,
#                 firstname=firstname,
#                 lastname=lastname,
#                 country=country,
#                 birthday=birthday,
#                 gender=gender,
#                 paraclimbing_sport_class=paraclimbing_sport_class,
#                 height=height,
#                 speed_personal_best_score=speed_personal_best_score,
#                 speed_personal_best_date=speed_personal_best_date,
#                 speed_personal_best_round=speed_personal_best_round
#             )
#
#             # Climbers' age is rounded down to the nearest year (general rule in climbing competitions)
#             if athlete_info["birthday"] is None:
#                 age = None
#             else:
#                 age = int(year) - int(athlete_info["birthday"][0:4])
#
#             # Calculate the number of years the athlete has been active in the IFSC based on the first documented result
#             first_activity_year = int(athlete_info["all_results"][-1]["season"])
#             years_active = int(year) - first_activity_year
#             prior_participations = 0
#             for result in reversed(athlete_info["all_results"]):
#                 if result["date"] > date:
#                     break
#                 else:
#                     prior_participations += 1
#
#             yield EntryItem(
#                 category_id=category_id,
#                 athlete_id=athlete_id,
#                 rank=rank,
#                 age=age,
#                 years_active=years_active,
#                 prior_participations=prior_participations,
#                 round_scores=round_scores_json
#             )
#
#             # Create a file entry item and save it to a file
#             yield FileEntryItem(
#                 date=date,
#                 event=event_name,
#                 athlete_id=athlete_id,
#                 rank=rank,
#                 firstname=firstname,
#                 lastname=lastname,
#                 country=country,
#                 birthday=birthday,
#                 gender=gender,
#                 paraclimbing_sport_class=paraclimbing_sport_class,
#                 height=height,
#                 age=age,
#                 years_active=years_active,
#                 prior_participations=prior_participations,
#                 round_scores=json.dumps(round_scores),
#             )
