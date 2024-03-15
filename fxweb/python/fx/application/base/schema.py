from marshmallow import (
    Schema,
    fields,
    validate,
)


class ResponseSchema(Schema):
    result = fields.String(
        attribute='result',
        description='The success status of the request',
        required=True,
        example='Success',
        default='Failure',
        validate=validate.OneOf([
            'Success',
            'Failure',
        ]),
    )
    message = fields.String(
        attribute='message',
        description='Any errors that occur will be stored here',
        example='Failed to perform requested action.',
        default='',
    )
