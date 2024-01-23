from my_app import app, db
from flask import Flask, jsonify, request
from datetime import datetime
from my_app.schems import user_schema, category_schema, record_schema, income_accounting_schema
from my_app.model import User, IncomeAccounting, Category, Record
from marshmallow.exceptions import ValidationError



with app.app_context():
    db.create_all()
    db.session.commit()


@app.route("/")
def notify_func():
    return f"<p>Laboratory work is done</p><a href='/healthcheck'>Healthcheck</a>"


@app.route("/healthcheck")
def healthcheck():
    response = jsonify(date=datetime.now(), status="OK")
    response.status_code = 200
    return response



@app.route("/user/<int:user_id>", methods=['GET', 'DELETE'])
def control_users(user_id):
    with app.app_context():
        user = User.query.get(user_id)

        if not user:
            return jsonify({'ERROR': f'USER ID - {user_id} IS NOT EXIST'}), 404

        income_accounting = IncomeAccounting.query.filter_by(user_id=user_id).first()

        if request.method == "GET":
            user_data = {
                'id': user.id,
                'username': user.username,
                'income_acc_balance': income_accounting.balance if income_accounting else 0.0
            }
            return jsonify(user_data), 200

        elif request.method == "DELETE":
            try:
                db.session.delete(user)
                if income_accounting:
                    db.session.delete(income_accounting)
                db.session.commit()
                return jsonify({'MESSAGE': f'USER ID - {user_id} DELETED'}), 200
            except Exception as e:
                return jsonify({'ERROR': str(e)}), 500



@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()

    user_sch = user_schema()
    try:
        user_data = user_sch.load(data)
    except ValidationError as err:
        return jsonify({'ERROR': err.messages}), 400

    new_user = User(
        username=user_data["username"],
        income_accounting =IncomeAccounting(**user_data.get("income_accounting", {}))
    )

    with app.app_context():
        db.session.add(new_user)
        db.session.commit()

        user_response = {
            'user_id': new_user.id,
            'income_acc_ballance': new_user.income_accounting.balance
        }

        return jsonify(user_response), 200


@app.route('/users', methods=['GET'])
def get_users():
    with app.app_context():
        users_data = {
            user.id: {"username": user.username} for user in User.query.all()
        }
        return jsonify(users_data)



@app.route('/category', methods=['POST', 'GET'])
def manage_category():
    if request.method == 'GET':
        with app.app_context():
            categories_data = {
                category.id: {"name": category.name} for category in Category.query.all()
            }
            return jsonify(categories_data)

    elif request.method == 'POST':
        data = request.get_json()
        cat_schema = category_schema()
        try:
            cat_data = cat_schema.load(data)
        except ValidationError as err:
            return jsonify({'ERROR': err.messages}), 400

        new_category = Category(name=cat_data["name"])
        with app.app_context():
            db.session.add(new_category)
            db.session.commit()

            category_response = {
                "id": new_category.id,
                "name": new_category.name
            }

            return jsonify(category_response), 200


@app.route('/category/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    with app.app_context():
        category = Category.query.get(cat_id)

        if not category:
            return jsonify({'ERROR': f'CATEGORY ID - {cat_id} NOT EXIST'}), 404

        db.session.delete(category)
        db.session.commit()
        return jsonify({'MESSAGE': f'CATEGORY ID - {cat_id} DELETED'}), 200


@app.route('/records', methods=['GET'])
def get_all_records():
    with app.app_context():
        records_data = {
            "records": [
                {
                    "id": record.id,
                    "user_id": record.user_id,
                    "category_id": record.category_id,
                    "amount": record.amount,
                    "created_at": record.created_at
                } for record in Record.query.all()
            ]
        }
        return jsonify(records_data)


@app.route('/record/<int:record_id>', methods=['GET', 'DELETE'])
def manage_record(record_id):
    with app.app_context():
        record = Record.query.get(record_id)

        if not record:
            return jsonify({"ERROR": f"RECORD ID - {record_id} NOT EXIST"}), 404

        if request.method == "GET":
            record_data = {
                "id": record.id,
                "user_id": record.user_id,
                "cat_id": record.category_id,
                "amount": record.amount,
                "created_at": record.created_at
            }
            return jsonify(record_data), 200

        elif request.method == "DELETE":
            db.session.delete(record)
            db.session.commit()
            return jsonify({'MESSAGE': f'RECORD ID - {record_id} DELETED'}), 200


@app.route('/record', methods=['POST', 'GET'])
def manage_records():
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        category_id = request.args.get('category_id')

        if not user_id and not category_id:
           return jsonify({'ERROR': 'SPECIFY USER ID AND CATEGORY ID'}), 400


        query = Record.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        if category_id:
            query = query.filter_by(category_id=category_id)

        need_records = query.all()
        print(need_records)
        records_data = {
           record.id: {
               "user_id": record.user_id,
               "cat_id": record.category_id,
               "amount": record.amount,
               "created_at": record.created_at
           } for record in need_records
        }
        return jsonify(records_data)

    elif request.method == 'POST':
        data = request.get_json()

        record_sch = record_schema()
        try:
            record_data = record_sch.load(data)
        except ValidationError as err:
            return jsonify({'ERROR': err.messages}), 400

        user_id = record_data['user_id']
        user = User.query.get(user_id)

        if not user:
            return jsonify({'ERROR': 'USER NOT EXIST'}), 404

        if user.income_accounting.balance < record_data['amount']:
            return jsonify({'ERROR': 'NOTHING'}), 400

        user.income_accounting.balance -= record_data['amount']
        db.session.commit()

        new_record = Record(
            user_id=user_id,
            category_id=record_data['category_id'],
            amount=record_data['amount']
        )

        with app.app_context():
            db.session.add(new_record)
            db.session.commit()

            record_response = {
                "id": new_record.id,
                "user_id": new_record.user_id,
                "cat_id": new_record.category_id,
                "amount": new_record.amount
            }

            return jsonify(record_response), 200

