import pytest
import io

from http_parser.http import HttpStream


def test_continuation_header():
    stream = io.BytesIO(b'GET /test HTTP/1.1\r\nX-Test: foo\r\n bar\r\n\r\n')
    hdr = HttpStream(stream).headers()
    assert hdr['X-Test'] == 'foo bar'

def test_repeated_header():
    stream = io.BytesIO(b'GET /test HTTP/1.1\r\nX-Test: foo\r\nX-Test: bar\r\n\r\n')
    hdr = HttpStream(stream).headers()
    assert hdr['X-Test'] == 'foo, bar'

def test_repeated_continuation_header():
    stream = io.BytesIO(b'GET /test HTTP/1.1\r\nX-Test: foo\r\n bar\r\nX-Test: baz\r\n qux\r\n\r\n')
    hdr = HttpStream(stream).headers()
    assert hdr['X-Test'] == 'foo bar, baz qux'


