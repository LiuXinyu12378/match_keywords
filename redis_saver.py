

def redis2dictlist(redis_result):  # redis的hash数据  转换为 字典列表数据
    '''
    :param redis_result: 
    [b'\xe8\xbf\x99\xe4\xb8\xaa\xe7\xa9\xba\xe8\xb0\x83\xe4\xbc\x9a\xe5\x8f\x98\xe9\xa2\x91\xe5\x90\x97\n\xe7\xa9\xba\xe8\xb0\x83 \xe5\x8f\x98\xe9\xa2\x91\n\xe5\x8f\xaf\xe4\xbb\xa5\xe7\x9a\x84\n1\n2020/8/14', 
    b'\xe8\xbf\x99\xe4\xb8\xaa\xe8\xa1\xa3\xe6\x9c\x8d\xe9\x83\xbd\xe6\x9c\x89\xe4\xbb\x80\xe4\xb9\x88\xe9\xa2\x9c\xe8\x89\xb2\n\xe9\xa2\x9c\xe8\x89\xb2\n\xe9\xbb\x91\xe7\x9a\x84\xe7\x99\xbd\xe7\x9a\x84\xe9\x83\xbd\xe6\x9c\x89\xe5\x95\x8a\n1\n2020/8/14', 
    b'\xe8\xbf\x99\xe4\xb8\xaa\xe8\xa1\xa3\xe6\x9c\x8d\xe4\xbb\xb7\xe6\xa0\xbc\xe6\x80\x8e\xe4\xb9\x88\xe6\xa0\xb7\n\xe4\xbb\xb7\xe6\xa0\xbc\n120\xe5\x85\x83\n1\n2020/8/14']
    
    :return:         [{'query':'这个空调会变频吗', 'keywords': ['空调', '变频'], 'answer': '可以的', 'state': '1', 'time': '2020/8/14'},
                {'query': '这个衣服都有什么颜色', 'keywords': ['颜色'], 'answer': '黑的白的都有啊', 'state': '1', 'time': '2020/8/14'},
                {'query': '这个衣服价格怎么样', 'keywords': ['价格'], 'answer': '120元', 'state': '1', 'time': '2020/8/14'}]
    '''
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


def dictlist2redis(datalist):    #字典列表数据转换为 redis的hash数据

    '''
    :param datalist: 
        [{'query':'这个空调会变频吗', 'keywords': ['空调', '变频'], 'answer': '可以的', 'state': '1', 'time': '2020/8/14'},
                {'query': '这个衣服都有什么颜色', 'keywords': ['颜色'], 'answer': '黑的白的都有啊', 'state': '1', 'time': '2020/8/14'},
                {'query': '这个衣服价格怎么样', 'keywords': ['价格'], 'answer': '120元', 'state': '1', 'time': '2020/8/14'}]
                
    :return: {0: '这个空调会变频吗\n空调 变频\n可以的\n1\n2020/8/14\n', 1: '这个衣服都有什么颜色\n颜色\n黑的白的都有啊\n1\n2020/8/14\n', 2: '这个衣服价格怎么样\n价格\n120元\n1\n2020/8/14\n'}
    '''

    redis_data = {}
    for idx,data in enumerate(datalist):
        query = data["query"]
        keywords = " ".join(data["keywords"])
        answer = data["answer"]
        state = str(data["state"])
        time = data["time"]
        data_str = query+"\n"+keywords+"\n"+answer+"\n"+state+"\n"+time+"\n"
        redis_data[idx] = data_str

    return redis_data