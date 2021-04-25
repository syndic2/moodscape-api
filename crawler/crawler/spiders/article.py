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
            url= element_box.css('a.sc-htoDjs.sc-jTzLTM.kmMpkI').attrib['href']
            
            yield response.follow(url, callback= self.parseData)
    
    def parseData(self, response):
        element= response.css('div.sc-cSHVUG.kTHmUf')
        article= ArticleItem()

        article['title']= element.css('h1.sc-htoDjs.iRWfRb.poppins::text').get()
        article['short_summary']= element.css('span.sc-htoDjs.ffgJvF::text').get()
        article['author']= element.css('a.sc-htoDjs.sc-jTzLTM.gQSQpq.Anchor-NexLink::text')[0].get()
        article['posted_at']= element.css('span.sc-htoDjs.kpiNV::text').get()
        article['reviewed_by']= element.css('a.sc-htoDjs.sc-jTzLTM.gQSQpq.Anchor-NexLink::text')[1].get()
        article['header_img']= element.css('picture.sc-Rmtcm.vvRNj img').attrib['src']
        article['content']= BeautifulSoup(element.css('div.sc-htpNat.eGAHHA').get()).get_text()
        article['url_name']= article['title'].lower().replace(', ', ' ').replace(' ', '-')
        article['url']= response.url

        yield article

        #yield {
        #    'title': article.css('h1.sc-htoDjs.iRWfRb.poppins::text').get(),
        #    'short_summary': article.css('span.sc-htoDjs.ffgJvF::text').get(),
        #    'author': article.css('a.sc-htoDjs.sc-jTzLTM.gQSQpq.Anchor-NexLink::text')[0].get(),
        #    'posted_at': article.css('span.sc-htoDjs.kpiNV::text').get(),
        #    'reviewed_by': article.css('a.sc-htoDjs.sc-jTzLTM.gQSQpq.Anchor-NexLink::text')[1].get(),
        #    'head_img': article.css('picture.sc-Rmtcm.vvRNj img').attrib['src'],
        #    'content': BeautifulSoup(article.css('div.sc-htpNat.eGAHHA').get()).get_text()
        #}
    
    def extract_content(content):
        pass
