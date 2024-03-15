"""
@file      cache.py
@author    James Espinoza (jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
The middleware cache for temporary objects
"""
import fx
import rk_defines
from rk_exceptions import CacheUpdateException
from application_log import ApplicationLogger
from librk import (
    ManagedObject,
    ManagedObjectUtils,
    MapManager,
    MMManagerContainer,
    ExcryptMessage
)


class Cache():
    """
    The Object Cache to reduce server queries
    """
    def __init__(self):
        self.mo_container = MMManagerContainer()
        for mo_type in rk_defines.BALANCER_MANAGERS:
            self.mo_container.setManagerAlloc(mo_type)

    def update_cache(self, objs, obj_type):
        try:
            map_manager = self.mo_container.getManager(obj_type)
            for msg in objs:
                mo = ManagedObjectUtils.createObjectFromType(obj_type, 0)
                mo.fromMessage(ExcryptMessage(str(msg)))

                if mo is not None:
                    map_manager.modify(mo)

        except Exception as exception:
            raise CacheUpdateException(exception=exception)

    def size(self, obj_type):
        map_manager = self.mo_container.getManager(obj_type)
        count = 0

        if map_manager is not None:
            count = map_manager.size()

        return count

    def get_objects(self, obj_type):
        map_manager = self.mo_container.getManager(obj_type)
        return map_manager.getCopyOfObjects()

    def get_full_cache(self):
        mo = {}
        for manager in rk_defines.BALANCER_MANAGERS:
            mo[manager] = self.get_objects(manager)

        return mo
