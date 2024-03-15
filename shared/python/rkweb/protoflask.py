import json
from google.protobuf import json_format

from rkweb.flaskutils import abort
from flask import request

from rkproto.mo.ObjectFilter_pb2 import ObjectFilter

def serialize_filter_results(pagination, objs) -> dict:
    """
    Convert the response from a protobuf object select to a dictionary response

    Args:
        pagination: Pagination information from select response
        objs: Protobuf results
    Returns:
        Response dictionary
    """

    results = []
    for obj in objs:
        str_data = json_format.MessageToJson(obj, including_default_value_fields=True)
        dict_data = json.loads(str_data)
        results.append(dict_data)

    data = serialize_pagination(pagination)
    data['results'] = results
    return data

def serialize_pagination(pagination) -> dict:

    # Calculate page logic from chunk logic
    page = pagination.chunk + 1

    total_pages = pagination.total_chunks
    if total_pages < 1:
        total_pages = 1

    previous_page = page - 1
    if previous_page < 1:
        previous_page = 1

    next_page = page + 1
    if next_page > total_pages:
        next_page = total_pages

    return {
        'page': page,
        'pageSize': pagination.chunk_size,
        'total': pagination.total,
        'totalPages': total_pages,
        'previousPage': previous_page,
        'nextPage': next_page,
    }

def load_paging(args, obj_filter: ObjectFilter) -> None:
    """
    Load object filter chunk settings from request parameters.
    This assumes the endpoint uses the PagedRequestModel.

    Args:
        obj_filter: The object filter to set chunk information on
    """
    page = int(args.get('page', 1))
    page_size = int(args.get('pageSize', 100))

    obj_filter.chunk = page - 1
    obj_filter.chunk_size = page_size

def args_to_proto(args, proto_type):
    # Convert query args to protobuf

    # Booleans get turned into strings, and protobuf wants them as bool type
    def sanitize(data: dict) -> None:
        for key in data.keys():
            if isinstance(data[key], dict):
                sanitize(data[key])
            elif data[key] == 'true':
                data[key] = True
            elif data[key] == 'false':
                data[key] = False
    # Get into a mutable dict and sanitize
    sanitized_dict = args
    sanitize(sanitized_dict)

    # Convert to JSON to proto
    request_data = json.dumps(sanitized_dict)
    msg = proto_type()
    try:
        json_format.Parse(request_data, msg)
    except Exception as e:
        # Handle parsing errors
        abort(400, str(e))
    return msg

def proto_to_dict(obj) -> dict:
    # Convert protobuf to python dictionary
    return json.loads(json_format.MessageToJson(obj, including_default_value_fields=True))
