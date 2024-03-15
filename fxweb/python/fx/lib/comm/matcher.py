"""
@file      matcher.py
@author    James Espinoza(jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Implements generic matchers for matching sent responses
"""
from abc import ABCMeta, abstractmethod

from lib.utils.data_structures import ExcryptMessage

class Matcher(metaclass=ABCMeta):
    """
    Matcher base class
    """

    def __init__(self):
        self.is_complete = False
        self.matched = True

    def init_match_status(self, data):
        """
        Inits the matcher object
        :param data: The data to init the matcher with. The data type and format
                     of this object is variable based on implementation of the Matcher
        :return: Returns the data that was passed in by default
        """
        return data

    def matches(self, message):
        """
        Checks to see if a message response matches the original request
        :param data: The data match against
        """
        return self.matched

    @abstractmethod
    def update_match_status(self, data):
        """
        Updates the completion status object state
        :param data: The data to update the matcher state with
        """
        pass

class SynchResponseMatcher(Matcher):
    """
    Implements a synchronous response matcher
    :param synch_tag: The response tag to check the matching value against
    :param synch_value: The value to match against
    """
    def __init__(self, synch_tag = 'AG', synch_value = ''):
        super(SynchResponseMatcher, self).__init__()
        self.synch_tag = synch_tag
        self.synch_value = synch_value
        self.matched = False

    def init_match_status(self, data):
        """
        Inits the matcher object
        :param data: The data to init the matcher with. Data must be a list with the
                     first index as the request synch tag, the second index as the message that
                     is going to be sent
        :return: Returns the data that was passed in by default
        """
        # TODO The message class needs to be abstracted out to support different
        #      implementations of ExcryptMessage
        req_tag = data[0]
        em = ExcryptMessage(data[1])
        em.setFieldAsString(req_tag, self.synch_value)
        return em.getText()
       
    def matches(self, data):
        """
        Checks to see if a message response matches the original request by checking the
        response synch tag value with the stored synch tag value
        :param data: The data match against
        """
        em = ExcryptMessage(data)
        self.matched = em.hasContext(self.synch_tag) and em.getContext(self.synch_tag) == self.synch_value
        return self.matched

    def update_match_status(self, data):
        """
        Updates the completion status object state
        :param data: The data to update the matcher state with
        """
        self.is_complete = self.matched

class CountResponseMatcher(SynchResponseMatcher):
    """
    Implements a synchronous response matcher that waits for expected_response_count
    number of responses
    :param expected_response_count: The number of responses that are expected before
                                    the matcher is complete
    :param synch_tag: The response tag to check the matching value against
    :param synch_value: The value to match against
    """
    def __init__(self, expected_response_count, synch_tag = 'AG', synch_value = ''):
        super(CountResponseMatcher, self).__init__(synch_tag, synch_value)
        self.total_response_count = 0
        self.expected_response_count = expected_response_count

    def update_match_status(self, data):
        """
        Updates the completion status object state
        :param data: The data to update the matcher state with
        """
        response = data

        if response:
            self.total_response_count += 1

        if self.total_response_count >= self.expected_response_count:
            self.is_complete = True

