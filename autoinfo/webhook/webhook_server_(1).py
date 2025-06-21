from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/skill', methods=['POST'])
def skill():
    # 예시 응답
    return jsonify({"version": "2.0", "template": {"outputs": [{"simpleText": {"text": "미션 현황입니다."}}]}})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)