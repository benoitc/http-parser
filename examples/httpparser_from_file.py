#coding=utf-8
'''
Created on 2012-3-24

@author: fengclient
'''
from http_parser.pyparser import HttpParser

if __name__ == '__main__':
    rsp = open('d:\\172_response.txt').read()
    # if your are reading a text file from windows, u may need manually convert \n to \r\n
    # universal newline support: http://docs.python.org/library/functions.html#open
    rsp = rsp.replace('\n', '\r\n')
    p = HttpParser()
    p.execute(rsp, len(rsp))
    print(p.get_headers())
