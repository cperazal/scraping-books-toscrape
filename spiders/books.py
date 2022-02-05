# -*- coding: utf-8 -*-
import os
import glob
from scrapy import Spider
from scrapy.http import Request

def product_information(response, value):
    return response.xpath(
        f'//th[text()="{value}"]/following-sibling::td/text()').extract_first()

class BooksSpider(Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['http://books.toscrape.com']

    def __init__(self, category):
        self.start_urls = {category}

    def parse(self, response):
        books = response.xpath('//h3/a/@href').extract()
        for book in books:
            absolute_url = response.urljoin(book)
            yield Request(absolute_url, callback=self.parse_book)

        # pagina siguiente
        # next_page_url = response.xpath('//a[text()="next"]/@href').extract_first()
        # absolute_next_page_url = response.urljoin(next_page_url)
        # yield Request(absolute_next_page_url)

    def parse_book(self, response):
        title = response.css('h1::text').extract_first()
        price = response.css('p::text').extract_first()
        url_img = response.xpath('//*[@class="item active"]/img/@src').extract_first()
        url_img = url_img.replace('../../','http://books.toscrape.com/')
        rating = response.xpath('//*[contains(@class, "star-rating")]/@class').extract_first()
        rating = rating.replace('star-rating ', '')
        description = response.xpath('//div[@id="content_inner"]/article/p//text()').extract_first()

        # product information
        upc = product_information(response, 'UPC')
        product_type = product_information(response, 'Product Type')
        price_excl_tax = product_information(response, 'Price (excl. tax)')
        price_incl_tax = product_information(response, 'Price (incl. tax)')
        tax = product_information(response, 'Tax')
        availability = product_information(response, 'Availability')
        numbers_view = product_information(response, 'Number of reviews')

        yield {
            'title': title,
            'price': price,
            'url_img': url_img,
            'rating': rating,
            'upc': upc,
            'product_type': product_type,
            'price_excl_tax': price_excl_tax,
            'price_incl_tax': price_incl_tax,
            'tax': tax,
            'availability': availability,
            'numers_view': numbers_view,
            'description': description
        }

    def close(self, reason):
        csv_file = max(glob.iglob('*.csv'), key=os.path.getctime)
        os.rename(csv_file, 'resultado.csv')