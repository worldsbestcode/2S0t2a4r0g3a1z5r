"""
@file      rk_defines.py
@author    James Espinoza (jespinoza@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
Rk definition collections
"""
from librk import client, ManagedObject

ADD_CMD = client.command_str(client.eCodeObjectAdd)
DELETE_CMD = client.command_str(client.eCodeObjectDelete)
MODIFY_CMD = client.command_str(client.eCodeObjectModify)

CRUD_CMDS = [ADD_CMD, DELETE_CMD, MODIFY_CMD]

BALANCER_MANAGERS = [
    ManagedObject.CARDGROUP,
    ManagedObject.KMES_GROUP,
    ManagedObject.REMOTE_KEY_GROUP,
    ManagedObject.CARD,
    ManagedObject.GUARDIAN_DEVICE,
    ManagedObject.LOCAL_GUARDIAN_DEVICE,
    ManagedObject.KMES_DEVICE,
    ManagedObject.REMOTE_KEY_DEVICE,
]
