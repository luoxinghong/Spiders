#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: 罗兴红
@contact: 767166726@qq.com
@file: demo1.py
@time: 2020/8/4 17:26
@desc:
'''
from urllib import request
import requests
from lxml import etree
import os
from queue import Queue
import threading


# 定义生产者
class Procuder(threading.Thread):
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }

    def __init__(self, page_queue, img_queue, *args, **kwargs):
        super(Procuder, self).__init__(*args, **kwargs)
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:
            if self.page_queue.empty():
                break
            url = self.page_queue.get()
            print(url)
            self.parse_url(url)

    def parse_url(self, url):
        response = requests.get(url, headers=self.HEADERS)
        html_str = etree.HTML(response.content.decode())
        titles = html_str.xpath('//ul[@class="b_dataList"]/li/a/@title')
        img_urls = html_str.xpath('//div[@class="img_cont hoff"]/img/@src')
        for i, img in enumerate(titles):
            item = {}
            item["titles"] = titles[i]
            item["img_url"] = img_urls[i]
            item["rank"] = i+1
            item["page_url"] = url
            self.img_queue.put(item)
        self.page_queue.task_done()


class Counsumer(threading.Thread):
    def __init__(self, page_queue, img_queue, *args, **kwargs):
        super(Counsumer, self).__init__(*args, **kwargs)
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        print("============")
        while True:
            if self.img_queue.empty() and self.page_queue.empty():
                break
            item = self.img_queue.get()
            print(item)
            self.img_queue.task_done()


def main():
    page_queue = Queue(10)
    img_queue = Queue(2000)
    base_url = 'https://cn.bing.com/images/async?q={}&first={}&count=100&relp=234&scenario=ImageHoverTitle&datsrc=I&layout=ColumnBased&mmasync=1&dgState=c*2_y*18167s18164_i*235_w*166&IG=4E2E86FE114344BE8DF24904C8A18F04&SFX=9&iid=images.5267'
    file_path = "./kws.txt"
    with open(file_path,"r",encoding="utf-8") as f:
        kws = [i.strip() for i in f.readlines()]
        for kw in kws:
            for i in range(0, 200,100):
                url = base_url.format(kw,i)
                page_queue.put(url)

    for i in range(2):
        t1 = Procuder(page_queue, img_queue)
        t1.start()
        t1.join()

    for i in range(2):
        t2 = Counsumer(page_queue, img_queue)
        t2.start()
        t2.join()


if __name__ == '__main__':
    main()
