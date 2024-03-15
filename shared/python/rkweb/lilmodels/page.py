from marshmallow import fields
from marshmallow import validate

from rkweb.lilmodels.base import field, Model

class PagedRequestModel(Model):
    page: int = field(
        description="The page number",
        required=False,
        load_default=1,
        validate=validate.Range(1),
    )
    pageSize: int = field(
        description="The number of results per page",
        required=False,
        load_default=100,
        validate=validate.Range(1, 100),
    )

class PagedResponseModel(Model):
    page: int = field(
        description="The current page number",
        required=True,
        validate=validate.Range(1),
    )
    pageSize: int = field(
        description="The number of results per page",
        required=True,
        validate=validate.Range(1, 100),
    )
    total: int = field(
        description="The total number of results",
        required=True,
        validate=validate.Range(0),
    )
    totalPages: int = field(
        description="The total number of pages",
        required=True,
        validate=validate.Range(0),
    )
    previousPage: int = field(
        description="The previous page number",
        required=True,
        validate=validate.Range(1),
    )
    nextPage: int = field(
        description="The next page number",
        required=True,
        validate=validate.Range(1),
    )

def PagedResponseField():
    return field(
        description="Response pages information",
        required=True,
        marshmallow_field=fields.Nested(PagedResponseModel.schema)
    )
