# 导入Flask类
from flask import Flask,request,jsonify

from data_process import Data_process
from keyword_matching import Match

#Flask类接收一个参数__name__
app = Flask(__name__)

@app.route('/get_all_data', methods=['POST'])
def get_data():
    id = request.args.get('id')

    data_process = Data_process(id)
    datas = data_process.read_all_data_state_1()

    datas_dict = {}
    for idx,data in enumerate(datas):
        _data = {}
        _data["query"] = data["query"]
        _data["keywords"] = data["keywords"]
        _data["answer"] = data["answer"]

        datas_dict[idx] = _data

    json_dict = {
        "id": id,
        "datas": datas_dict
    }
    return jsonify(json_dict)


@app.route('/get_answer', methods=['POST'])
def get_answer():
    id = request.args.get('id')
    query = request.args.get('query')

    match = Match(id)
    answer = match.find_max_score_answer(query)

    json_dict = {
        "id": id,
        "answer": answer
    }
    return jsonify(json_dict)



# Flask应用程序实例的run方法启动WEB服务器
if __name__ == '__main__':
    app.run(host="0.0.0.0")