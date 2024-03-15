from marshmallow import Schema, fields


__all__ = ['Echo']


class Echo(Schema):
    message = fields.String()
