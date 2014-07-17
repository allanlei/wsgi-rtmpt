# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function

from flask import Blueprint, request, current_app, abort, session

import random
import socket
import heapq

from .utils import get_interval


application = app = Blueprint('rtmpt', __name__)

connections = {}


class RTMPConnection(object):
    SENT = 0
    PENDING = 1

    class DoesNotExist(Exception):
        pass

    class QueryManager(object):
        def create(self, id=None):
            if id is None:
                id = str(random.randint(1000000000, 9999999999))
            while True:
                id = str(random.randint(1000000000, 9999999999))
                if id not in connections:
                    connection = RTMPConnection(id=id)
                    connections[connection.id] = connection
                    connection.open()
                    return connection

        def get(self, id):
            try:
                return connections[id]
            except KeyError:
                raise RTMPConnection.DoesNotExist()

        def get_or_404(self, *args, **kwargs):
            try:
                return self.get(*args, **kwargs)
            except RTMPConnection.DoesNotExist:
                abort(404)

        def all(self):
            return connections.values()

    objects = QueryManager()

    def __init__(self, id=None):
        self.id = id
        self.addr = current_app.config['RTMP_SERVER']
        self.cursor = 0
        self.queue = []

    def open(self, timeout=None):
        if timeout is None:
            timeout = current_app.config['RTMP_TIMEOUT']
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.sock.connect(self.addr)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # make it non-block
        self.sock.settimeout(timeout)
        current_app.logger.debug('Connection opened')

    def close(self):
        self.sock.close()
        connections.pop(self.id, None)
        current_app.logger.debug('Connection closed')

    def send(self, sequence, payload):
        heapq.heappush(self.queue, (sequence, payload))

        while True:
            seq, data = heapq.heappop(self.queue)

            if seq == self.cursor:
                if data:
                    self.sock.send(data)
                self.cursor += 1
                break
            elif seq < self.cursor:
                pass
            elif seq > self.cursor:
                heapq.heappush(self.queue, (seq, data))
                return self.PENDING, None
        try:
            response = self.sock.recv(current_app.config['RTMP_BUFFER_SIZE'])
        except socket.timeout:
            return self.SENT, None
        return self.SENT, response


@app.route('/fcs/ident2', methods=['POST', 'GET'])
def ident2():
    return '', 404


@app.route('/open/1', methods=['POST'])
def open():
    try:
        connection = RTMPConnection.objects.create()
    except Exception as err:
        abort(500, 'Cannot connect to server')
    return connection.id + '\n', 200


@app.route('/idle/<session_id>/<int:sequence>', methods=['POST'], defaults={'data': lambda: None})
@app.route('/send/<session_id>/<int:sequence>', methods=['POST'], defaults={'data': lambda: request.data})
def send(session_id, sequence, data):
    connection = RTMPConnection.objects.get_or_404(id=session_id)

    try:
        rc, rv = connection.send(sequence, data())
    except Exception as err:
        current_app.logger.error(err)
        failed = int(session.get('failed', 0)) + 1
        session['failed'] = failed
        interval = get_interval(failed)
        return interval + '', 500
    else:
        failed = 0
        session['failed'] = failed
        interval = get_interval(failed)

        if rc == RTMPConnection.PENDING:
            return interval + '', 200
    return interval + (rv or ''), 200


@app.route('/close/<session_id>/<int:sequence>', methods=['POST'])
def close(session_id, sequence):
    connection = RTMPConnection.objects.get_or_404(id=session_id)
    connection.close()
    return b'\x00', 200
