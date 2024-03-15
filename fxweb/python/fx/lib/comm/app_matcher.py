"""
@file      app_matcher.py
@author    James Espinoza(jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Implements RK application specific matchers for matching sent responses
"""
from matcher import Matcher, SynchResponseMatcher
from librk import ManagedObject, ManagedObjectUtils
from lib.utils.data_structures import ExcryptMessage
from application_log import ApplicationLogger as Log

class QueryMatcher(SynchResponseMatcher):
    """
    Implements a matcher to match any messages that are associated with 
    a RKY12 query filter command to the server
    :param manager: Manager of objects to query for
    :param synch_tag: Synch tag to check response against
    :param synch_value: Synch value to match reponse against
    """
    def __init__(self, manager, synch_tag, synch_value, command = "RKY12", match_manager=True):
        super(QueryMatcher, self).__init__(synch_tag, synch_value)
        self.manager = manager
        self.command = command
        self.match_manager = match_manager

    def get_manager(self):
        """Gets the manager list for this matcher.
        
        Returns:
            list -- Manager list.
        """

        return self.manager

    def matches(self, data):
        """
        A matcher to match all messages from a query filter
        :param data: Individual message to match
        :return: True if matches, false otherwise
        """
        self.matched = False

        em = ExcryptMessage(data)

        if em.getCommand() == self.command and (em.getField("BB") == "Y" or em.getField("BB") == "N") and em.getField(self.synch_tag) == self.synch_value:
            self.matched = super(QueryMatcher, self).matches(data)
        else :
            mo_type = ManagedObjectUtils.getType(em.getField("MN")) if em.getField("MN") else ManagedObject.UNKNOWN
            
            if self.match_manager:
                self.matched = mo_type in self.manager and em.getCommand() == "RKY400" and em.getField(self.synch_tag) == self.synch_value
            else:
                self.matched = em.getCommand() == "RKY400" and em.getField(self.synch_tag) == self.synch_value

        return self.matched

    def update_match_status(self, data):
        """
        Check all responses for an RKY12 success response. The completion event
        has occurred once this occurs
        :param data:  Indvidual message to check completion status
        """
        em = ExcryptMessage(data)
        if em.getCommand() == self.command and (em.getField("BB") == "Y" or em.getField("BB") == "N") and em.getField(self.synch_tag) == self.synch_value:
            self.is_complete = super(QueryMatcher, self).matches(data)

class UpdateObjectMatcher(SynchResponseMatcher):
    """
    Implements a matcher to match any messages that are associated with 
    a RKY2 object update command from the server
    :param manager: Manager of objects to query for
    """
    def __init__(self, manager):
        # NOTE: RKY400 now sends updates from filters
        self.command = "RKY2"
        self.manager = manager

    def matches(self, data):
        """
        A matcher to match all messages from a query filter
        :param data: Individual message to match
        :return: True if matches, false otherwise
        """
        self.matched = False

        em = ExcryptMessage(data)
        if em.getCommand() == self.command:
            self.matched = em.getField("MN") in self.manager
        return self.matched

class DeleteObjectMatcher(SynchResponseMatcher):
    """
    Implements a matcher for the RKY3 delete object response
    Note: This is currently needed because RKY3 does not respond with a 
    synch ID. This can be removed once RKY3 supports synch ids
    :param dbid: ID of object that was deleted
    :param manager: Manager of object that was deleted
    """
    def __init__(self, manager, dbid = -1):
        super(DeleteObjectMatcher, self).__init__()
        self.command = "RKY3"
        self.dbid = str(dbid)
        self.manager = manager

    def matches(self, data):
        """
        A matcher to match all messages from a query filter
        :param data: Individual message to match
        :return: True if matches, false otherwise
        """
        self.matched = False
        em = ExcryptMessage(data)
        self.matched = em.getCommand() == "RKY3" and em.getField("MN") in self.manager

        if self.matched and self.dbid and self.dbid != '-1':
            self.matched = em.getField("ID") == self.dbid
        return self.matched

class NotifyExternalChangeMatcher(SynchResponseMatcher):
    """
    Implements a matcher for the NotifyExternalChange (RKY57) event
    :param manager: Manager of objects to query for
    """
    def __init__(self, manager):
        self.command = "RKY57"
        self.manager = manager

    def matches(self, data):
        """
        A matcher to match all messages from a query filter
        :param data: Individual message to match
        :return: True if matches, false otherwise
        """
        self.matched = False

        em = ExcryptMessage(data)
        self.matched = em.getCommand() == self.command and em.getField("MN") in self.manager

        return self.matched
