from marshmallow import Schema, fields, validate, ValidationError


class BuyerRegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
    full_name = fields.String(required=True, validate=validate.Length(min=2))


class OrderCreateSchema(Schema):
    livestock_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))


def validate_request(schema, data):
    """
    Utility function to validate request data
    """
    try:
        return schema.load(data)
    except ValidationError as err:
        raise ValidationError(err.messages)
