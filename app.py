import os
import certifi
import math
import uuid
from pymongo import MongoClient
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

load_dotenv()
MONGODB_URL = os.getenv('MONGODB_URL')

ca = certifi.where()
client = MongoClient(MONGODB_URL, tlsCAFile=ca)
db = client.rollingsparta


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/member/<member_id>')
def member(member_id):
    return render_template('member.html')


@app.route('/api/team', methods=["GET"])
def member_list():
    all_member = list(db.member.find({}, {'_id': False, 'mbti': False,
                      'musicURL': False, 'location': False, 'hobby': False}).sort('name', 1))
    return jsonify({'result': 'success', 'list': all_member})


@app.route('/api/member/<member_id>', methods=["GET"])
def get_member(member_id):
    member_info = db.member.find_one({'memberId': member_id}, {'_id': False})
    if (member_info is None):
        return jsonify({'result': 'fail', 'message': '없는 팀원인데요!'})
    return jsonify({'result': 'success', 'data': member_info})


@app.route('/api/rollingpaper/<member_id>', methods=["POST"])
def make_rolling(member_id):
    doc = {
        'memberId': member_id,
        'commentId': str(uuid.uuid4()),
        'name': request.form['name'],
        'password': request.form['password'],
        'comment': request.form['comment'],
        'date': request.form['date'],
    }
    db.comment.insert_one(doc)
    return jsonify({'result': 'success', 'message': '등록이 완료되었습니다.'})


@app.route('/api/rollingpaper/<member_id>', methods=["GET"])
def get_rolling(member_id):
    page = request.args.get('page', 1, type=int)
    limit = 9
    tot_count = db.comment.count_documents({})
    last_page_num = math.ceil(tot_count / limit) - 1
    if page == 1:
        limit -= 1
    rolling_list = list(db.comment.find({'memberId': member_id}, {
                        '_id': False, 'memberId': False, 'password': False}).sort('date', -1).skip((page - 1) * limit).limit(limit))
    return jsonify({'result': 'success', 'list': rolling_list, 'limit': limit, 'page': page, 'last_page': last_page_num})


@app.route('/api/rollingpaper/<member_id>', methods=["DELETE"])
def del_rolling(member_id):
    comment_id = request.form['commentId']
    input_password = request.form['password']
    comment = db.comment.find_one({"commentId": comment_id})

    if comment['password'] != input_password:
        return jsonify({'result': 'fail', 'message': '비밀번호가 다릅니다.'})

    db.comment.delete_one({"commentId": comment_id})
    return jsonify({'result': 'success', 'message': '삭제 완료되었습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
