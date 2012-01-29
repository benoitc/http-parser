# -*- coding: utf-8 -
#
# This file is part of http-parser released under the MIT license.

# See the NOTICE for more information.

from errno import EINTR, EAGAIN, EWOULDBLOCK
import socket
import sys
import types
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from io import DEFAULT_BUFFER_SIZE, RawIOBase
except ImportError:
    from http_parser.py25 import DEFAULT_BUFFER_SIZE, RawIOBase

try:
    bytes
    bytearray
except (NameError, AttributeError):
    # python < 2.6
    from py25 import bytes, bytearray


_blocking_errnos = ( EAGAIN, EWOULDBLOCK )

if sys.version_info < (2, 7, 0, 'final'):
    # in python 2.6 socket.recv_into doesn't support bytesarray
    import array
    def _readinto(sock, b):
        l = max(len(b), DEFAULT_BUFFER_SIZE)
        while True:
            try:
                buf = sock.recv(l)
                recved = len(buf)
                b[0:recved] = buf
                return recved
            except socket.error, e:
                n = e.args[0]
                if n == EINTR:
                    continue
                if n in _blocking_errnos:
                    return None
                raise
else:
    _readinto = None

class HttpBodyReader(RawIOBase):
    """ Raw implementation to stream http body """

    def __init__(self, http_stream):
        self.http_stream = http_stream
        self.eof = False

    def readinto(self, b):
        if self.http_stream.parser.is_message_complete() or self.eof:
            if  self.http_stream.parser.is_partial_body():
                return self.http_stream.parser.recv_body_into(b)
            return 0

        self._checkReadable()
        try:
            self._checkClosed()
        except AttributeError:
            pass

        while True:
            buf = bytearray(DEFAULT_BUFFER_SIZE)
            recved = self.http_stream.stream.readinto(buf)
            if recved is None:
                break

            del buf[recved:]
            nparsed = self.http_stream.parser.execute(bytes(buf), recved)
            if nparsed != recved:
                return None

            if self.http_stream.parser.is_partial_body() or recved == 0:
                break
            elif self.http_stream.parser.is_message_complete():
                break

        if not self.http_stream.parser.is_partial_body():
            self.eof = True
            b = bytes('')
            return len(b)

        return self.http_stream.parser.recv_body_into(b)

    def readable(self):
        return not self.closed or self.http_stream.parser.is_partial_body()

    def close(self):
        if self.closed:
            return
        RawIOBase.close(self)
        self.http_stream = None

class IterReader(RawIOBase):
    """ A raw reader implementation for iterable """
    def __init__(self, iterable):
        self.iter = iter(iterable)
        self._buffer = ""

    def readinto(self, b):
        self._checkClosed()
        self._checkReadable()

        l = len(b)
        try:
            chunk = self.iter.next()
            self._buffer += chunk
            m = min(len(self._buffer), l)
            data, self._buffer = self._buffer[:m], self._buffer[m:]
            b[0:m] = data
            return len(data)
        except StopIteration:
            del b[0:]
            return 0

    def readable(self):
        return not self.closed

    def close(self):
        if self.closed:
            return
        RawIOBase.close(self)
        self.iter = None

class StringReader(IterReader):
    """ a raw reader for strings or StringIO.StringIO,
    cStringIO.StringIO objects """

    def __init__(self, string):
        if isinstance(string, types.StringTypes):
            iterable = StringIO(string)
        else:
            iterable = string
        IterReader.__init__(self, iterable)




class SocketReader(RawIOBase):
    """ a raw reader for sockets or socket like interface. based
    on SocketIO object from python3.2 """

    def __init__(self, sock):
        RawIOBase.__init__(self)
        self._sock = sock

    if _readinto is not None:
        def readinto(self, b):
            try:
                self._checkClosed()
            except AttributeError:
                pass
            self._checkReadable()
            return _readinto(self._sock, b)

    else:
        def readinto(self, b):
            try:
                self._checkClosed()
            except AttributeError:
                pass
            self._checkReadable()

            while True:
                try:
                    return self._sock.recv_into(b)
                except socket.error, e:
                    n = e.args[0]
                    if n == EINTR:
                        continue
                    if n in _blocking_errnos:
                        return None
                    raise

    def readable(self):
        """True if the SocketIO is open for reading.
        """
        return not self.closed

    def fileno(self):
        """Return the file descriptor of the underlying socket.
        """
        self._checkClosed()
        return self._sock.fileno()

    def close(self):
        """Close the SocketIO object. This doesn't close the underlying
        socket, except if all references to it have disappeared.
        """
        if self.closed:
            return
        RawIOBase.close(self)
        self._sock = None
