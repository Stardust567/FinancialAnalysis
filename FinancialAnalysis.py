import requests
import re
from bs4 import BeautifulSoup
from lxml import etree
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import time

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

class GetFinancialData:
    '''
    获取公司财务数据
    '''

    def __init__(self, code):
        # 服务器域名
        self.server = 'http://quotes.money.163.com/'
        self.cwnb = 'http://quotes.money.163.com/f10/zycwzb_'
        self.url = self.cwnb + code + '.html#01c01'
        # 请求头
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36'}

    def getHTMLText(self, url):
        try:
            r = requests.get(url, headers=self.headers, timeout=30)
            r.raise_for_status()
            r.encoding = "utf-8"
            return r.text
        except:
            return "产生异常"

    def get_information(self):
        '''
        基于网易财经-沪深行情的数据获取
        :param url: 所要爬取的网页(基于股票代码）
        :return name: 给出该股票代码的股票名称
        :return table_time: 最近的12个季度
        :return data_mat: 最近12个季度的数据（dictionary类型）
        '''
        html = self.getHTMLText(self.url)
        page_bf = BeautifulSoup(html, 'lxml')

        name = page_bf.find_all('span', class_='name')
        if (len(name) == 0):
            print("Sorry, no relative data,please check out the number you entered.")
            exit()
        name = name[0].string
        name = name.split(')')[0]
        name = name + ')'
        name = re.sub(u'[\/:*?"<>]', ' ', name) # 英文的 \ / : * ? " < > 不能作为文件名

        table_name = page_bf.find_all('td', class_='td_1')
        for i in range(len(table_name)):
            table_name[i] = table_name[i].get_text()
            # table_name此时为该网页上所有指标的名字

        table_time = page_bf.find_all('th')
        for i in range(len(table_time)):
            table_time[i] = table_time[i].get_text()
            time_list = table_time[i].split('-')
            if(len(time_list)!=3): continue
            time_temp = str(time_list[0])+'-'+str(time_list[1])
            table_time[i] = time_temp
        table_time = table_time[1:13] # 最近12个季度的数据情况
        table_time = table_time[::-1]

        table_data = []
        table_name_num = len(table_name)
        for i in range(len(table_name)):
            if(table_name_num != len(table_name)):
                break
                # 当table_name_num变动时退出循环
            data = []
            for j in range(len(table_time)):
                xpath = '//*[@id="scrollTable"]/div[8]/table/tr['+str(i+2)+']/td['+str(j+1)+']'
                selector = etree.HTML(html)
                data_temp = selector.xpath(xpath + '/text()')
                if(len(data_temp) == 0):
                    table_name_num = i
                    break
                    # 当第一个表格（主要财务指标）数据读取完毕时退出循环
                    # 此时将table_name_num的值修改为i
                data_temp = data_temp[0].replace(',','') # 去除有些数据中的千分隔符
                if (data_temp == '--'): data_temp = 0 # 有的数据为-- 我们将其换为0
                data.append(data_temp)
            data = np.array(data[::-1])
            data = data.astype('float64')
            table_data.append(data)

        table_name = table_name[0:table_name_num]
        table_data = table_data[0:table_name_num]
        data_mat = dict(zip(table_name, table_data))

        return name, table_time, table_name, data_mat


class GetBussinessData:
    '''
    获取公司相关数据
    '''

    def __init__(self, code):
        # 服务器域名
        self.server = 'http://quotes.money.163.com/'
        self.cwnb = 'http://quotes.money.163.com/f10/gszl_'
        self.url = self.cwnb + code + '.html#01f01'
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
        index = []
        content = []
        for i in range(1, 11):
            for j in range(1, 5):
                xpath = '/html/body/div[2]/div[4]/table/tr[' + str(i) + ']/td[' + str(j) + ']'
                selector = etree.HTML(html)
                if(len(selector.xpath(xpath + '/text()')) == 0): # 为了避免有些内容为空导致index out的情况
                    data_temp = " "
                else:
                    data_temp = selector.xpath(xpath + '/text()')[0]
                if (j == 1 or j == 3):
                    index.append(data_temp)
                else:
                    content.append(data_temp)
        return dict(zip(index, content))


