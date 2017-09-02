# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
import sqlite3
import scrapy
import re
from scrapy.exceptions import DropItem
class DeskZolPipeline(object):
    def process_item(self, item, spider):
        conn = sqlite3.connect('bizhi.db')
        c = conn.cursor()
        cursor = c.execute("SELECT *  from bizhi where name = \'"+item['name']+'\'')
        if cursor.fetchone():   #去重
            raise DropItem('duplicate item : %s' % item['name'])
        else:
            img_urls = ';'.join(item['img_url'])
            name = item['name']
            url =item['url']
            insert_sql = 'INSERT INTO bizhi VALUES ( '+ \
                         '\'' + name + '\',' + \
                         '\'' +url+ '\',' + \
                         '\'' +img_urls+ '\')'
            c.execute(insert_sql)   #写入数据库
            conn.commit()
            conn.close()
            return item

class MyImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url,meta={'item': item})

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        print(image_paths)
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item

    def file_path(self, request, response=None, info=None):
        """
        :param request: 每一个图片下载管道请求
        :param response:
        :param info:
        :param strip :清洗Windows系统的文件夹非法字符，避免无法创建目录
        :return: 每套图的分类目录
        """
        item = request.meta['item']
        folder = item['name']
        folder_strip = strip(folder)
        image_guid = request.url.split('/')[-1]+'.jpg'
        return u'full/{0}/{1}'.format(folder_strip, image_guid)
def strip(path):
    """
    :param path: 需要清洗的文件夹名字
    :return: 清洗掉Windows系统非法文件夹名字的字符串
    """
    path = re.sub(r'[？\\*|“<>:/]', '', str(path))
    return path

