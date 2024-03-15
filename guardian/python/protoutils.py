from google.protobuf.json_format import MessageToDict, Parse
import json

class ProtoUtils(object):
    @staticmethod
    def to_json(obj):
        """
        Convert a protobuf object to JSON

        Args:
            obj: The object to convert
        Returns:
            JSON string representation
        """
        return MessageToDict(
            obj,
            including_default_value_fields = True,
            preserving_proto_field_name = True,
            use_integers_for_enums = False,
        )

    @staticmethod
    def from_json(data, obj) -> None:
        """
        Convert JSON to a protobuf

        Args:
            data: The JSON data (dict or str)
            obj: The protobuf to fill in
        """
        if not isinstance(data, str):
            data = json.dumps(data)
        Parse(data, obj)

