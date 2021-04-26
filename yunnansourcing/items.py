# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class YunnansourcingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    collection = scrapy.Field()
    item_name = scrapy.Field()
    item_type = scrapy.Field()
    pid = scrapy.Field()
    display_price = scrapy.Field()
    pricing = scrapy.Field()
    brand = scrapy.Field()
    amount = scrapy.Field()
    tags = scrapy.Field()
    notes = scrapy.Field()
    wishlist_score = scrapy.Field()
    starscore = scrapy.Field()
    review_titles = scrapy.Field()
    review_names = scrapy.Field()
    review_scores = scrapy.Field()
    review_dates = scrapy.Field()
    review_texts = scrapy.Field()
    review_helpful = scrapy.Field()
    review_unhelpful = scrapy.Field()
