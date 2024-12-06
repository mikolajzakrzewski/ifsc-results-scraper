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
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    location = scrapy.Field()


class AthleteItem(scrapy.Item):
    athlete_id = scrapy.Field()
    firstname = scrapy.Field()
    lastname = scrapy.Field()
    country = scrapy.Field()
    birthday = scrapy.Field()
    gender = scrapy.Field()
    paraclimbing_sport_class = scrapy.Field()
    height = scrapy.Field()
    speed_personal_best_score = scrapy.Field()
    speed_personal_best_date = scrapy.Field()
    speed_personal_best_round = scrapy.Field()


class EntryItem(scrapy.Item):
    event_id = scrapy.Field()
    discipline = scrapy.Field()
    category = scrapy.Field()
    athlete_id = scrapy.Field()
    rank = scrapy.Field()
    age = scrapy.Field()
    years_active = scrapy.Field()
    prior_participations = scrapy.Field()
    qualification_rank = scrapy.Field()
    qualification_score = scrapy.Field()
    semi_final_rank = scrapy.Field()
    semi_final_score = scrapy.Field()
    final_rank = scrapy.Field()
    final_score = scrapy.Field()


class FileEntryItem(scrapy.Item):
    event = scrapy.Field()
    event_start_date = scrapy.Field()
    event_end_date = scrapy.Field()
    discipline = scrapy.Field()
    category = scrapy.Field()
    athlete_id = scrapy.Field()
    rank = scrapy.Field()
    firstname = scrapy.Field()
    lastname = scrapy.Field()
    country = scrapy.Field()
    birthday = scrapy.Field()
    gender = scrapy.Field()
    paraclimbing_sport_class = scrapy.Field()
    height = scrapy.Field()
    age = scrapy.Field()
    years_active = scrapy.Field()
    prior_participations = scrapy.Field()
    qualification_rank = scrapy.Field()
    qualification_score = scrapy.Field()
    semi_final_rank = scrapy.Field()
    semi_final_score = scrapy.Field()
    final_rank = scrapy.Field()
    final_score = scrapy.Field()
