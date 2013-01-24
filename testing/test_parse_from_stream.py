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
            if isinstance(event, type(b'')):
                return event
            elif isinstance(event, int):
                raise socket.error(event, os.strerror(event))
            else:
                assert 0
    
    def recv_into(self, buf):
        data = self.recv()
        l = len(data)
        assert l <= len(buf)
        buf[0:l] = data
        return l




inputs = {
    '01_complete': [
        b'GET /test HTTP/1.1\r\nContent-Type: text\r\n\r\n',
    ],

    '02_eagain_before_headers': [
        b'GET /test HTTP/1.1\r\n', 
        EAGAIN,
        b'Content-Type: text\r\n\r\n',
    ],


}


@pytest.mark.parametrize('input', sorted(inputs))
def test_parse_headers(input):
    sock = FakeInputSocket(inputs[input])
    reader = SocketReader(sock)
    stream = HttpStream(reader)
    assert stream.headers()


