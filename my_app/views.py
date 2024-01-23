from my_app import app
from flask import Flask, jsonify, request
from datetime import datetime
import uuid

users = {}
categories = {}
records = {}

@app.route("/")
def notify_func():
    return f"<p>Laboratory work is done</p><a href='/healthcheck'>Healthcheck</a>"


@app.route("/healthcheck")
def healthcheck():
    response = jsonify(date=datetime.now(), status="OK")
    response.status_code = 200
    return response

@app.route("/user/<user_id>", methods=['GET', 'DELETE'])
def get_user(user_id):
    user_info = users.get(user_id)
    if not user_info:
        return jsonify({"ERROR": "User not found"}), 404
    return jsonify(user_info)

@app.route("/user/<user_id>", methods=['GET', 'DELETE'])
def delete_user(user_id):
    user_info = users.pop(user_id, None)
    if not user_info:
        return jsonify({"ERROR": "User not found"}), 404
    return jsonify(user_info)

@app.route('/user', methods=['POST'])
def post_user():
    user_info = request.get_json()
    if "username" not in user_info:
        return jsonify({"ERROR": "username are required"}), 400
    user_id = uuid.uuid4().hex
    user = {"id": user_id, **user_info}
    users[user_id] = user
    return jsonify(user)


@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(list(users.values()))


@app.route('/category', methods=['POST', 'GET', 'DELETE'])
def manager_category():
    if request.method == 'POST':
        category_info = request.get_json()
        if "name" not in category_info:
            return jsonify({"ERROR": "name are required"}), 400
        category_id = uuid.uuid4().hex
        category = {"id": category_id, **category_info}
        categories[category_id] = category
        return jsonify(category)

    elif request.method == 'GET':
        return jsonify(list(categories.values()))

    elif request.method == 'DELETE':
        category_id = request.args.get('id')
        if category_id:
            category = categories.pop(category_id, None)
            if not category:
                return jsonify({"ERROR": f"Category id {category_id} not found"}), 404
            return jsonify(category)
        else:
            categories.clear()
            return jsonify({"MESSAGE": "Categories are deleted"})


@app.route('/record/<record_id>', methods=['GET', 'DELETE'])
def manager_record(record_id):
    if request.method == 'GET':
        record = records.get(record_id)
        if not record:
            return jsonify({"ERROR": "Record not found"}), 404
        return jsonify(record)

    elif request.method == 'DELETE':
        record = records.pop(record_id, None)
        if not record:
            return jsonify({"ERROR": "Record not found"}), 404
        return jsonify(record)


@app.route('/record', methods=['POST'])
def post_record():
    record_info = request.get_json()
    user_id = record_info.get('userID')
    category_id = record_info.get('categoryID')

    if not user_id or not category_id:
        return jsonify({"ERROR": "Both user_id and category_id are needed"}), 400
    if user_id not in users:
        return jsonify({"ERROR": f"User with id {user_id} not found"}), 404
    if category_id not in categories:
        return jsonify({"ERROR": f"Category with id {category_id} not found"}), 404

    record_id = uuid.uuid4().hex
    record = {"id": record_id, **record_info}
    records[record_id] = record
    return jsonify(record)

@app.route('/record', methods=['GET'])
def get_record():
    user_id = request.args.get('userID')
    category_id = request.args.get('categoryID')
    if not user_id and not category_id:
        return jsonify({"ERROR": "Required user_id or category_id"}), 400
    filtered_records = [
        r for r in records.values() if (not user_id or r['user_id'] == user_id) or (not category_id or r['category_id'] == category_id)
    ]
    return jsonify(filtered_records)
