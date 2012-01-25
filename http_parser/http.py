# -*- coding: utf-8 -
#
# This file is part of http-parser released under the MIT license.
# See the NOTICE for more information.

try:
    from io import DEFAULT_BUFFER_SIZE, BufferedReader, TextIOWrapper
except ImportError:
    from py25 import DEFAULT_BUFFER_SIZE, BufferedReader, TextIOWrapper


try:
    bytes
    bytearray
except (NameError, AttributeError):
    # python < 2.6
    from py25 import bytes, bytearray

try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser

from http_parser.reader import HttpBodyReader
from http_parser.util import status_reasons

HTTP_BOTH = 2
HTTP_RESPONSE = 1
HTTP_REQUEST = 0

class NoMoreData(Exception):
    """ exception raised when trying to parse headers but
    we didn't get all data needed.
    """

class ParserError(Exception):
    """ error while parsing http request """

class HttpStream(object):
    """ An HTTP parser providing higher-level access to a readable,
    sequential io.RawIOBase object. You can use implementions of
    http_parser.reader (IterReader, StringReader, SocketReader) or
    create your own.
    """

    def __init__(self, stream, kind=HTTP_BOTH, decompress=False):
        """ constructor of HttpStream.

        :attr stream: an io.RawIOBase object
        :attr kind: Int,  could be 0 to parseonly requests,
        1 to parse only responses or 2 if we want to let
        the parser detect the type.
        """
        self.parser = HttpParser(kind=kind, decompress=decompress)
        self.stream = stream

    def _check_headers_complete(self):
        if self.parser.is_headers_complete():
            return

        while True:
            try:
                data = self.next()
            except StopIteration:
                if self.parser.is_headers_complete():
                    return
                raise NoMoreData()

            if self.parser.is_headers_complete():
                return

    def url(self):
        """ get full url of the request """
        self._check_headers_complete()
        return self.parser.get_url()

    def path(self):
        """ get path of the request (url without query string and
        fragment """
        self._check_headers_complete()
        return self.parser.get_path()

    def query_string(self):
        """ get query string of the url """
        self._check_headers_complete()
        return self.parser.get_query_string()

    def fragment(self):
        """ get fragment of the url """
        self._check_headers_complete()
        return self.parser.get_fragment()

    def version(self):
        self._check_headers_complete()
        return self.parser.get_version()

    def status_code(self):
        """ get status code of a response as integer """
        self._check_headers_complete()
        return self.parser.get_status_code()

    def status(self):
        """ return complete status with reason """
        status_code = self.status_code()
        reason = status_reasons.get(int(status_code), 'unknown')
        return "%s %s" % (status_code, reason)


    def method(self):
        """ get HTTP method as string"""
        self._check_headers_complete()
        return self.parser.get_method()

    def headers(self):
        """ get request/response headers, headers are returned in a
        OrderedDict that allows you to get value using insensitive
        keys."""
        self._check_headers_complete()
        return self.parser.get_headers()

    def should_keep_alive(self):
        """ return True if the connection should be kept alive
        """
        self._check_headers_complete()
        return self.parser.should_keep_alive()

    def is_chunked(self):
        """ return True if Transfer-Encoding header value is chunked"""
        self._check_headers_complete()
        return self.parser.is_chunked()

    def wsgi_environ(self, initial=None):
        """ get WSGI environ based on the current request.

        :attr initial: dict, initial values to fill in environ.
        """
        self._check_headers_complete()
        return self.parser.get_wsgi_environ()

    def body_file(self, buffering=None, binary=True, encoding=None,
            errors=None, newline=None):
        """ return the body as a buffered stream object. If binary is
        true an io.BufferedReader will be returned, else an
        io.TextIOWrapper.
        """
        self._check_headers_complete()

        if buffering is None:
            buffering = -1
        if buffering < 0:
            buffering = DEFAULT_BUFFER_SIZE

        raw = HttpBodyReader(self)
        buffer = BufferedReader(raw, buffering)
        if binary:
            return buffer
        text = TextIOWrapper(buffer, encoding, errors, newline)
        return text

    def body_string(self, binary=True, encoding=None, errors=None,
            newline=None):
        """ return body as string """
        return self.body_file(binary=binary, encoding=encoding,
                newline=newline).read()

    def __iter__(self):
        return self

    def next(self):
        if self.parser.is_message_complete():
            raise StopIteration

        # fetch data
        b = bytearray(DEFAULT_BUFFER_SIZE)
        recved = self.stream.readinto(b)
        if recved is None:
            raise NoMoreData("no more data")

        del b[recved:]

        # parse data
        nparsed = self.parser.execute(bytes(b), recved)
        if nparsed != recved and not self.parser.is_message_complete():
            raise ParserError("nparsed != recved")

        if recved == 0:
            raise StopIteration

        return bytes(b)
