# -*- coding: utf-8 -*-
import scrapy
from immo_crawler.items import ImmoCrawlerItem
import re


class PapFrSpider(scrapy.Spider):
    name = 'pap_fr'
    allowed_domains = ['pap.fr']
    start_urls = ['http://www.pap.fr/annonce/vente-appartement-maison-paris-75-g439']

    def parse(self, response):
        for url in response.css('a.btn-details::attr(href)').extract():
            # if url in self.urls:
            #    self.urls.remove(url)
            #    continue
            yield response.follow(url, self.parse_details)
            url = 'http://www.pap.fr/annonces/maison-paris-16e-r416900442'
            yield response.follow(url, self.parse_details)
            # break
            # follow pagination link
        for next_url in response.css('div.pagination a::attr(href)').extract():
            yield response.follow(next_url)
        return

    def parse_details(self, response):
        item = ImmoCrawlerItem()
        item['listingId'] = response.url.split('-')[-1][1:]
        item['url'] = response.url
        item['title'] = response.css("h1 span::text").extract_first().strip()
        item['date'] = response.css("p.date::text").extract_first().split('/')[-1].strip()
        item['price'] = response.css('span.price strong::text').extract_first()
        item['zip_code'] = response.css('div.item-geoloc h2::text').re_first(r'\((\d+)\)')
        item['city'] = response.css('div.item-geoloc h2::text').re_first(r'\A(\D+) | (\D) ')
        # item['propertyType'] = response.xpath("//h2[span='Type de bien']/span[@class='value']/text()").extract_first()
        item['rooms'] = \
            response.xpath(u'//ul[@class="item-summary"]/li[contains(text(),"Pièce")]/strong/text()').extract_first()
        item['superficy'] = \
            response.xpath('//ul[@class="item-summary"]/li[contains(text(),"Surface")]/strong/text()').extract_first()
        item['description'] = ' '.join(' '.join(response.css("p.item-description::text").extract()).split())
        images = response.css('div.owl-thumbs a img::attr(src)').extract()
        item['status'] = '1'
        item['file_urls'] = images
        yield item
