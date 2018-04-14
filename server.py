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
import signal

def sigint_handler(signum, frame):
    print '\nQuitting...'
    sys.exit(1)

signal.signal(signal.SIGINT, sigint_handler)


def log_input(status_code, file_path, connection, content_type):

    content_types = {'pdf':'application/pdf', 'txt':'text/html', 'jpeg':'image/jpeg', 'jpg':'image/jpeg', 'gif':'image/gif', 'css':'text/css'}
    status_codes = {200:'OK', 404:'Not Found', 501:'Not Implemented'}
    log = ""

    # determine file extension
    extension = file_path.split('.')
    extension = extension[2]

    # cross-browser compatability
    if extension in ('pdf', 'txt', 'jpeg', 'jpg', 'gif', 'css'):
        content_type = content_types.get(extension)
    
    # error codes
    if status_code in (404,501):
        # format response
        status = 'HTTP/1.1 %i %s' % (status_code, status_codes.get(status_code))
        now = datetime.datetime.now()
        date = str(format_date_time(mktime(now.timetuple())))
        content_length = str(os.path.getsize(file_path))
        connection_type = connection

        # log response
        log += status + '\n'
        log += 'Date: ' + date + '\n'
        log += 'Content-Length: ' + content_length + '\n'
        log += 'Content-Type: ' + content_type + '\n'
        log += 'Connection: ' + connection_type + '\n' 

    else:
        # format response
        status = 'HTTP/1.1 %i %s' % (status_code, status_codes.get(status_code))
        now = datetime.datetime.now()
        date = str(format_date_time(mktime(now.timetuple())))
        last_modified = str(time.ctime(os.path.getmtime(file_path)))
        content_length = str(os.path.getsize(file_path))
        connection_type = connection

        # log response
        log += status + '\n'
        log += 'Date: ' + date + '\n'
        log += 'Last-Modified: ' + last_modified + '\n'
        log += 'Content-Length: ' + content_length + '\n'
        log += 'Content-Type: ' + content_type + '\n'
        log += 'Connection: ' + connection_type + '\n'    

    return log

def create_response(log, status_code, file_path):

    # file not found
    if status_code == 404:
        with open ('./404.html', "r") as myfile:
            data=myfile.read()
    # not implemented
    if status_code == 501:
        with open ('./501.html', "r") as myfile:
            data=myfile.read()
    # send page contents
    else:
        with open (file_path, "r") as myfile:
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
    
     = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                    # get connection type
                    connection = request.split("Connection: ")
                    connection = connection[1].split('\n')
                    connection = connection[0]

                    # get content type
                    content_type = request.split('Accept: ')
                    content_type = content_type[1].split('\n')
                    content_type = content_type[0]

                    if log_file:
                        log_file.write('\n---REQUEST---\n')
                        log_file.write(request)
                    else:
                        print '\n---REQUEST---\n'
                        print request

                    # unsupported request
                    if 'GET' not in request:
                        status_code = 501
                        file_path = './501.html'
                        connection = 'keep-alive'
                        log = log_input(status_code, file_path, connection, content_type)
                        response = create_response(log, status_code, file_path)

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
                    # GET request
                    else:
                        # get requested file 
                        file = request.split('GET')
                        file = file[1]
                        file = file.split('HTTP')
                        file = file[0].strip()

                        print docroot, file
                        # create file path
                        file_path = docroot + file

                        # file doesn't exist in current directory 
                        if not os.path.exists(file_path):
                            status_code = 404
                            file_path = './404.html'
                            log = log_input(status_code, file_path, connection, content_type)
                            response = create_response(log, status_code, file_path)
                           
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
                        # file exists
                        elif os.path.exists(file_path):
                            status_code = 200
                            log = log_input(status_code, file_path, connection, content_type)
                            response = create_response(log, status_code, file_path)

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

        for s in exceptional:
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()
            del response_queue[s]


if __name__ == '__main__':
    arguments = docopt(__doc__)
    main()
