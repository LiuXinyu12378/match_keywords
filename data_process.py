import json
import os
from datetime import datetime
from logger import logger


class Data_process():

    base_path = os.getcwd()
    keywords_path = os.path.join(base_path, "the_words","keywords.txt")


    def __init__(self,id):
        self.id = id
        self.path_name = "users_data"
        self.data_path = os.path.join(self.base_path,self.path_name,self.id+".txt")

        with open(self.keywords_path, "r", encoding="utf-8") as f_keywords:
            self.keywords = [x.strip() for x in f_keywords.readlines()]


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

            with open(self.data_path, "r", encoding="utf-8") as f_read:
                datas_text = f_read.readlines()
                datas = []
                for data_text in datas_text:
                    data = json.loads(data_text)
                    if data["state"] != 0:
                        datas.append(data)
                return datas

        except EnvironmentError as e:
            logger.error(e)


    #读取一条数据
    def read_data(self,query):
        datas = self.read_all_data()
        idx_data = {}
        if datas:
            for idx,data in enumerate(datas):
                if data["query"] == query and data["state"] == 1:    #读到了状态为1的query
                    idx_data[idx] = data
                if data["query"] == query and data["state"] ==0:     #读到了状态为零的query
                    idx_data[idx] = data
            if idx_data:
                return idx_data
        return None

    #创建用户的数据存储
    def create_data(self,datas):
        if datas:
            if not os.path.exists(self.data_path):
                with open(self.data_path,"a",encoding="utf-8") as f_create:
                    logger.info(self.id+"的txt文件创建成功！")

            for data in datas:
                self.add_data(data)

    def recreate_data(self, datas):   #类内部调用，重建
        if datas:
            for data in datas:
                self.readd_data(data)


    def readd_data(self,data):      #添加数据，重建时使用

        data = {
            "class":data['class'],
            "query":data["query"],
            "keywords":data["keywords"],
            "answer":data["answer"],
            "state":data["state"],
            "time":data["time"]
            }
        self.write_json_data(data)

    #增加数据
    def add_data(self,data,state=1):

        classify = data["class"]
        query = data["query"]
        keywords = data["keywords"]
        answer = data["answer"]
        curr_time = datetime.now()
        time_str = datetime.strftime(curr_time, '%Y-%m-%d/%H:%M:%S')

        data = {
            "class":classify,
            "query":query,
            "keywords":keywords,
            "answer":answer,
            "state":state,
            "time":time_str
            }

        if os.path.exists(self.data_path):  # 去重操作，防止问题重复,若问题重其他不重，则将原来的query的state设为0
            data_dict = self.read_data(query)   #看是否重复

            if data_dict:  #读到重复的query

                for index,_data in data_dict.items():
                    if _data["query"] == query and (_data["class"] != classify or _data["answer"] != answer or _data["keywords"] != keywords) and _data['state'] == 1:  #query重复，keywords和answer不重复并且state=1的状态下,把原来的数据state设为0
                        self.set_state_0(index)
                        self.no_repeat_write(data)   #不重复写入
                        self.insert_keyword(keywords)

                    elif _data["query"] == query and _data["class"] == classify and _data["answer"] == answer and _data["keywords"] == keywords and _data['state'] == 0:    #完全重复了，但原来state本身就是0，则把state改回1
                        self.set_state_1(index)   #根据索引值来修改

                    else:                                                                                                                                                   #完全重复，而且state是1，则不操作
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
                if data["query"] == query and data['state'] == 1:
                    data["state"] = 0
                    break

            self.delete_and_rebuilt_txtfile(datas)
            logger.info(self.id+"设置‘ {} ’ 的状态为0".format(query))
        except EnvironmentError as e:
            logger.error(e)

    def set_state_0(self,index):         #修改存储的状态为1
        try:
            datas = self.read_all_data()
            for idx,data in enumerate(datas):
                if idx == index:
                    data["state"] = 0
                    query = data["query"]
                    break
            self.delete_and_rebuilt_txtfile(datas)
            logger.info(self.id + "设置‘ {} ’ 的状态为0".format(query))
        except EnvironmentError as e:
            logger.error(e)


    def set_state_1(self,index):         #修改存储的状态为1
        try:
            datas = self.read_all_data()
            for idx,data in enumerate(datas):
                if idx == index:
                    data["state"] = 1
                    query = data["query"]
                    break
            self.delete_and_rebuilt_txtfile(datas)
            logger.info(self.id + "恢复 {} 的state为1".format(query))
        except EnvironmentError as e:
            logger.error(e)


    #删除所有数据
    def delete_all_data(self):
        try:
            datas = self.read_all_data()
            for idx, data in enumerate(datas):
                data["state"] = 0

            self.delete_and_rebuilt_txtfile(datas)
            logger.info(self.id+"删除所有数据成功！")
        except EnvironmentError as e:
            logger.error(e)



    #删除文件并重新写入数据，用于修改数据时使用
    def delete_and_rebuilt_txtfile(self,datas):
        os.remove(self.data_path)
        if datas:
            self.recreate_data(datas)

    def no_repeat_write(self,data):
        data_list = self.read_all_data_state_1()
        for _data in data_list:
            if data["class"] == _data["class"] and data["query"] == _data["query"] and data["keywords"] == _data["keywords"] and data["answer"] == _data["answer"] and data["state"] == _data["state"]:
                return

        self.write_json_data(data)



if __name__ == '__main__':

    data_process = Data_process("000001")
    # data = [{'class':"1",'query': '这件衣服什么价格？', 'keywords': ['价格'], 'answer': '125元'},
    #         {'class':"1",'query': '这件衣服都有什么颜色？', 'keywords': ['颜色'], 'answer': '黑色白色都有啊'},
    #         {'class':"1",'query': '这件衣服都有什么尺码？', 'keywords': ['尺码'], 'answer': 'XXL'}]
    #
    # data_process.create_data(data)
    #
    # data_process.add_data({'class':"2",'query':'格力变频空调真的很省电吗？', 'keywords':["格力","变频","空调","省电"],'answer':"是的，每晚不到一度电"})
    # data_process.add_data({'class':'1','query':'这件衣服什么价格？','keywords':["价格"],'answer':"125元"})
    # print(data_process.read_all_data())
    # data_process.delete_data("这件衣服都有什么颜色？")

    # data_process.updata_redis()
    # print(data_process.read_all_data())
    print(data_process.read_all_data_state_1())

    # print(type(data_process.redis_exist_state))

