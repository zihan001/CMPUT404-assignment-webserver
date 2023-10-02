#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Ahmed Zihan Hossain
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        request = self.data.decode('utf-8')
        request_list = request.split('\r\n')
        main_list = request_list[0].split()
        protocol = main_list[2]

        status = "200 OK"

        files_dir = "./www"
        file_path = files_dir + main_list[1]
        if "/www" in os.path.abspath(file_path):
            # if path ends as directory serve index.html of that directory
            if main_list[1][-1] == '/' and os.path.isdir(file_path):
                file_path = files_dir + main_list[1] + "index.html"
            # if final path directory but does not end with '/'
            elif len(main_list[1].rsplit('.',1)) == 1:
                status = "301 Moved Permanently"
                file_path = files_dir + main_list[1] + "/index.html"
                location = main_list[1] + "/"
            if not os.path.exists(file_path):
                status = "404 Not Found"
        else:
            status = "404 Not Found"

        if main_list[0] != "GET":
            status = "405 Method Not Allowed"

        if status == "200 OK":
            if os.path.exists(file_path):
                ctype = file_path.rsplit('.', 1)[1]
                self.request.sendall(bytearray(("%s %s\r\n")%(protocol, status),'utf-8'))
                self.request.sendall(bytearray(("Content-type: text/%s\r\n\r\n")%(ctype), 'utf-8'))
                file = open(file_path, 'r')
                content = file.read()
                self.request.sendall(bytearray(content, 'utf-8'))

        if status == "301 Moved Permanently":
            if os.path.exists(file_path):
                self.request.sendall(bytearray(("%s %s\r\n")%(protocol, status),'utf-8'))
                self.request.sendall(bytearray(("Location: http://127.0.0.1:8080%s\r\n\r\n")%(location),'utf-8'))

        if status == "404 Not Found":
            self.send4XX(protocol, status)
        
        if status == "405 Method Not Allowed":
            self.send4XX(protocol, status)
                
        #self.request.sendall(bytearray("OK",'utf-8'))

    def send4XX(self, protocol, status):
        self.request.sendall(bytearray(("%s %s\r\n")%(protocol, status),'utf-8'))
        self.request.sendall(bytearray(("Content-type: text/html\r\n"), 'utf-8'))
        if status == "404 Not Found":
            self.request.sendall(bytearray(("\r\n<!DOCTYPE html>\n<html><head><title>404 Not Found</title></head><body><p>The page you requested cannot be found :(</p></body></html>\n"), 'utf-8'))
        elif status == "405 Method Not Allowed":
            self.request.sendall(bytearray(("Allow: GET\r\n\r\n"), 'utf-8'))
            self.request.sendall(bytearray(("<!DOCTYPE html>\n<html><head><title>405 Method Not Allowed</title></head><body><p>Only GET method is allowed.</p></body></html>\n"), 'utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()