# -*- coding: utf-8 -*-
from scrapy.pipelines.files import FilesPipeline
import scrapy
import MySQLdb
from scrapy.conf import settings
import logging
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ImmoCrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


class MySQLPipeline(object):
    conn = MySQLdb.connect(host=settings.get('DB_HOST'), user=settings.get('DB_USER'), port=settings.get('DB_PORT'),
                           passwd=settings.get('DB_PASSWORD'), db=settings.get('DB_BASE'), charset='utf8')
    cur = conn.cursor()
    cur.execute('SET names UTF8')
    table = settings.get('DB_TABLE')
    update_for_duplicate = settings.get('UPDATE_FOR_DUPLICATE')

    def open_spider(self, spider):
        logging.info('LOADING URL...')
        query = "SELECT url FROM {} WHERE status=1".format(self.table)
        self.cur.execute(query)
        spider.urls = [str(row[0]) for row in self.cur.fetchall()]
        print len(spider.urls)
        return

    def close_spider(self, spider):
        print len(spider.urls)
        query = 'UPDATE {} SET status = 0 WHERE url in ("{}")'.format(self.table, '","'.join(spider.urls))
        # print query
        self.cur.execute(query)
        # print query
        self.conn.commit()
        return

    def process_item(self, item, spider):
        del item['file_urls']
        keys = u'`, `'.join(item.keys())
        values = u"','".join([unicode(val).replace("'", "''").replace('\\', '\\\\') for val in item.values()])
        if self.update_for_duplicate:
            update = ', '.join([u"`{}` = '{}'".format(
                key, unicode(item[key]).replace("'", "''").replace('\\', '\\\\')) for key in item])
            query = u"INSERT INTO {} (`{}`) VALUES ('{}') ON DUPLICATE KEY UPDATE {}".format(
                self.table, keys, values, update)
        else:
            query = u"INSERT INTO {} (`{}`) VALUES ('{}')".format(self.table, keys, values)
        try:
            self.cur.execute(query)
            self.conn.commit()
        except MySQLdb.Error as e:
            logging.error(e)
            logging.error(u'BAD QUERY: {}'.format(query))
        return item


class ImmoCrawlerImagePipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        imgid = 1
        for image in item['file_urls']:
            yield scrapy.Request(image, meta={'file_path': item['listingId'] + '_image' + str(imgid)})
            imgid += 1

    def file_path(self, request, response=None, info=None):
        return request.meta['file_path']
