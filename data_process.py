import json
import os
from datetime import datetime
import redis
from config import REDIS,REDIS_SAVE_TIME
from redis_saver import redis2dictlist,dictlist2redis
from logger import logger


redis_client = redis.StrictRedis(**REDIS)    #连接redis数据库


class Data_process():

    base_path = os.getcwd()
    keywords_path = os.path.join(base_path, "the_words","keywords.txt")



    def __init__(self,id):
        self.id = id
        self.path_name = "users_data"
        self.data_path = os.path.join(self.base_path,self.path_name,self.id+".txt")
        self.redis_exist_state = redis_client.exists(id)       #用户id的Redis数据是否存在

        with open(self.keywords_path, "r", encoding="utf-8") as f_keywords:
            self.keywords = [x.strip() for x in f_keywords.readlines()]

    def updata_redis(self):

        datas = self.read_all_data_state_1()
        try:
            redis_client.hdel(self.id)
            add = redis_client.hmset(self.id, dictlist2redis(datas))
            set_time = redis_client.expire(self.id, REDIS_SAVE_TIME)
            if add == 1:
                logger.info(self.id+"的数据写入redis成功")
            else:
                logger.info(self.id + "的数据写入redis失败")
        except EnvironmentError as e:
            logger.error(e)


    #读取所有数据
    def read_all_data(self):

        with open(self.data_path,"r",encoding="utf-8") as f_read:
            datas_text = f_read.readlines()
            datas = []
            for data_text in datas_text:
                data = json.loads(data_text)
                datas.append(data)
            return datas

    # 读取所有数据,但不能读取state为0的数据
    def read_all_data_state_1(self):

        try:
            if self.redis_exist_state == 1:
                len = redis_client.hlen(self.id)
                result = redis_client.hmget(self.id, [i for i in range(len)])
                return redis2dictlist(result)

            else:
                with open(self.data_path, "r", encoding="utf-8") as f_read:
                    datas_text = f_read.readlines()
                    datas = []
                    for data_text in datas_text:
                        data = json.loads(data_text)
                        if data["state"] != 0:
                            datas.append(data)
                    if datas:
                        self.updata_redis()
                    return datas

        except EnvironmentError as e:
            logger.error(e)


    #读取一条数据
    def read_data(self,query):
        datas = self.read_all_data()
        if datas:
            for data in datas:
                if data["query"] == query and data["state"] == 1:
                    return data
        return None

    #创建用户的数据存储
    def create_data(self,datas):
        if datas:
            if not os.path.exists(self.data_path):
                with open(self.data_path,"a",encoding="utf-8") as f_create:
                    logger.info(self.id+"的txt文件创建成功！")

            for data in datas:
                query = data["query"]
                keywords = data["keywords"]
                answer = data["answer"]
                self.add_data(query,keywords,answer)

    def recreate_data(self, datas):   #类内部调用，重建
        if datas:
            for data in datas:
                query = data["query"]
                keywords = data["keywords"]
                answer = data["answer"]
                state = data["state"]
                time_str = data["time"]
                self.readd_data(query, keywords, answer,state,time_str)

            self.updata_redis(datas)   #更新数据到redis里

    def readd_data(self,query,keywords,answer,state,time_str):      #添加数据，重建时使用
        data = {
            "query":query,
            "keywords":keywords,
            "answer":answer,
            "state":state,
            "time":time_str
            }
        self.write_json_data(data)


    #增加数据
    def add_data(self,query,keywords,answer,state=1):

        curr_time = datetime.now()
        time_str = datetime.strftime(curr_time, '%Y-%m-%d/%H:%M:%S')
        data = {
            "query":query,
            "keywords":keywords,
            "answer":answer,
            "state":state,
            "time":time_str
            }

        if os.path.exists(self.data_path):  # 去重操作，防止问题重复,若问题重其他不重，则将原来的query的state设为0
            _data = self.read_data(query)   #看是否重复

            if _data:  #读到重复的query
                if _data["query"] == query and (_data["answer"] != answer or _data["keywords"] != keywords):  #query重复，keywords和answer不重复的状态下,把原来的数据state设为0
                    self.delete_data(query)
                    self.write_json_data(data)
                    self.insert_keyword(keywords)

                else:                         #完全重复了，不做任何操作
                    pass

            else:     #未读到重复的query
                self.write_json_data(data)
                self.insert_keyword(keywords)


    def insert_keyword(self,keywords):                          # 向分词字典加入新词
        for keyword in keywords:
            if keyword not in self.keywords:
                with open(self.keywords_path, "a", encoding="utf-8") as f_keywords:
                    f_keywords.write(keyword + "\n")



    def write_json_data(self,data):                                      # 写新数据到文件
        with open(self.data_path, "a", encoding="utf-8") as f_write:
            json.dump(data, f_write)
            f_write.write("\n")



    #删除数据
    def delete_data(self,query):
        try:
            datas = self.read_all_data()
            for idx,data in enumerate(datas):
                if data["query"] == query:
                    data["state"] = 0
                    break

            self.delete_and_rebuilt_txtfile(datas)
            logger.info(self.id+"删除‘ {} ’数据成功".format(query))
        except EnvironmentError as e:
            logger.error(e)



    def set_state_1(self,query):
        try:
            datas = self.read_all_data()
            for idx,data in enumerate(datas):
                if data["query"] == query:
                    data["state"] = 1
                    break
            self.delete_and_rebuilt_txtfile(datas)
            logger.info(self.id + "添加‘ {} ’数据成功".format(query))
        except EnvironmentError as e:
            logger.error(e)


    #删除所有数据
    def delete_all_data(self):
        try:
            datas = self.read_all_data()
            for idx, data in enumerate(datas):
                data["state"] = 0

            self.delete_and_rebuilt_txtfile(datas)
            redis_client.delete(self.id)
            logger.info(self.id+"删除所有数据成功！")
        except EnvironmentError as e:
            logger.error(e)



    #删除文件并重新写入数据，用于修改数据时使用
    def delete_and_rebuilt_txtfile(self,datas):
        os.remove(self.data_path)
        if datas:
            self.recreate_data(datas)




if __name__ == '__main__':

    data_process = Data_process("000001")
    # data = [{'query': '这件衣服什么价格？', 'keywords': ['价格'], 'answer': '125元'}, {'query': '这件衣服都有什么颜色？', 'keywords': ['颜色'], 'answer': '黑色白色都有啊'}, {'query': '这件衣服都有什么尺码？', 'keywords': ['尺码'], 'answer': 'XXL'}]
    #
    # data_process.create_data(data)

    data_process.add_data('格力变频空调真的很省电吗？', ["格力","变频","空调","省电"], "是的，每晚不到一度电")
    # data_process.add_data('这件衣服什么价格？', ["价格"], "120元")
    # print(data_process.read_all_data())
    # data_process.delete_data("这件衣服都有什么颜色？")

    print(data_process.read_all_data_state_1())

    # print(type(data_process.redis_exist_state))

