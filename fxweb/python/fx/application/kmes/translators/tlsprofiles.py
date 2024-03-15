import lib.utils.hapi_parsers as parsers
from base.base_translator import BaseTranslator
from kmes.schemas import tlsprofiles as schemas

def serialize_fxcerts_type(request):
    if 'fxcertsType' in request:
        if 'certType' not in request:
            request['certType'] = 'FxCerts'
        fxType = request['fxcertsType']
        if fxType == 'RSA Admin':
            request['generatedType'] = '1'
            request['fxcertsType'] = '1'
        elif fxType == 'RSA Prod':
            request['generatedType'] = '1'
            request['fxcertsType'] = '2'
        elif fxType == 'ECC Admin':
            request['generatedType'] = '2'
            request['fxcertsType'] = '1'
        elif fxType == 'ECC Prod':
            request['generatedType'] = '2'
            request['fxcertsType'] = '2'
    elif 'generatedType' in request:
        if 'generatedType' == 'RSA':
            request['generatedType'] = '1'
        elif 'generatedType' == 'ECC':
            request['generatedType'] = '2'

class CreateTlsProfile(BaseTranslator):
    request_schema = schemas.TlsProfile(exclude=("uuid",))

    def __init__(self, server_interface):
        request_map = {
            "name": "NA",
            "certType": "ET",
            "certUuid": "CU",
            "trustedCertUuids": ("TU", parsers.serialize_csv),
            "anonymous": ("AY", parsers.serialize_bool),
            "fxcertsType": "FT",
            "generatedType": "PT",
            "sslAsTrusted": ("TR", parsers.serialize_bool),
            "ciphers": ("PH", parsers.serialize_csv),
            "protocols": ("PR", parsers.serialize_csv),
        }

        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "uuid",
        }

        super().__init__(server_interface, "TlsProfiles", "TTCP", request_map, response_map)

    def preprocess_request(self, request):
        serialize_fxcerts_type(request)
        return request

class UpdateTlsProfile(BaseTranslator):
    request_schema = schemas.TlsProfile()

    def __init__(self, server_interface):
        request_map = {
            "uuid": "ID",
            "name": "NH",
            "certType": "ET",
            "certUuid": "CU",
            "trustedCertUuids": ("TU", parsers.serialize_csv),
            "anonymous": ("AY", parsers.serialize_bool),
            "fxcertsType": "FT",
            "generatedType": "PT",
            "sslAsTrusted": ("TR", parsers.serialize_bool),
            "ciphers": ("PH", parsers.serialize_csv),
            "protocols": ("PR", parsers.serialize_csv),
        }

        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(server_interface, "TlsProfiles", "TTUP", request_map, response_map)

    def preprocess_request(self, request):
        serialize_fxcerts_type(request)
        return request

class RetrieveTlsProfile(BaseTranslator):
    request_schema = schemas.Resource()

    def __init__(self, server_interface):
        request_map = {
            "uuid": "ID",
        }

        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "uuid",
            "NA": "name",
            "ET": "certType",
            "CU": "certUuid",
            "TU": ("trustedCertUuids", parsers.parse_csv),
            "AY": ("anonymous", parsers.parse_bool),
            "FT": "fxcertsType",
            "PT": "generatedType",
            "TR": ("sslAsTrusted", parsers.parse_bool),
            "PH": ("ciphers", parsers.parse_csv),
            "PR": ("protocols", parsers.parse_csv),
        }

        super().__init__(server_interface, "TlsProfiles", "TTRP", request_map, response_map)

    def finalize_response(self, response):
        if response.get("status") != "Y" or response.get("message"):
            return response

        # Converts the fxcerts/algo from int to string
        if "fxcertsType" in response:
            if response["fxcertsType"] == "1" and response["generatedType"] == "1":
                response["fxcertsType"] = "RSA Admin"
                response["generatedType"] = "RSA"

            elif response["fxcertsType"] == "2" and response["generatedType"] == "1":
                response["fxcertsType"] = "RSA Prod"
                response["generatedType"] = "RSA"

            elif response["fxcertsType"] == "1" and response["generatedType"] == "2":
                response["fxcertsType"] = "ECC Admin"
                response["generatedType"] = "ECC"

            elif response["fxcertsType"] == "2" and response["generatedType"] == "2":
                response["fxcertsType"] = "ECC Prod"
                response["generatedType"] = "ECC"

        elif "generatedType" in response:
            if response["generatedType"] == "1":
                response["generatedType"] = "RSA"

            elif respoinse["generatedType"] == "2":
                response["generatedType"] = "ECC"

        return response

class ListTlsProfiles(BaseTranslator):
    request_schema = schemas.ListTlsProfiles()

    def __init__(self, server_interface):
        request_map = {
            "page": ("CH", (1).__rsub__),  # pages start at 1, chunks start at 0
            "pageCount": "CS",
            "MN": "MN",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": ("profiles.uuid", parsers.parse_csv),
            "NA": ("profiles.name", parsers.parse_csv),
            "CC": ("pageCount", int),
            "CT": ("totalPages", int),
            "TO": ("totalItems", int),
        }

        super().__init__(server_interface, "TlsProfiles", "RKLN", request_map, response_map)

    def preprocess_request(self, request):
        request["MN"] = "TLSPROFILE"
        return request

    def finalize_response(self, response):
        if response.get("status") != "Y" or response.get("message"):
            return response

        response["currentPage"] = int(self.raw_request.get("page", 1))
        if response["currentPage"] < response["totalPages"]:
            response["nextPage"] = response["currentPage"] + 1

        # Transpose/unpivot groups from dict of lists to list of dicts:
        response["profiles"] = parsers.unpivot_dict(response["profiles"])

        return response

class DeleteTlsProfile(BaseTranslator):
    request_schema = schemas.Resource()

    def __init__(self, server_interface):
        request_map = {
            "uuid": "ID",
        }

        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(server_interface, "TlsProfiles", "TTDP", request_map, response_map)
