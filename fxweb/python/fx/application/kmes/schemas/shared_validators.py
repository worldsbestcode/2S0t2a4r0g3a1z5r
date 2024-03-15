"""
@file      kmes/schemas/shared_validators.py
@author    Dalton Mcgee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Validators shared among multiple schema modules
"""

from marshmallow import ValidationError


def pki_cert_validator(data):
    pkiTree = data.get("pkiTree", None)
    certId = data.get("certId", None)
    certName = data.get("certName", None)
    certAlias = data.get("certAlias", None)

    error_flag = False
    error_message = ""
    field_list = []

    if pkiTree is not None:
        field_list.append("certName, certAlias")
        if certName is None and certAlias is None:
            error_message = "One field must be specified if pkiTree is specified"
            error_flag = True

        elif certName and certAlias:
            error_message = "Only one field must be specified if pkiTree is specified"
            error_flag = True

    elif pkiTree is None and certId is None:
        field_list.append("pkiTree, certId")
        error_message = "Must specify pkiTree or certId"
        error_flag = True

    if error_flag:
        raise ValidationError(error_message, ",".join(field_list))
