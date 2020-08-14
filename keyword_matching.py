from data_process import Data_process
from cut_sentences import cut


class Match():

    '''
    self.answer_score:{'这件衣服都有什么颜色？': [0, 0], '这件衣服都有什么尺码？': [1, 0], '美的变频空调真的很省电吗？': [2, 2], '这件衣服什么价格？': [3, 0], '格力变频空调真的很省电吗？': [4, 3]}
    格式：query：[idx,score]
    '''

    def __init__(self,id):
        self.id = id

    def keyword_matching(self,query):     #根据关键词匹配来返回每个query及对应的分数
        words = cut(query,use_stopwords=True)
        # print(words)

        data_process = Data_process(self.id)
        self.datas = data_process.read_all_data_state_1()

        self.answer_score = {}
        for idx,data in enumerate(self.datas):
            self.answer_score[data["query"]]=[idx,0]

        for word in words:
            for data in self.datas:
                if word in data["keywords"]:
                    self.answer_score[data["query"]][1] += 1

        return self.answer_score


    def find_max_score_answer(self,query):   #找到分数最高的query答案返回

        answer_score = self.keyword_matching(query)

        answer_score = sorted(answer_score.items(),key=lambda item:item[1][1],reverse=True)

        score =  answer_score[0][1][1]
        if  score != 0:  #判断分数不是0
            index = answer_score[0][1][0]  #找到idx索引值
            result =  self.datas[index]
            result_answer = result["answer"]

            return result_answer

        return None


if __name__ == '__main__':

    match = Match("000001")

    query = "我想知道尺码怎么样？"
    print(query,match.find_max_score_answer(query))

    query = "我想知道颜色怎么样？"
    print(query, match.find_max_score_answer(query))

    query = "我想知道价格怎么样？"
    print(query, match.find_max_score_answer(query))

    query = "我想知道格力空调变频怎么样？"
    print(query,match.find_max_score_answer(query))

