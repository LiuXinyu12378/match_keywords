import string
import jieba
import jieba.posseg as psg
import logging

# 关闭jieba日制
jieba.setLogLevel(logging.INFO)

jieba.load_userdict("./the_words/keywords.txt")

stopwords_path = "./the_words/stopwords.txt"

stopwords = [i.strip() for i in open(stopwords_path, encoding="utf-8").readlines()]
continue_words = string.ascii_lowercase + string.digits
punctuation = string.punctuation+"！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘'‛“”„‟…‧﹏."

def _cut_sentence_by_word(sentence):
    '''
    按照单个字进行分词
    :param sentence:
    :return:
    '''
    temp = ""
    result = []
    for word in sentence:
        if word in continue_words:
            temp += word
        else:
            if len(temp) > 0:
                result.append(temp)
                temp = ""
            result.append(word)
    if len(temp) > 0:
        result.append(temp)
    return [i for i in result if i not in punctuation]


def _cut_sentence(sentence, use_stopwords, use_seg):
    '''
    按照词语进行分词
    :param sentence:
    :return:
    '''
    if not use_seg:
        result = jieba.lcut_for_search(sentence,HMM=True)
    else:
        result = [(i.word, i.flag) for i in psg.lcut(sentence)]
    if use_stopwords:
        if not use_seg:
            result = [i for i in result if i not in stopwords]
        else:
            result = [i for i in result if i[0] not in stopwords]

    return [i for i in result if i not in punctuation]


def cut(sentence, by_word=False, use_stopwords=False, use_seg=False):
    '''
    封装上述方法
    :param sentence:
    :param by_word:
    :param use_stopwords:
    :param use_seg:
    :return:
    '''
    if by_word:
        return _cut_sentence_by_word(sentence)
    else:
        return _cut_sentence(sentence, use_stopwords, use_seg)


if __name__ == '__main__':
    print(_cut_sentence_by_word("python邓紫棋画python"))
    # print(cut("python邓紫棋画人工智能+python啊", use_seg=True, use_stopwords=False))

    words = cut("我想知道格力空调变频怎么样？", use_stopwords=True)
    print(words)

