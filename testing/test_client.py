import pytest
import io

from http_parser.http import HttpStream
from http_parser.parser import HttpParser
from http_parser.pyparser import HttpParser as PyHttpParser

def _test_no_headers(parser):
    data = b'HTTP/1.1 200 Connection established\r\n\r\n'
    assert parser.execute(data, len(data)) == len(data)
    assert parser.is_headers_complete()
    assert parser.is_message_begin()
    assert not parser.is_partial_body()
    assert not parser.is_message_complete()

def _test_headers(parser):
    data = (b'HTTP/1.1 200 OK\r\n'
            b'Connection: Keep-Alive\r\n'
            b'Content-Length: 4\r\n'
            b'Content-type: text/plain\r\n\r\n'
            b'ciao')
    assert parser.execute(data, len(data)) == len(data)
    assert parser.is_headers_complete()
    assert parser.is_message_begin()
    assert parser.is_partial_body()
    assert parser.is_message_complete()

def test_client_no_headers():
    _test_no_headers(HttpParser())

def test_client_no_headers_py():
    _test_no_headers(PyHttpParser())

def test_client_headers():
    _test_headers(HttpParser())

def test_client_headers_py():
    _test_headers(PyHttpParser())

