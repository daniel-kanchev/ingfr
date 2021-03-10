import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from ingfr.items import Article


class IngfrSpider(scrapy.Spider):
    name = 'ingfr'
    start_urls = ['https://newsroom.ing.fr/']

    def parse(self, response):
        links = response.xpath('//ul[@id="nav-1"]/li/a/@href').getall()[1:]
        yield from response.follow_all(links, self.parse_category)

    def parse_category(self, response):
        links = response.xpath('//a[@class="read-more"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="title-cp-dp"]/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@id="ban_cp_top"]/p[2]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="entry-content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
