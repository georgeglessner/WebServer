#!/usr/bin/env python

'''Usage: server.py [-p PORT] [-d DIRECTORY] [-l FILE]

-h --help               show this
-p --port PORT          specify port [default: 8080]
-d --docroot DIRECTORY  specify directory of files [default: .]
-l --logfile file       specify file for logs to printed to [default: standard output]

'''

from docopt import docopt
from wsgiref.handlers import format_date_time
from time import mktime
import socket
import select
import Queue
import os
import datetime
import time


def log_input(status_code, filePath):

    status_codes = {200:'OK', 404:'Not Found', 501:'Not Implemented'}
    log = ""

    #TODO: still have some hard coded values
    if status_code in (404,501):
        status = 'HTTP/1.1 %i %s' % (status_code, status_codes.get(status_code))
        now = datetime.datetime.now()
        date = str(format_date_time(mktime(now.timetuple())))
        server = 'Apache/2.2.14'
        contentLength = str(os.path.getsize(filePath))
        contentType = 'text/html'
        connectionType = 'closed'

        # log reponse
        log += status + '\n'
        log += 'Date: ' + date + '\n'
        log += 'Server: ' + server + '\n'
        log += 'Content-Length: ' + contentLength + '\n'
        log += 'Content-Type: ' + contentType + '\n'
        log += 'Connection: ' + connectionType + '\n' 

    else:
        status = 'HTTP/1.1 %i %s' % (status_code, status_codes.get(status_code))
        now = datetime.datetime.now()
        date = str(format_date_time(mktime(now.timetuple())))
        server = 'Apache/2.2.14'
        lastModified = str(time.ctime(os.path.getmtime(filePath)))
        contentLength = str(os.path.getsize(filePath))
        contentType = 'text/html'
        connectionType = 'closed'

        # log response
        log += status + '\n'
        log += 'Date: ' + date + '\n'
        log += 'Server: ' + server + '\n'
        log += 'Last-Modified: ' + lastModified + '\n'
        log += 'Content-Length: ' + contentLength + '\n'
        log += 'Content-Type: ' + contentType + '\n'
        log += 'Connection: ' + connectionType + '\n'    

    return log

def create_response(log, status_code, filePath):

    # print error page
    if status_code == 404:
        with open ('404.html', "r") as myfile:
                    data=myfile.read()
    # send page contents
    else:
        with open (filePath, "r") as myfile:
                    data=myfile.read()
    
    # format response
    response = log + '\r\n' + data

    return response

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
    status_code = 0

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
                    if log_file:
                        log_file.write('\n---REQUEST---\n')
                        log_file.write(request)
                    else:
                        print '\n---REQUEST---\n'
                        print request
                    # Get requested filename
                    if 'GET' not in request:
                        status_code = 501
                    else:
                        request = request.split('GET')
                        request = request[1]
                        request = request.split('HTTP')
                        request = request[0].strip()

                    filePath = docroot + request

                    # file doesn't exist in current directory 
                    if not os.path.exists(filePath):
                        status_code = 404
                        filePath = './404.html'
                        log = log_input(status_code, filePath)
                        response = create_response(log, status_code, filePath)
                       
                        if log_file:
                            log_file.write('\n---RESPONSE---\n')
                            log_file.write(log)
                            response_queue[s].put(response)
                            outputs.append(s)
                        else:
                            response_queue[s].put(response)
                            outputs.append(s)
                            print '---RESPONSE---'
                            print log
                    else:
                        status_code = 200
                        log = log_input(status_code, filePath)
                        response = create_response(log, status_code, filePath)

                        if log_file:
                            log_file.write('\n---RESPONSE---\n')
                            log_file.write(log) 
                            response_queue[s].put(response)
                            outputs.append(s)
                        else:
                            response_queue[s].put(response)
                            outputs.append(s)
                            print '---RESPONSE---'
                            print log
        for s in writable:
            try:
                next_msg = response_queue[s].get_nowait()
            except Queue.Empty:
                outputs.remove(s)
            else:
                s.send(next_msg)


if __name__ == '__main__':
    arguments = docopt(__doc__)
    main()
