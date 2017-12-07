import requests as r
from lxml import etree
import re

def get_code_dict_and_list():
    code_dict = {}
    code_list = []
    last_codes = []
    def crawl_stock_page():
        url = 'http://quote.eastmoney.com/stocklist.html'
        response = r.get(url)
        response.encoding = 'gbk'
        r_text = response.text
        html = etree.HTML(r_text)
        raw_list = html.xpath('//*[@id="quotesearch"]/ul/li/a/text()')
        # print(raw_list)
        return raw_list

    raw_list = crawl_stock_page()
    compile_word = re.compile(r'(.*?)\(\d+')
    compile_code = re.compile(r'.*?(\d+)')
    for i in raw_list:
        word = re.findall(compile_word, i)[0]
        code = re.findall(compile_code, i)[0]
        # print(word, code)
        code_dict[word] = code
        code_list.append(code)
    # print(code_dict, code_list)

    for w, c in code_dict.items():
        code_sh = re.compile('600...')
        code_cyb = re.compile('300...')
        code_sz = re.compile('000...')
        sh_ = re.findall(code_sh, c)
        cyb_ = re.findall(code_cyb, c)
        sz_ = re.findall(code_sz, c)
        [last_codes.append(i) for i in sh_ if i is not None]
        [last_codes.append(i) for i in cyb_ if i is not None]
        [last_codes.append(i) for i in sz_ if i is not None]
    # print(last_codes, len(last_codes))
    return last_codes
# get_code_dict_and_list()


# get all the code list
def get_start_urls():
    cl = get_code_dict_and_list()  #total 2078 codes
    urls = []
    for code in cl:
        sturl = 'http://guba.eastmoney.com/list,%s.html' % code
        urls.append(sturl)
    # print(urls, len(urls))
    return urls
