from flask import (
    jsonify,
)

from marshmallow import (
    Schema,
    fields,
    validate,
)

from marshmallow.exceptions import ValidationError

from base.schema import ResponseSchema
from fx_view import FxView
from application_log import ApplicationLogger
import conn_exceptions
from server_login_context import ServerLoginContext

from lib.utils.data_structures import ExcryptMessage


logger = ApplicationLogger


class SmokeTestStatus(fields.String):
    def __init__(self, **kwargs):
        kwargs['validate'] = validate.OneOf([
            'Success',
            'Failure',
            'Abort',
        ])
        kwargs['example'] = 'Success'

        super(SmokeTestStatus, self).__init__(**kwargs)


class SmokeTestSchema(Schema):
    connect = SmokeTestStatus(
        attribute='connect',
        description='Attempt to make a connection to the server',
    )
    write = SmokeTestStatus(
        attribute='write',
        description='Attempt to write data to the connection to the server',
    )
    echo = SmokeTestStatus(
        attribute='echo',
        description='Send an echo to the server and wait for a response',
    )


class SystemInfoPostResponseSchema(ResponseSchema):
    smoketest = fields.Nested(
        SmokeTestSchema,
        attribute='smoketest',
        description='Basic health tests',
    )


class SmokeTest(object):
    def __init__(self, server_interface):
        super(SmokeTest, self).__init__()
        self.server_interface = server_interface
        self._context = ServerLoginContext(server_interface)
        self.context = None

    def _tryconnect(self):
        _, self.context = self._context.create_middleware_context()
        self.server_interface.connect(self.context)

    def __call__(self):
        results = {
            'echo': 'Abort',
            'connect': 'Abort',
            'write': 'Abort',
        }

        try:
            self._tryconnect()
            results['connect'] = 'Success'

        except conn_exceptions.CannotConnectException:
            results['connect'] = 'Failure'

            return results

        try:
            rsp = ExcryptMessage(self.server_interface.send('[AOECHO;]', context=self.context))
            results['write'] = 'Success'

            if rsp.getField("AO") == "ECHO":
                results['echo'] = 'Success'
            else:
                logger.error('"{command}" received as response to echo during smoketest.'.format(
                    command=rsp.getField("AO"),
                ))
                results['echo'] = 'Failure'
        except conn_exceptions.ErrorOnWriteException:
            results['write'] = 'Failure'
        except conn_exceptions.ServerConnectionTimeout:
            results['write'] = 'Success'
            results['echo'] = 'Failure'
        finally:
            self.server_interface.conn_handler.remove(self.context)
            self.context = None

        return results


class SystemInfoView(FxView):
    def __init__(self, server_interface):
        super(SystemInfoView, self).__init__(server_interface)
        self.smoketest = SmokeTest(server_interface)

    def post(self, *args, **kwargs):
        '''Queries the application server for application and system
        diagnostic information
        ---
        tags:
            - generic-rk
        responses:
            200:
                description: The system information
                schema:
                    $ref: '#/definitions/SystemInfoPostResponseSchema'
        '''

        smoketest_result = self.smoketest()
        data = {
            'smoketest': smoketest_result,
            'result': 'Success',
        }

        schema = SystemInfoPostResponseSchema()

        try:
            result = schema.dump(data)
        except ValidationError as e:
            logger.error('Serialized system information is incorrect: {error}'.format(
                error=str(e.message),
            ))

        return jsonify(result)
