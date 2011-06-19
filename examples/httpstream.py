#!/usr/bin/env python
import socket

from http_parser.http import HttpStream
from http_parser.reader import SocketReader

from http_parser.util import b

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('gunicorn.org', 80))
        s.send(b("GET / HTTP/1.1\r\nHost: gunicorn.org\r\n\r\n"))
        p = HttpStream(SocketReader(s))
        print(p.headers())

        print(p.body_file().read())
    finally:
        s.close()

if __name__ == "__main__":
    main()


