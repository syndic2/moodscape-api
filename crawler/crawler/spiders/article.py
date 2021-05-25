import scrapy
from bs4 import BeautifulSoup

from ..items import ArticleItem

#scrapyrt: http://localhost:9080/crawl.json?spider_name=articles&start_requests=True&crawl_args=%7B%22pages%22%3A%201%7D
class ArticleSpider(scrapy.Spider):
    name= 'articles'
    
    def __init__(self, pages= 1, *args, **kwargs):
        super(ArticleSpider, self).__init__(*args, **kwargs)
        
        if type(pages) == str:
            pages= int(pages)

        self.start_urls= [f"http://www.sehatq.com/artikel/kesehatan-mental?page={(page+1)}" for page in range(pages)]

    def parse(self, response):
        for element_box in response.css('div.sc-htpNat.ifZKKW'):
            url= element_box.css('a.sc-gZMcBi.sc-kAzzGY.krILH').attrib['href']
            
            yield response.follow(url, callback= self.parseData)
    
    def parseData(self, response):
        element= response.css('div.sc-kpOJdX.gUcjBw')
        article= ArticleItem()

        article['title']= element.css('h1.sc-gZMcBi.gIFFao.poppins::text').get()
        article['short_summary']= element.css('span.sc-gZMcBi.gQCEgT::text').get()
        article['author']= element.css('a.sc-gZMcBi.sc-kAzzGY.bdXpyA.Anchor-NexLink::text')[0].get()
        article['posted_at']= element.css('span.sc-gZMcBi.hhLaDY::text').get()
        article['reviewed_by']= element.css('a.sc-gZMcBi.sc-kAzzGY.bdXpyA.Anchor-NexLink::text')[0].get()
        #article['header_img']= element.css('picture.sc-feJyhm.gmuGxr img').attrib['src']
        
        if len(element.css('picture.sc-feJyhm.gmuGxr img')) > 0:
            article['header_img']= element.css('picture.sc-feJyhm.gmuGxr img').attrib['src']
        elif len(element.css('picture.sc-kafWEX.ilMpFx img')) > 0:
            article['header_img']= element.css('picture.sc-kafWEX.ilMpFx img').attrib['src']
        else:
            article['header_img']= 'https://via.placeholder.com/150'

        article['content']= BeautifulSoup(element.css('div.sc-htpNat.eGAHHA').get()).get_text()
        article['url_name']= article['title'].lower().replace(', ', ' ').replace(' ', '-')
        article['url']= response.url

        yield article
    
    def extract_content(content):
        pass
