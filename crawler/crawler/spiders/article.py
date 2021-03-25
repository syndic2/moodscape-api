import scrapy

class ArticleSpider(scrapy.Spider):
    name= 'articles'
    start_urls = [
        'http://https://www.sehatq.com/artikel/kesehatan-mental?page=1/'
    ]

    def parse(self, response):
        pass
