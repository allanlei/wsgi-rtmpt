# -*- coding: utf-8 -*- 
from __future__ import absolute_import, division, unicode_literals, print_function

from flask import Flask, Response


class RTMPTResponse(Response):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('mimetype', 'application/x-fcs')
        kwargs.setdefault('content_type', 'application/x-fcs')
        super(RTMPTResponse, self).__init__(*args, **kwargs)


def get_application():
    application = Flask('rtmpt')
    application.config.update({
        'SECRET_KEY': 'secret_key',
        'RMPT_INTERVALS': (b'\x01', b'\x03', b'\x05', b'\x09', b'\x11', b'\x21'),
        'RTMP_FAIL_RAMPUP': 10,
        'RTMP_SERVER': ('127.0.0.1', 1935),
        'RTMPT_DEFAULT_CONTENT_TYPE': 'application/x-fcs',
        'RTMP_BUFFER_SIZE': 8 * 1024,
        'RTMP_TIMEOUT': 0.020,
    })
    # application.config.from_object(
        # os.environ.get('SETTINGS_MODULE', 'rtmpt.settings').strip())

    application.response_class = RTMPTResponse

    # Installed Apps
    from .views import application as bp
    application.register_blueprint(bp, url_prefix='')
    
    return application


application = get_application()