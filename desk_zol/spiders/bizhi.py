# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import re
from desk_zol.items import DeskZolItem
class BizhiSpider(scrapy.Spider):
    name = 'bizhi'
    start_urls = ['http://desk.zol.com.cn/nb/']
    num = 0
    
    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        total_num_string = soup.select('.allPic')[0].font.text  # 壁纸专辑总数
        total_num = int(total_num_string)  # 转换为int类型
        if total_num % 15 == 0:
            self.num = total_num / 15
        else:
            self.num = total_num // 15 + 1
        for i in range(1, int(self.num) + 1):  #test
            url = response.url + str(i) + '.html'
            yield scrapy.Request(url, callback=self.parse_start_url)
    def parse_start_url(self,response):
        soup = BeautifulSoup(response.body,'lxml')
        alist = soup.select('.pic-list2')[0].find_all('a')
        for a in alist:
            item = DeskZolItem()
            item['name'] = a.span['title']
            item['url']='http://desk.zol.com.cn'+a['href']
            item['img_url']=[]
            item['image_urls'] = []
            yield scrapy.Request('http://desk.zol.com.cn'+a['href'] , meta={'key':item},callback=self.parse_mainurl)
    def parse_mainurl(self,response):
        soup =BeautifulSoup(response.text,'lxml')
        lis= soup.find('ul',id='showImg').find_all('li')
        #print('li:',len(lis),lis[0],lis[len(lis)-1],response.url)
        for li in lis:
            #print('li:',li)
            yield scrapy.Request('http://desk.zol.com.cn'+li.a['href'],dont_filter=True,meta={'key':response.meta['key']},callback=self.parse_imgurl)

    def parse_imgurl(self,response):
        #print(response.url)
        item = response.meta['key']
        a = response.xpath('/html/body/div[3]/h3/span/text()[2]').extract()
        cnt = int ( a[0].rstrip('）').lstrip('/') )
        #b = response.xpath('/html/body/div[3]/h3/span/span').extract()
        soup = BeautifulSoup(response.text,'lxml')
        t = soup.find('img',id='bigImg')['src']
        real_url = re.sub('960x600','1600x900',t)
        #yield {'test':real_url}
        item['img_url'].append(real_url)
        item['image_urls'].append(real_url)
        #print(b ,len(item['img_url']),cnt)
        if len(item['img_url']) == cnt :
            yield item


        
        
