#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: 罗兴红
@contact: 767166726@qq.com
@file: demo1.py
@time: 2020/8/4 17:26
@desc:
'''
import requests
from threading import Thread, Lock
from queue import Queue
import json
from lxml import etree
import json
import time
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 未处理异常请求
# 未加日志
class Spider(object):
    def __init__(self, page_num, keyword_file_path, thread_num):
        self.url_queue = Queue()
        self.item_queue = Queue()
        self.save_data_queue = Queue()
        self.page_num = page_num
        self.keyword_file_path = keyword_file_path
        self.thread_num = thread_num
        self.HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        }
        self.base_url = 'https://cn.bing.com/images/async?q={}&first={}&count=100&relp=234&scenario=ImageHoverTitle&datsrc=I&layout=ColumnBased&mmasync=1&dgState=c*2_y*18167s18164_i*235_w*166&IG=4E2E86FE114344BE8DF24904C8A18F04&SFX=9&iid=images.5267'
        # self.mu = Lock()

    def produce_url(self):
        with open(self.keyword_file_path, "r", encoding="utf-8") as f:
            kws = [i.strip().split()[0] for i in f.readlines()]
            for kw in kws:
                for first_num in range(0, self.page_num * 100, 100):
                    url = self.base_url.format(kw, first_num)
                    self.url_queue.put((url, kw))

    def get_info(self):
        while not self.url_queue.empty():
            url, kw = self.url_queue.get()
            response = requests.get(url, headers=self.HEADERS, verify=False,timeout=5)
            if response.status_code == 200:
                html_str = etree.HTML(response.content.decode())
                titles = html_str.xpath('//div[@class="iuscp"]//div[@class="img_cont hoff"]/img/@src')
                sites = html_str.xpath('//div[@class="infnmpt"]/div[2]/ul[@class="b_dataList"]/li/a/@title')
                img_urls = html_str.xpath('//div[@class="img_cont hoff"]/img/@src')
                print(len(titles), len(sites), len(img_urls))
                if len(titles) == len(img_urls) == len(sites):
                    dic = {}
                    items = []
                    for i, title in enumerate(titles):
                        item = {}
                        item["titles"] = title
                        item["img_url"] = img_urls[i]
                        item["rank"] = i + 1
                        item["page_url"] = response.url
                        item["page_url"] = url
                        # print(item)
                        items.append(item)
                    dic["query"] = kw
                    dic["country"] = "US"
                    dic["lang"] = "en"
                    dic["lang"] = items
                    dic["crawl_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    f = open("res.txt", "a+", encoding="utf-8")
                    f.write(json.dumps(dic,ensure_ascii=False))
                    f.close()
            else:
                self.url_queue.put(url)

    def run(self):
        self.produce_url()
        ths = []
        for _ in range(self.thread_num):
            th = Thread(target=self.get_info)
            th.start()
            ths.append(th)
        for th in ths:
            th.join()
        print('===========Data crawling is finished.===========')


if __name__ == '__main__':
    page_num = 1
    keyword_file_path = "kws.txt"
    thread_num = 20
    Spider(page_num, keyword_file_path, thread_num).run()
