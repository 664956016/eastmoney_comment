# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EastmoneyCommentItem(scrapy.Item):
    # define the fields for your item here like:
    title_name = scrapy.Field()
    publisher = scrapy.Field()
    reading_num = scrapy.Field()
    comment_num = scrapy.Field()
    pub_time = scrapy.Field()
    url = scrapy.Field()

    #the is in the second layer page
    content = scrapy.Field()

    #this is in deeper layer page
    reader_comment = scrapy.Field()
