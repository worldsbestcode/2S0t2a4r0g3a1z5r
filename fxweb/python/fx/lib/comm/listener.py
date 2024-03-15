from application_log import ApplicationLogger
from librk import ManagedObjectUtils, ManagedObject, ExcryptMessage
from asynccomm import run_async_interval, synchronized
from collections import deque
import threading
import json

class Listener(object):
    """
    Listener Class for generic message listening
    """
    def __init__(self):
        """
        Initialize the Listener class
        """

    def handle(self, message, conn):
        return True

class SocketIOListener(Listener):
    """
    Listens for messages and emits updates to the browser over a web socket
    :param matcher:   Determines whether to handle the message
    :param socketio:  Provides the web socket
    :param event:     Name of the event being emitted
    :param namespace: Namespace to publish to
    """

    delay_secs = 1
    daemon_mode = True
    responses_lock = threading.Lock()

    def __init__(self, matcher=None, socketio=None, event=None, namespace=None):
        super(SocketIOListener, self).__init__()
        self.matcher = matcher
        self.socketio = socketio
        self.event = event
        self.namespace = namespace
        self.responses = deque([])
        self._send_responses()

    # Handle the message being passed in
    @synchronized(responses_lock)
    def handle(self, message, conn):

        # Handle the message if the matcher test passes or there is no matcher
        if (self.matcher and self.matcher.matches(message)) or not self.matcher:
            # Generate the response
            response_data = self.gen_response(ExcryptMessage(message))

            # Determine what to do with the new response
            if response_data is not None:
                # Attempt to remove redundant responses
                # Note: since this is referenced asynchronously, we must Iterate a copy
                for response in list(self.responses):
                    if self.is_stale_response(response, response_data):
                        self.responses.remove(response)
                # Enqueue the new response
                self.responses.append(response_data)

    # Determine whether a response should be removed
    def is_stale_response(self, old_response, new_response):
        # Nothing is removed by default
        return False

    # Generate a response based on the current message being handled
    def gen_response(self, em):
        # No response by default
        return {}

    # Flush all the responses to the web socket
    @synchronized(responses_lock)
    @run_async_interval(delay_secs, daemon_mode)
    def _send_responses(self):
        while self.responses and self.event and self.namespace:
            # Dequeue and emit the response
            response = self.responses.popleft()
            self.socketio.emit(self.event, response, namespace=self.namespace)


class SocketIOObjectUpdateListener(SocketIOListener):

    def __init__(self, matcher=None, socketio=None):
        """
        Initialize the SocketIOObjectUpdateListener class
        """
        super(SocketIOObjectUpdateListener, self).__init__(matcher, socketio, 'update_object', '/object')

    def gen_response(self, em):
        response_data = None
        motype = ManagedObject.TYPE(em.getFieldAsInt("TY"))
        mo = ManagedObjectUtils.createObjectFromTypeTake(motype, 0)

        if mo:
            mo.fromMessage(em)
            json_string = ""
            try:
                json_string = mo.toJSONString()
            except Exception as e:
                ApplicationLogger.error(
                    'Failed to convert object of type "{}" to JSON: {}.'
                    .format(str(motype), str(e)))

            json_object = {}
            try:
                json_object = json.loads(json_string)
            except Exception as e:
                ApplicationLogger.error(
                    'Failed to parse json for object of type "{}": {}.'
                    .format(str(motype), str(e)))

            response_data = {
                'result': 'Success',
                'method': 'update',
                'objectData': json_object,
            }

        return response_data

    def is_stale_response(self, old_response, new_response):
        return old_response == new_response


class SocketIOObjectDeleteListener(SocketIOListener):

    def __init__(self, matcher=None, socketio=None):
        """
        Initialize the SocketIOObjectDeleteListener class
        """
        super(SocketIOObjectDeleteListener, self).__init__(matcher, socketio, 'delete_object', '/object')

    def gen_response(self, em):
        response_data = None

        response_data = {
            'result' : 'Success',
            'method' : 'delete',
            'objectData' : {
                'objectType': em.getField("MN"),
                'objectID' : em.getField("ID")
            }
        }

        return response_data

    def is_stale_response(self, old_response, new_response):
        return old_response == new_response


class SocketIONotifyExternalChangeListener(SocketIOListener):

    def __init__(self, matcher = None, socketio = None):
        """
        Initialize the SocketIONotifyExternalChangeListener class
        """
        super(SocketIONotifyExternalChangeListener, self).__init__(matcher, socketio, 'notify_external_change', '/object')

    def gen_response(self, em):
        response_data = None

        response_data = {
            'result' : 'Success',
            'method' : 'notify_external_change',
            'objectData' : {
                'objectType': em.getField("MN")
            }
        }

        return response_data

    def is_stale_response(self, old_response, new_response):
        return old_response == new_response
