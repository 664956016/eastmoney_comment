# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json, os
from scrapy.utils.project import get_project_settings

def reopen_dir():
	if not os.path.exists('gupiao_comments/'):
		os.mkdir('gupiao_comments/')
		path = os.path.join(os.getcwd(), 'gupiao_comments/')
	else:
		path = os.path.join(os.getcwd(), 'gupiao_comments/')
	return path

# settings = get_project_settings()
# code_name = reopen_dir() + settings['ST_URL'] + '.txt'

class EastmoneyCommentPipeline(object):
    def process_item(self, item, spider):
        with open(code_name, 'a') as f:
            f.write(str(item)+'\n')
        return item


class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('items.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
###################################################################
###################################################################
#Using mongodb

import pymongo

class MongoPipeline(object):

    collection_name = 'eastmoney_comments'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'es_comments')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item