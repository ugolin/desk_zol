# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import re
from desk_zol.items import DeskZolItem
class BizhiSpider(scrapy.Spider):
    name = 'bizhi'
    start_urls = ['http://desk.zol.com.cn/nb/','http://desk.zol.com.cn/pc/']
    
    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        next = soup.select('.next')
        alist = soup.select('.pic-list2')[0].find_all('a')
        for a in alist:
            item = DeskZolItem()
            item['name'] = a.span['title']
            item['url']='http://desk.zol.com.cn'+a['href']
            item['image_urls'] = []
            yield scrapy.Request('http://desk.zol.com.cn'+a['href'] , meta={'item':item},callback=self.parse_img)
        if next:
            yield scrapy.Request('http://desk.zol.com.cn' +next[0]['href'], callback=self.parse)


    def parse_img(self,response):
        item = response.meta['item']
        soup =BeautifulSoup(response.text,'lxml')
        lis= soup.find('ul',id='showImg').find_all('li')
        for li in lis:
            img = str(li.a.img)
            if re.search('srcs',img):
                real_url = re.sub('144x90', '1600x900', li.a.img['srcs'])
            elif re.search('src',img):
                real_url = re.sub('144x90', '1600x900', li.a.img['src'])
            item['image_urls'].append(real_url)
        yield item




        
        