class Data:
    '''
    数据面板
    '''

    def __init__(self, code):
        self.code = code
        FinancialData = GetFinancialData(code)
        name, time, index, data_mat = FinancialData.get_information()
        self.name = name
        self.time = time
        self.index = index
        self.data_mat = data_mat
        self.path = 'E:/Python/FinancialAnalysis/FinancialData/' + code +'/'
        BusinessData = GetBussinessData(code)
        business_data = BusinessData.get_information()
        self.business_data = business_data

    def save(self):
        dataframe = pd.DataFrame(self.data_mat, index=self.time)
        filename = self.path + 'FinancialData' + '.csv'
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        dataframe.to_csv(filename, sep=',')

        dataframe = pd.DataFrame(self.business_data, index=['内容'])
        filename = self.path + 'BusinessData' + '.csv'
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        dataframe.to_csv(filename, sep=',')
        '''
        dataframe = pd.DataFrame(self.data_mat, index=self.time)
        filename = self.path + 'FinancialData' + '.json'
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        dataframe.to_json(filename, force_ascii=False)

        dataframe = pd.DataFrame(self.business_data, index=['内容'])
        filename = self.path + 'BusinessData' + '.json'
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        dataframe.to_json(filename, force_ascii=False)
        '''


class getPicture:
    '''
    绘制图像
    '''

    def __init__(self,code):

        self.path = 'E:/Python/FinancialAnalysis/FinancialData/' + code + '/'
        self.style = 'seaborn-bright'
        # self.style = 'dark_background'

    def get_linePicture(self, title, time, key1, value1, color_set = 0, key2='', value2=[], split = False, bar = True, save = False):
        '''
        绘制折线图
        :param title: 股票名
        :param time: 时间序列
        :param key1: 第一个指标名
        :param value1: 第一个指标的数据
        :param key2: 第二个指标名（默认为空格' '）
        :param value2: 第二个指标的数据（默认为空集[])
        :param split: 是否设置左右两个y轴（默认为否False）
        :param save: 是否存图（默认False）
        '''
        plt.style.use(self.style) # 设置风格
        fig, ax1 = plt.subplots(facecolor='#FFF7E3')

        color = ['tab:blue', 'tab:orange',
                 'tab:green', 'tab:red',
                 'tab:purple', 'tab:brown',
                 'tab:pink', 'tab:gray',
                 'tab:olive', 'tab:cyan']
        #blue, orange, green, red, purple, brown, pink, gray, olive, cyan
        plt.xticks(rotation=30)
        ax1.tick_params(axis='x', labelcolor=color[7])
        ax1.set_ylabel(key1)
        ax1.tick_params(axis='y', labelcolor=color[color_set])
        ax1.plot(time, value1, '--', color=color[color_set], marker = '*', label = key1)
        plt.title(title)
        ax1.grid(True)
        if(bar is True):
            ax1.bar(time, value1, align="center", width=0.5, alpha=0.5, color=color[color_set])

        if(len(value2)!=0):
            if (split is False):
                ax1.plot(time, value2, '-.', color=color[1], marker='*', label=key2)
                ax1.tick_params(axis='y', labelcolor=color[1])
                ax1.legend(loc=2)
                if (bar is True):
                    ax1.bar(time, value2, align="edge", width=0.5, alpha=0.5, color=color[1])


            if(split is True):
                ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
                ax2.set_ylabel(key2)
                ax2.tick_params(axis='y', labelcolor=color[1])
                ax2.plot(time, value2, '-.', color=color[1], marker='*', label=key2)
                ax2.grid(False)
                if (bar is True):
                    ax2.bar(time, value2, align="edge", width=0.5, alpha=0.5, color=color[1])

            fig.tight_layout()  # otherwise the right y-label is slightly clipped

        if(save is True):
            filename = self.path + 'linePicture/' + title +".png"
            dirname = os.path.dirname(filename)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            fig.savefig(filename)

        plt.close('all')

    def get_piePicture(self, title, labels1, data1, labels2 = [], data2 = [], save = False):
        '''
        绘制饼状图
        :param title:股票名
        :param labels1: 外环的所有标签构成的列表
        :param data1: 外环各标签数据构成的列表
        :param labels2: 内环的所有标签构成的列表（默认与外环一致）
        :param data2: 内环各标签数据构成的列表（默认与外环一致）
        :param save: 是否存图（默认False）
        '''
        plt.style.use(self.style)

        if(len(data2)==0):
            labels = labels1
            fig, ax = plt.subplots(facecolor='#FFF7E3')
            ax.grid(True)
            cmap = plt.get_cmap("tab20c")
            color = np.array(range(0, 20, 1))
            outer_colors = cmap(color[4:4+len(data1)])

            ax.pie(data1, labels=labels1, radius=1, autopct='%1.1f%%', colors=outer_colors,
                   wedgeprops=dict(width=0.3, edgecolor='w'))

        else:
            labels = labels1 + labels2
            fig, ax = plt.subplots(facecolor='#FFF7E3')
            ax.grid(True)
            cmap = plt.get_cmap("tab20c")
            color = np.array(range(100))
            outer_colors = cmap(color[0:len(data1)])
            inner_colors = cmap(color[12:12+len(data2)])

            ax.pie(data1, labels=labels1, radius=1, autopct='%1.1f%%', colors=outer_colors,
                   wedgeprops=dict(width=0.3, edgecolor='w'))

            ax.pie(data2, radius=1 - 0.5, autopct='%1.1f%%', colors=inner_colors,
                   wedgeprops=dict(width=0.3, edgecolor='w'))

        ax.legend(labels=labels, loc='best', bbox_to_anchor=(0.8, 0.6, 0.5, 0.5))

        ax.set_title(title)
        if (save is True):
            filename = self.path + 'piePicture/' + title + ".png"
            dirname = os.path.dirname(filename)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            fig.savefig(filename)

        plt.close('all')

    def get_radarPicture(self, title, time, labels, data_list, save = False):
        '''
        绘制雷达图
        :param title:股票名称
        :param labels:标签列表
        :param data_list:第一维是时间，第二维是标签的数据矩阵
        :param save: 是否存图（默认False）
        '''
        plt.style.use(self.style)

        N = len(labels)
        # 设置雷达图的角度，用于平分切开一个圆面
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
        # 为了使雷达图一圈封闭起来，需要下面的步骤
        #data = np.concatenate((data, [data[0]]))
        angles = np.concatenate((angles, [angles[0]]))

        # 绘图
        fig = plt.figure()
        ax = fig.add_subplot(111, polar=True)
        num = 0
        color = ['tab:pink', 'tab:orange',
                 'tab:purple', 'tab:blue',]
        for data in data_list:
            num += 1
            data = np.concatenate((data, [data[0]]))
            ax.plot(angles, data, c=color[num], marker='P', linewidth=1, label='%d'%num)
            ax.fill(angles, data, c=color[num], alpha=0.25)

        # 添加每个特征的标签
        ax.set_thetagrids(angles * 180 / np.pi, labels)
        # 设置雷达图的范围
        ax.set_ylim(data_list.min(), 100)
        # 添加标题
        plt.title(title)

        # 添加网格线
        ax.grid(True)
        # 设置图例
        plt.legend(labels=time, loc='best', bbox_to_anchor=(0.8, 0.6, 0.5, 0.5))
        if (save is True):
            filename = self.path + 'radarPicture/' + title + ".png"
            dirname = os.path.dirname(filename)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            fig.savefig(filename)

        plt.close('all')

