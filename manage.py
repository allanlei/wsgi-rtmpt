#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

from flask import current_app
from flask.ext import script
try:
    from termcolor import cprint
    import functools
    print = functools.partial(cprint, color='green')
except ImportError:
    pass
from rtmpt.wsgi import get_application


class Shell(script.Shell):
    def get_context(self):
        context = super(Shell, self).get_context()

        context.update({'current_app': current_app})
        print('from flask import current_app')
        return context


if __name__ == '__main__':
    application = get_application()
    manager = script.Manager(application)
    manager.add_command('shell', Shell())
    manager.add_command('runserver', script.Server(host='0.0.0.0', port=8000))
    manager.run()
