http-parser
-----------

HTTP request/response parser for Python in C under MIT License, based on
http-parser_ from Ryan Dahl.


Project url: https://github.com/benoitc/http-parser/

Requirements:
-------------

- Python 2.6 or sup.
- Cython if you need to rebuild the C code

Installation
------------

::

    $ pip install http-parser

Or install from source::

    $ git clone git://github.com/benoitc/http-parser.git
    $ cd http-parser && python setup.py install

Usage
-----

http-parser provide you **parser.HttpParser** low-level parser in C that
you can access in your python program and **http.HttpStream** providing
higher-level access to a readable,sequential io.RawIOBase object.

To help you in your day work, http-parser prvides you 3 kind of readers
in the reader module: IterReader to read iterables, StringReader to
reads strings and StringIO objects, SocketReader to read sockets or
objects with the same aî (recv_into needed). You cnan of course use any
io.RawIOBase object.

Example of HttpStream
+++++++++++++++++++++

ex::
    
    #!/usr/bin/env python
    import socket

    from http_parser.http import HttpStream
    from http_parser.reader import SocketReader

    def main():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(('gunicorn.org', 80))
            s.send("GET / HTTP/1.1\r\nHost: gunicorn.org\r\n\r\n")
            r = SocketReader(s)
            p = HttpStream(r)
            print p.headers()
            print p.body_file().read()
        finally:
            s.close()

    if __name__ == "__main__":
        main()

Example of HttpParser:
++++++++++++++++++++++

::
    
    #!/usr/bin/env python
    import socket

    from http_parser.parser import HttpParser


    def main():

        p = HttpParser()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        body = []
        try:
            s.connect(('gunicorn.org', 80))
            s.send("GET / HTTP/1.1\r\nHost: gunicorn.org\r\n\r\n")
            
            while True:
                data = s.recv(1024)
                if not data:
                    break

                recved = len(data)
                nparsed = p.execute(data, recved)
                assert nparsed == recved

                if p.is_headers_complete():
                    print p.get_headers()

                if p.is_partial_body():
                    body.append(p.recv_body())

                if p.is_message_complete():
                    break

            print "".join(body)
        
        finally:
            s.close()

    if __name__ == "__main__":
        main()


You can find more docs in the code (or use a doc genererator).


Copyright
---------

2011 (c) Benoît Chesneau <benoitc@e-engura.org>


.. http-parser_ https://github.com/ry/http-parser
