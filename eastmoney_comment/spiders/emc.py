# -*- coding: utf-8 -*-
import scrapy, re
from eastmoney_comment.items import EastmoneyCommentItem
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from scrapy.utils.project import get_project_settings
from .crawl_stock_code import get_code_dict_and_list

#get all the code list
def get_start_urls():
    code_list = get_code_dict_and_list()  #total 2078 codes
    urls = []
    for code in code_list:
        sturl = 'http://guba.eastmoney.com/list,%s.html' % code
        urls.append(sturl)
    print(urls)
    return urls[1:200]
settings = get_project_settings()

# st_url = settings['ST_URL']
#choose the stock of yours, and input them
#st_url = input('Please input company code:')
#st_url = '002732'

#fill the comment_page by yourself
page_num = 39

#################################################################################################
#adding itemloader function to parse the results

def int_num(x):
    return int(x)
reading_num_proc = MapCompose(int_num)

def make_sentence(lst):
    sentence = ''
    for i in lst:
        sentence += i
    return sentence
sentence_proc = MapCompose(make_sentence)

def remove_symbol(lst):
    line = make_sentence(lst)
    result = re.sub(r"[\*,\t,\-,\+,\],\[]","",line)
    return result
remove_symbol_proc = MapCompose(remove_symbol)



####################################below is the spider class####################################
class EmcSpider(scrapy.Spider):
    name = "emc"
    # allowed_domains = ["http://guba.eastmoney.com"]
    # start_urls = ['http://guba.eastmoney.com/list,%s.html' % st_url]
    start_urls = get_start_urls()
    page_url_list = []

    def parse(self, response):
        links = response.xpath('//*[@class="articleh"]/span[3]/a/@href').extract()
        links_odd = response.xpath('//*[@class="articleh odd"]/span[3]/a/@href').extract()
        links_all = links + links_odd
        links_last = ['http://guba.eastmoney.com'+i for i in links_all if 'http' not in i]
        self.page_url_list += links_last
        # print(self.page_url_list, len(self.page_url_list))
        try:
            for url in self.page_url_list:
                yield scrapy.Request(url=url, callback=self.parse_font_page)
        except Exception as e:
            print(e)

        code_compile = re.compile(r'.*?(\d+).*?')
        _code = re.findall(code_compile, response.url)[0]
        next_urls = ['http://guba.eastmoney.com/list,'+_code+'_%s.html' %  i for i in range(2, page_num+1)]
        for next_link in next_urls:
            # print('next_link: ', next_link)
            yield scrapy.Request(url=next_link, callback=self.parse)


    def parse_font_page(self, response):
        l = ItemLoader(item=EastmoneyCommentItem(), response=response)

        #processing title_name
        raw_title_name = ["".join(i.split()) for i in response.xpath('//*[@class="zwcontentmain"]/div[1]/text()').extract()]
        l.add_value('title_name', make_sentence(raw_title_name))

        #processing content
        raw_content = ["".join(i.split()) for i in response.xpath('//*[@class="zwcontentmain"]/div[2]/div/text()').extract()]
        l.add_value('content', make_sentence(raw_content))
        l.add_xpath('publisher', '//*[@id="zwconttbn"]/strong/a/text()')

        #processing the reading number##############################
        # l.add_value('reading_num', response.text, re='<script>var num=(.*?);var count=.*?;</script>')
        read_num = re.findall(re.compile('<script>var num=(.*?);var count=.*?;</script>'), response.text)
        l.add_value('reading_num', reading_num_proc(read_num))

        # processing the comment number##############################
        # try:
        #     raw_comment_num = response.xpath('//*[@id="zwcontab"]/ul/li[1]/a/text()').extract()[0]
        #     comment_num = re.findall(r'.*?(\d+).', raw_comment_num)
        #     comment_num_proc = MapCompose(int_num)
        #     l.add_value('comment_num', comment_num_proc(comment_num))
        # except:
        #     pass

        re_com = re.compile('var pinglun_num=(.*?);')
        l.add_value('comment_num', re.findall(re_com, response.text))

        # processing the pub number##############################
        pub_time = re.findall(re.compile('<div class="zwfbtime">.*?(\d+-\d+-\d+).\d+:\d+:\d+.*?</div>'), response.text)
        l.add_value('pub_time', pub_time)

        reader_comment = response.xpath('//*[@class="zwlitext stockcodec"]/text()').extract()
        l.add_value('reader_comment', remove_symbol(reader_comment))

        l.add_value('url', response.url)
        # #reader comment page_number(30comments per page) and get url
        get_comment_num = l.load_item()['comment_num'][0]
        if get_comment_num:
            if int(get_comment_num) > 30:
                page_nums = int(get_comment_num) // 30 + 1
                for page_num in range(2, page_nums+1):
                    raw_url = 'http://guba.eastmoney.' + response.url.split('.')[-2] + '_' + '{}' + '.html'
                    raw_next_url = raw_url.format(page_num)
                    print('next comment page is : ', page_num, '\n',raw_next_url, '*'*200)
                    yield scrapy.Request(url=raw_next_url, callback=self.parse_next_comment_page, meta={'l': l})
            else:
                pass


    def parse_next_comment_page(self, response):
        # l = ItemLoader(item=EastmoneyCommentItem(), response=response)
        l = response.meta['l']
        reader_comment = response.xpath('//*[@class="zwlitext stockcodec"]/text()').extract()
        l.add_value('reader_comment', remove_symbol(reader_comment))

        print(l.load_item())
        return l.load_item()






