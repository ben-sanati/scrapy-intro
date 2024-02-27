# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class BookscraperItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class BookItem(Item):
    url = Field()
    title = Field()
    upc = Field()
    product_type = Field()
    price = Field()
    price_excluding_tax = Field()
    price_including_tax = Field()
    tax = Field()
    availability = Field()
    number_of_reviews = Field()
    stars = Field()
    category = Field()
    description = Field()
