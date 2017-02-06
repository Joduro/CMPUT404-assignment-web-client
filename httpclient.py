#!/usr/bin/env python
# coding: utf-8
# Copyright 2017 https://github.com/Joduro, Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
#from urlparse import urlparse
# you may use urllib to encode data appropriately
import urllib
from urlparse import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):
    def __init__(self):
        self.path = None
        self.host = None
        self.port = 80
        self.query = None

    def parse_url(self, url):
        #print("Parsing Url", url)

        parsed = urlparse(url)
    	self.host = parsed.hostname
        self.port = parsed.port
        self.path = parsed.path
        self.query = parsed.query

        #if (self.path == ""): self.path = '/'

        url = url.strip("http://")

        if ('/' not in self.path): self.path = '/'

        if (self.host == None or self.host == ""): self.host = url.split(':')[0]#.strip("http://").strip("www.")

        if ((self.port == None) and (':' in url) and ('/' in url)): 
            self.port = int(url.split(':')[1].split("/")[0])
        elif ((self.port == None) and (':' in url)):
            self.port = int(url.split(':')[1])

        if (self.port == None): self.port = 80

        return

    def connect(self, host, port):
        # use sockets!
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((self.host, self.port))

        if(clientSocket == None):
            print ("CONNECTION FAILED")
        return clientSocket

    def get_code(self, data):
        return int(data.split("\r\n")[0].split(' ')[1])

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        code = 500
        body = ""

        self.parse_url(url)
        """
        print ("getting", url)
        print ("host is:", self.host)
        print ("port is:", self.port)
        print ("path is:", self.path)
        """
        try:

            cs = self.connect(self.host, self.port)

            cs.send("GET " + self.path + " HTTP/1.1\r\n")
            cs.send("HOST: " + self.host + "\r\n")
            cs.sendall("Accept: */*\r\n\r\n")

            data = self.recvall(cs)

            print(data)

            code = self.get_code(data)
            body = self.get_body(data)

            #print("code:", code, "\n body: " + body)
        except Exception, e:
            print("A GET Error has occured: ", e)
            code = 500


        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        self.parse_url(url)
        """
        print("Posting to", url)
        print ("host is:", self.host)
        print ("port is:", self.port)
        print ("path is:", self.path)
        print ("query is:", self.query)
        print ("args are:", args)
        """

        try:
            cs = self.connect(self.host, self.port)

            cs.send("POST " + self.path + " HTTP/1.1\r\n")
            cs.send("HOST: " + self.host + "\r\n")
            cs.send("Accept: */*\r\n")

            if (args != None):
                encoded = urllib.urlencode(args)

                cs.send("Content-Length: ")
                cs.send(str(len(encoded)))
                cs.send("\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n")
                cs.send(str(encoded))
            else:
                cs.send("Content-Length: 0\r\n\r\n")
            cs.send("\r\n\r\n")

            data = self.recvall(cs)

            print(data)

            code = self.get_code(data)
            body = self.get_body(data)
        except Exception, e:
            print("An Error has occured: ", e)
            code = 500

        #print("code:", code, "\n body: " + body)

 
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )   
