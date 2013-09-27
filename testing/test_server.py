import pytest
import io

from http_parser.http import HttpStream
from http_parser.parser import HttpParser
from http_parser.pyparser import HttpParser as PyHttpParser

def _test_no_headers(parser):
    assert not parser.is_headers_complete()
    data = b'GET /forum/bla?page=1#post1 HTTP/1.1\r\n\r\n'
    assert parser.execute(data, len(data)), len(data)
    assert parser.get_fragment(), 'post1'
    assert parser.is_message_begin()
    assert parser.is_headers_complete()
    assert parser.is_message_complete()
    assert not parser.get_headers()

def test_server_no_headers():
    _test_no_headers(HttpParser())

def test_server_no_headers_py():
    _test_no_headers(PyHttpParser())
