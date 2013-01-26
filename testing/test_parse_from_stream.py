from errno import EINTR, EAGAIN, EWOULDBLOCK

import os
import socket

import pytest
from http_parser.http import HttpStream
from http_parser.reader import SocketReader

class FakeInputSocket(object):
    def __init__(self, events):
        self.events = events

    def recv(self, *ignored):
        try:
            event = self.events.pop(0)
        except IndexError:
            return b''
        else:
            if isinstance(event, Exception):
                raise event
            else:
                return event

    def recv_into(self, buf):
        data = self.recv()
        l = len(data)
        assert l <= len(buf)
        buf[0:l] = data
        return l


complete_request = b'GET /test HTTP/1.1\r\nContent-Type: text\r\n\r\n'

inputs = {
    '01_complete': [
        complete_request
    ],

    '02_eagain_before_headers': [
        b'GET /test HTTP/1.1\r\n',
        socket.error(EAGAIN, 'eagain'),
        b'Content-Type: text\r\n\r\n',
    ],


}


@pytest.mark.parametrize('input', sorted(inputs))
def test_parse_headers(input):
    sock = FakeInputSocket(inputs[input])
    reader = SocketReader(sock)
    stream = HttpStream(reader)
    assert stream.headers()


def test_parse_with_timeout_raises():
    sock = FakeInputSocket([
        b'GET /test HTTP/1.1\r\n',
        socket.timeout(EAGAIN, 'timeout'),
        b'Content-Type: text\r\n\r\n',
    ])
    reader = SocketReader(sock)
    stream = HttpStream(reader)
    ex = pytest.raises(socket.timeout, stream.headers)
    print(ex.getrepr(style='short'))


def test_parse_from_real_socket():
    sock, sink = socket.socketpair()
    sink.send(complete_request)
    reader = SocketReader(sock)
    stream = HttpStream(reader)
    assert stream.headers()
