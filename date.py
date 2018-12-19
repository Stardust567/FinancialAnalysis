import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import os

class DateData:
    '''
    获取数据
    '''

    def __init__(self, code):
        # 服务器域名
        self.server = 'http://api.money.126.net/'
        self.cwnb = 'http://api.money.126.net/data/feed/1'
        self.url = self.cwnb + code + ',money.api?'
        # 请求头
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36'}

    def get_information(self):
        '''
        基于网易财经-沪深行情的数据获取
        :param url: 所要爬取的网页(基于股票代码）
        :return name: 给出该股票代码的股票名称
        :return table_time: 最近的12个季度
        :return data_mat: 最近12个季度的数据（dictionary类型）
        '''
        req = requests.get(url=self.url, headers=self.headers)
        req.encoding = 'utf-8'
        html = req.text
        attrs = re.findall(r':{(.*?)}',html)[0]
        attrs = attrs.split(',')
        index = []
        data = []
        labels = {'high': '今日最高价',
                  'price': '当前价',
                  'open': '今日开盘价',
                  'low': '今日最低价',
                  'updown': '价格升降',
                  'percent': '升降百分比',
                  'update': '更新时间',
                  'volume': '今日成交量',
                  'yestclose': '昨日收盘价',
                  'turnover': '今日成交额'
                  }
        for attr in attrs:
            list_temp = attr.split(':')
            index_temp = list_temp[0].split('"')[1]
            if index_temp in labels.keys():
                index_temp = labels[index_temp]
                index.append(index_temp)
                data.append(list_temp[1])
        data_mat = dict(zip(index, data))
        return index, data_mat



if __name__ == '__main__':
    code = input('请输入股票代码 (类似于000001):')
    data = DateData(code)
    print(data.get_information())