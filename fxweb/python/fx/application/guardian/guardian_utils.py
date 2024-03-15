"""
@file guardian_utils.py
@author Daniel Jones (djones@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2018

@section DESCRIPTION
Utilities for guardian
"""
from broker import Broker
from librk import ManagedObjectUtils, BalancerUtils

def is_remote_object_authorized(manager, obj_id, parent_id, user_store):
    """Check if the specific object is authorized through the guardian
    Arguments:
        obj: the object to check (with manager, obj_id, and parent_id)
        user_store: the store of users
    Returns: True if authorized false otherwise
    """
    if manager is None and obj_id is None:
        return True

    mo_type = ManagedObjectUtils.getType(manager)
    if BalancerUtils.isBalancedDeviceGroup(mo_type):
        return obj_id in user_store.authenticated_remote_groups
    elif BalancerUtils.isBalancedDevice(mo_type):
        return obj_id in user_store.authenticated_remote_devices or \
            parent_id in user_store.authenticated_remote_groups

    return False


