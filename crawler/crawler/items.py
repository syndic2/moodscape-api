# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ArticleItem(scrapy.Item):
    title= scrapy.Field()
    short_summary= scrapy.Field()
    author= scrapy.Field()
    posted_at= scrapy.Field()
    reviewed_by= scrapy.Field()
    header_img= scrapy.Field()
    content= scrapy.Field()
    url= scrapy.Field()
