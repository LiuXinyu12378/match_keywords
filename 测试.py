import jieba.analyse as analyse
import jieba
import redis
from config import REDIS

# text = "我想知道格力空调变频怎么样"
# # TF-IDF
# tf_result = analyse.extract_tags(text, topK=5) # topK指定数量，默认20
# print(tf_result)
# # TextRank
# tr_result = analyse.textrank(text, topK=5) # topK指定数量，默认20
# print(tr_result)
#
# result = jieba.lcut_for_search(text,HMM=True)
# print(result)
#
# result = jieba.lcut(text,cut_all=True,HMM=True)
# print(result)

def redis2dictlist(redis_result):
    data_list = []
    for x in redis_result:
        data = x.decode("utf-8").strip().split("\n")
        data_dict = {
            "query": data[0],
            "keywords": [x for x in data[1].split()],
            "answer": data[2],
            "state": data[3],
            "time": data[4],
        }
        data_list.append(data_dict)

    return data_list

def dictlist2redis(datalist):
    redis_data = {}
    for idx,data in enumerate(datalist):
        query = data["query"]
        keywords = " ".join(data["keywords"])
        answer = data["answer"]
        state = data["state"]
        time = data["time"]
        data_str = query+"\n"+keywords+"\n"+answer+"\n"+state+"\n"+time+"\n"
        redis_data[idx] = data_str

    return redis_data

try:

    client = redis.StrictRedis(**REDIS)

    id = "000001"
    id_redis_exist = client.exists(id)

    if id_redis_exist == 0:   #如果用户id不存在

        data = {
            0:"这个空调会变频吗?\n空调 变频\n可以的\n1\n2020/8/14",
            1:"这个衣服都有什么颜色\n颜色\n黑的白的都有啊\n1\n2020/8/14",
            2:"这个衣服价格怎么样\n价格\n120元\n1\n2020/8/14",
                }

        add = client.hmset(id,data)
        print(add)
        set_time = client.expire(id,300)
        print(set_time)

    else:
        len = client.hlen(id)

        result = client.hmget(id,[i for i in range(len)])

        print(result)
        print(redis2dictlist(result))

except Exception as e:
    print(e)


# if __name__ == '__main__':
#     datalist = [{'query':'这个空调会变频吗', 'keywords': ['空调', '变频'], 'answer': '可以的', 'state': '1', 'time': '2020/8/14'},
#                 {'query': '这个衣服都有什么颜色', 'keywords': ['颜色'], 'answer': '黑的白的都有啊', 'state': '1', 'time': '2020/8/14'},
#                 {'query': '这个衣服价格怎么样', 'keywords': ['价格'], 'answer': '120元', 'state': '1', 'time': '2020/8/14'}]
#
#     print(dictlist2redis(datalist))