from marshmallow import Schema, fields, validate, ValidationError

class category_schema(Schema):
    name = fields.String(required=True)
class record_schema(Schema):
    category_id = fields.Integer(required=True, validate=validate.Range(min=0))
    user_id = fields.Integer(required=True, validate=validate.Range(min=0))
    amount = fields.Float(required=True, validate=validate.Range(min=0.0))
class income_accounting_schema(Schema):
    balance = fields.Float(required=True, validate=validate.Range(min=0.0, error="Balance error"))


class user_schema(Schema):
    id = fields.Int()
    username = fields.String(required=True)
    password = fields.String(required=True)
    income_accounting = fields.Nested(income_accounting_schema)
