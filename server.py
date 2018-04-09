#!/usr/bin/env python

'''Usage: server.py [-p PORT] [-d DIRECTORY] [-l FILE]

-h --help               show this
-p --port PORT          specify port [default: 8080]
-d --docroot DIRECTORY  specify directory of files [default: .]
-l --logfile file       specify file for logs to printed to [default: standard output]

'''

from docopt import docopt
import socket
import select
import Queue
import os
import datetime
import time

def main():

    # get values of arguments
    docroot = arguments.get('--docroot')
    port = int(arguments.get('--port'))
    log_file = arguments.get('--logfile')

    # create log file if one specified
    if log_file == 'standard output':
        log_file = False
    else:
        log_file = open(log_file, 'w')

    # create server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', port))
    server.listen(1)
    inputs = [server]
    outputs = []
    response_queue = {}         
    request = ''

    while inputs:
        readable, writable, exceptional = select.select(
            inputs, outputs, inputs)
        for s in readable:
            # create new connection
            if s is server:
                client_connection, client_address = s.accept()
                client_connection.setblocking(0)
                inputs.append(client_connection)
                response_queue[client_connection] = Queue.Queue()
            # receive HTTP request
            else:
                request = s.recv(1024)
                if request:
                    # Get requested filename
                    request = request.split('GET')
                    request = request[1]
                    request = request.split('HTTP')
                    request = request[0].strip()

                    filePath = docroot + request
                    if not os.path.exists(filePath):
                        print 'File does not exist'
                        #TODO: send error responsh
                    else:
                        print 'File exists!'
                        #TODO: remove hard-code, format dates, server?
                        status = 'HTTP/1.1 200 OK'
                        date = datetime.datetime.utcnow()
                        server = 'Apache/2.2.14'
                        lastModified = time.ctime(os.path.getmtime(filePath))
                        contentLength = os.path.getsize(filePath)
                        contentType = 'text/html'
                        connectionType = 'closed'

                    # test print out
                    print request
                    print status
                    print date
                    print server
                    print lastModified
                    print contentLength
                    print contentType
                    print connectionType


if __name__ == '__main__':
    arguments = docopt(__doc__)
    main()