class Picture():
    '''
    图像画板
    '''

    def __init__(self, data):
        self.data = data
        self.get = getPicture(data.code)

    def linePicture(self, save = True):
        data = self.data
        time = data.time

        key2 = data.index[8]
        value2 = data.data_mat[key2]
        self.get.get_linePicture('利 润 总 额', time, key2, value2,
                                 color_set=1, bar=True, save=save)

        key1 = data.index[3]
        value1 = data.data_mat[key1]
        key2 = data.index[4]
        value2 = data.data_mat[key2]
        self.get.get_linePicture('主 营 业 务', time, key1, value1,
                                 key2=key2, value2=value2, color_set=0,
                                 split=False, bar=False, save=save)

        key1 = data.index[4]
        value1 = data.data_mat[key1]
        key2 = data.index[8]
        value2 = data.data_mat[key2]
        self.get.get_linePicture('盈 利 能 力', time, key1, value1,
                                 key2=key2, value2=value2, color_set=0,
                                 split=False, bar=False, save=save)

        key1 = data.index[13]
        value1 = data.data_mat[key1]
        key2 = data.index[15]
        value2 = data.data_mat[key2]
        self.get.get_linePicture('偿 债 能 力', time, key1, value1,
                                 key2=key2, value2=value2, color_set=0,
                                 split=False,bar=True, save=save)

    def piePicture(self, save = True):
        data = self.data
        time = data.time
        labels_test1 = []
        data_test1 = []
        labels_test2 = []
        data_test2 = []
        for i in {13, 15}:  # 取哪些标签作为饼状图的绘制依据
            index_temp = data.index[i]
            labels_test1.append(index_temp)
            data_temp = (data.data_mat[index_temp])[-1]
            if (data_temp == 0): data_temp = 1
            data_test1.append(data_temp)
        for i in {14, 16}:  # 取哪些标签作为饼状图的绘制依据
            index_temp = data.index[i]
            labels_test2.append(index_temp)
            data_temp = (data.data_mat[index_temp])[-1]
            if (data_temp == 0): data_temp = 1
            data_test2.append(data_temp)
        self.get.get_piePicture('偿 债 能 力', labels_test1, data_test1, labels_test2, data_test2, save=save)

        labels_test1 = []
        data_test1 = []
        for i in {4, 6, 7}:  # 取哪些标签作为饼状图的绘制依据
            index_temp = data.index[i]
            labels_test1.append(index_temp)
            data_temp = (data.data_mat[index_temp])[-1]
            if (data_temp == 0): data_temp = 1
            data_test1.append(data_temp)
        self.get.get_piePicture('盈 利 组 成', labels_test1, data_test1, save=save)

    def radarPicture(self, save = True):
        data = self.data
        time = data.time
        index_set = [4,6,7]
        labels = []
        for label in index_set:
            labels.append(data.index[label])
        data_test = []
        time_test = data.time[::-4]
        for season in range(-1, -10, -4):
            data_temp = []
            for label in index_set:  # 可以手动设定取哪些做标签
                label = data.index[label]
                test = data.data_mat[label]
                max = test.max() if test.max() > 0 else -test.max()
                min = test.min() if test.min() > 0 else -test.min()
                max = max if max > min else min
                if(max==0): max = 1 # 防止除数为0
                test = test / max * 95
                data_temp.append(test[season])
            data_test.append(data_temp)
        data_test = np.array(data_test)
        self.get.get_radarPicture('盈利组成历史对比', time_test, labels, data_test, save=save)

    def show(self):
        plt.show()

'''
if __name__ == '__main__':
    for i in range(1,10):
        data = Data('%06d'%i)
        data.save()
        print(data.name, time.ctime(time.time()))
        picture = Picture(data)
        picture.radarPicture()
        picture.linePicture()
        picture.piePicture()
'''
