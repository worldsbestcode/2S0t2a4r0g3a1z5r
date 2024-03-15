from marshmallow import Schema, fields

class BaseResponse(Schema):
    status = fields.String(
        required=True,
        description="Status string",
        example="Success",
    )

    message = fields.String(
        required=True,
        description="Human readable sucess or error message",
        example="Success",
    )

class ErrorResponse(BaseResponse):
    code = fields.Integer(
        required=True,
        description="Numeric Futurex response code identifier",
        example=101,
    )

    field = fields.String(
        required=True,
        description="Additional context for error reason. Use in combination with code to catch specific errors.",
        example="uuid",
    )

    status = fields.String(
        required=True,
        description="Status string",
        example="Failure",
    )

    message = fields.String(
        required=True,
        description="Human readable message",
        example="Invalid UUID format.",
    )

    type = fields.String(
        required=True,
        description="String Futurex response code identifier",
        example="ArgumentParseError",
    )


class SchemaErrorResponse(BaseResponse):
    status = fields.String(
        required=True,
        description="Status string",
        example="Failure",
    )

    message = fields.String(
        required=True,
        description="Human readable message",
        example="Validation error",
    )

    errors = fields.List(
        fields.String,
        required=True,
        description="Validation errors",
        example=["Missing data for required field: json.authCredentials","Unknown field: json.aauthCredentials"],
    )

