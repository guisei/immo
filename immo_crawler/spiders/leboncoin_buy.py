# -*- coding: utf-8 -*-
import scrapy
from immo_crawler.items import ImmoCrawlerItem
import re


class ListingsSpider(scrapy.Spider):
    name = 'leboncoin_buy'
    allowed_domains = ['leboncoin.fr']
    start_urls = ['https://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/paris/?th=1&ret=1&ret=2']
    urls = []

    def parse(self, response):
        urls = response.xpath("//*[@id='listingAds']/section/section/ul/li/a/@href").extract()
        for url in urls:
            url = "https:" + str(url)
            #if this listing already exists in the database (list self.urls) then we don't open it and remove this url from the list. After the script is finished, we update status = 0 for all urls that was not delete (see pipelines.py)
            if url in self.urls:
                self.urls.remove(url)
                continue
            yield scrapy.Request(url=url, callback=self.parse_details)
            # follow pagination link
        for next_url in response.xpath('//div[@class="pagination_links_container"]/a/@href').extract():
            yield scrapy.Request(url="https:" + next_url, callback=self.parse)
        return

    def parse_details(self, response):
        items = ImmoCrawlerItem()
        items['listingId'] = response.xpath("//span[@class='flat-horizontal saveAd link-like']/@data-savead-id").extract_first()
        items['url'] = "https:" + response.xpath("//head/meta[@property='og:url']/@content").extract_first()
        items['title'] = response.xpath("//h1[@itemprop='name']/text()").extract_first().strip()
        items['date'] = response.xpath("//p[@itemprop='availabilityStarts']/@content").extract_first()
        price = response.xpath("//h2[span='Prix']/span[@class='value']/text()").extract_first()
        #sometimes, the price doest not exist on the listing and if the price doesn't exist then variable is None, but None not has method .strip() and the script has error in this case
        if price:
            items['price'] = price.strip()
        #this structure allows to take into account the cities that have two words
        items['zip_code'] = response.xpath("//h2/span[@itemprop='address']/text()").extract_first().strip().split()[-1]
        items['city'] = \
            ' '.join(response.xpath("//h2/span[@itemprop='address']/text()").extract_first().strip().split()[:-1])
        items['propertyType'] = response.xpath("//h2[span='Type de bien']/span[@class='value']/text()").extract_first()
        items['rooms'] = response.xpath(u"//h2[span='Pièces']/span[@class='value']/text()").extract_first()
        items['superficy'] = response.xpath("//h2[span='Surface']/span[@class='value']/text()").extract_first()
        items['description'] = ' '.join(response.xpath("//div/p[@itemprop='description']/text()").extract())
        # urls for image contains into <script> tag. Using RegExp for get image urls directly from source code
        images = ['http:' + image for image in set(re.findall(r'"(.*?/ad-large/.*?)";', response.body))]
        items['time'] = response.xpath('//p[@itemprop="availabilityStarts"]/text()').re_first(r'\d\d:\d\d')
        items['status'] = '1'
        items['file_urls'] = images
        yield items
