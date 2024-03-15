"""
@file      run.py
@author    James Espinoza(jespinoza@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Starts middleware server
"""
from fx import Program

if __name__ == '__main__':
    program = Program()
    program.run()
else:
    uwsgiApp = Program()
    if uwsgiApp.config.getboolean('flask', 'uwsgi'):
        uwsgiApp.run()
        uwsgiApp = uwsgiApp.app
