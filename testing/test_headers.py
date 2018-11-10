import pytest
import io

from http_parser.http import HttpStream
from http_parser.pyparser import HttpParser as PyHttpParser

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

def test_upgrade_header():
    stream = io.BytesIO(b'GET /test HTTP/1.1\r\nConnection: keep-alive, upgrade\r\nUpgrade: websocket\r\nSec-WebSocket-Key: hojIvDoHedBucveephosh8==\r\nSec-WebSocket-Version: 13\r\n\r\n')
    hdr = HttpStream(stream)
    hdr.headers()
    assert hdr.parser.is_upgrade() == 1

    stream = io.BytesIO(b'GET /test HTTP/1.1\r\nConnection: upgrade\r\nUpgrade: websocket\r\nSec-WebSocket-Key: hojIvDoHedBucveephosh8==\r\nSec-WebSocket-Version: 13\r\n\r\n')
    hdr = HttpStream(stream)
    hdr.headers()
    assert hdr.parser.is_upgrade() == 1

    stream = io.BytesIO(b'GET /test HTTP/1.1\r\nConnection: shenanigans\r\n\r\n')
    hdr = HttpStream(stream)
    hdr.headers()
    assert hdr.parser.is_upgrade() == 0

def test_continuation_header_py():
    stream = io.BytesIO(b'GET /test HTTP/1.1\r\nX-Test: foo\r\n bar\r\n\r\n')
    hdr = HttpStream(stream, parser_class=PyHttpParser).headers()
    assert hdr['X-Test'] == 'foo bar'

def test_repeated_header_py():
    stream = io.BytesIO(b'GET /test HTTP/1.1\r\nX-Test: foo\r\nX-Test: bar\r\n\r\n')
    hdr = HttpStream(stream, parser_class=PyHttpParser).headers()
    assert hdr['X-Test'] == 'foo, bar'

def test_repeated_continuation_header_py():
    stream = io.BytesIO(b'GET /test HTTP/1.1\r\nX-Test: foo\r\n bar\r\nX-Test: baz\r\n qux\r\n\r\n')
    hdr = HttpStream(stream, parser_class=PyHttpParser).headers()
    assert hdr['X-Test'] == 'foo bar, baz qux'


