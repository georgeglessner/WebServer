#!/usr/bin/env python

'''Usage: server.py [-p PORT] [-d DIRECTORY] [-l FILE]

-h --help               show this
-p --port PORT          specify port [default: 8080]
-d --docroot DIRECTORY  specify directory of files [default: ./]
-l --logfile file       specify file for logs to printed to [default: standard output]

'''

from docopt import docopt
import socket

def main():

    # get values of arguments
    docroot = arguments.get('--docroot')
    port = int(arguments.get('--port'))
    log_file = arguments.get('--logfile')

    # create log file if one specified
    if log_file == 'standard output':
        log_file = False
    else:
        with open(log_file, 'w') as log_file:
            log_file.write('test' + '\n')

    # create server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server.bind(('localhost', port))
    server.listen(5)

if __name__ == '__main__':
    arguments = docopt(__doc__)
    main()
