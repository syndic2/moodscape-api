import scrapy

class BookSpider(scrapy.Spider):
    name= 'books'
    start_urls= [
        'https://books.toscrape.com/'
    ]

    def parse(self, response):
        rating_numbers= {
            'One': 1,
            'Two': 2,
            'Three': 3,
            'Four': 4,
            'Five': 5
        }

        for book in response.css('ol.row').css('article.product_pod'):
            rating_text= book.css('p.star-rating').attrib['class'].split()[-1]

            yield {
                'title': book.css('h3 a::text').get(),
                'price': book.css('div.product_price p.price_color::text').get(),
                'availability': book.css('div.product_price p.instock.availability::text').getall()[1].strip(),
                'rating_text': rating_text,
                'rating_count': [v for k, v in rating_numbers.items() if k in rating_text][0],
                'img_url': f"https://books.toscrape.com/{book.css('div.image_container img.thumbnail').attrib['src']}"
            }
