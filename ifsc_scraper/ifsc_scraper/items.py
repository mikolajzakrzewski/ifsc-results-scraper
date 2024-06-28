# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IfscScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class EventItem(scrapy.Item):
    event_id = scrapy.Field()
    name = scrapy.Field()
    date = scrapy.Field()
    location = scrapy.Field()


class CategoryItem(scrapy.Item):
    category_id = scrapy.Field()
    event_id = scrapy.Field()
    discipline = scrapy.Field()
    name = scrapy.Field()


class AthleteItem(scrapy.Item):
    athlete_id = scrapy.Field()
    firstname = scrapy.Field()
    lastname = scrapy.Field()
    country = scrapy.Field()
    birthday = scrapy.Field()
    gender = scrapy.Field()
    height = scrapy.Field()
    speed_personal_best_score = scrapy.Field()
    speed_personal_best_date = scrapy.Field()
    speed_personal_best_round = scrapy.Field()


class EntryItem(scrapy.Item):
    category_id = scrapy.Field()
    athlete_id = scrapy.Field()
    rank = scrapy.Field()
    age = scrapy.Field()
    years_active = scrapy.Field()
    prior_participations = scrapy.Field()
    round_scores = scrapy.Field()


class FileEntryItem(scrapy.Item):
    date = scrapy.Field()
    event = scrapy.Field()
    athlete_id = scrapy.Field()
    rank = scrapy.Field()
    firstname = scrapy.Field()
    lastname = scrapy.Field()
    country = scrapy.Field()
    birthday = scrapy.Field()
    gender = scrapy.Field()
    height = scrapy.Field()
    age = scrapy.Field()
    years_active = scrapy.Field()
    prior_participations = scrapy.Field()
    round_scores = scrapy.Field()
