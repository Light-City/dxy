import requests
from lxml import etree
import pymongo
import pandas as pd

base_url = 'http://i.dxy.cn/profile/'
MONGO_URI = 'localhost'
MONGO_DB = 'test' # 定义数据库
MONGO_COLLECTION = 'dxy' # 定义数据库表
user = 'yilizhongzi'
class dxy_spider(object):
    def __init__(self, user_id, mongo_uri, mongo_db):
        self.url = base_url + user_id
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[mongo_db]

    def get_html(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        }

        req = requests.get(self.url, headers=headers).text
        # print(req)
        return req

    def get_UserInfo(self):
        raw_html = self.get_html()
        selector = etree.HTML(raw_html)
        key_list = []
        value_list = []
        force_fan_dd_key = selector.xpath('//div[@class="follows-fans clearfix"]//p/text()')
        force_fan_dd_value = selector.xpath('//div[@class="follows-fans clearfix"]//p/a/text()')
        for each in force_fan_dd_key:
            key_list.append(each)
        for each in force_fan_dd_value:
            value_list.append(each)

        UserInfo_dict = dict(zip(key_list,value_list)) # 两个list合并为dict
        # print(UserInfo_dict) # {'关注': '28', '粉丝': '90', '丁当': '1128'}

        user_home = selector.xpath('//p[@class="details-wrap__items"]/text()')[0]
        user_home = user_home.replace(',','') # 去掉逗号,否则使用MongoDB可视化工具导出csv文件报错！

        # print(user_home)
        UserInfo_dict['地址'] = user_home
        user_profile = selector.xpath('//p[@class="details-wrap__items details-wrap__last-item"]/text()')[0]
        UserInfo_dict['座右铭'] = user_profile
        # print(UserInfo_dict)
        # 帖子被浏览
        article_browser = selector.xpath('//li[@class="statistics-wrap__items statistics-wrap__item-topic fl"]/p/text()')
        UserInfo_dict[article_browser[0]] = article_browser[1]
        # 帖子被投票
        article_vote = selector.xpath('//li[@class="statistics-wrap__items statistics-wrap__item-vote fl"]/p/text()')
        UserInfo_dict[article_vote[0]] = article_vote[1]
        # 帖子被收藏
        article_collect = selector.xpath('//li[@class="statistics-wrap__items statistics-wrap__item-fav fl"]/p/text()')
        UserInfo_dict[article_collect[0]] = article_collect[1]
        # 在线时长共
        onlie_time = selector.xpath('//li[@class="statistics-wrap__items statistics-wrap__item-time fl"]/p/text()')
        UserInfo_dict[onlie_time[0]] = onlie_time[1]
        # print(UserInfo_dict)
        return UserInfo_dict

    def Save_MongoDB(self,userinfo):
        self.db[MONGO_COLLECTION].insert(userinfo)
        self.client.close()

    def Sava_Excel(self, userinfo):
        key_list = []
        value_list = []
        for key, value in userinfo.items():
            key_list.append(key)
            value_list.append(value)
        key_list.insert(0, '用户名')  # 增加用户名列
        value_list.insert(0, user)  # 增加用户名
        data = pd.DataFrame(data=[value_list],columns=key_list)
        print(data)
        '''
           表示以用户名命名csv文件，并去掉DataFame序列化后的index列(这就是index=False的意思)，并以utf-8编码，
           防止中文乱码。
           注意：一定要先用pandas的DataFrame序列化后，方可使用to_csv方法导出csv文件！
        '''
        data.to_csv('./' + user + '.csv', encoding='utf-8', index=False)

dxy = dxy_spider(user,MONGO_URI,MONGO_DB)
userinfo = dxy.get_UserInfo()
print(userinfo)
dxy.Save_MongoDB(userinfo)
dxy.Sava_Excel(userinfo)

