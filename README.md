# WebServer


## Invocation

Your server should accept the following command line arguments:

- `-p [port]`: Specify the port the server should run on. If no port is specified, the default should be 8080 (because without root access, we can not use the standard port 80).  
- `-docroot [directory]`: Specify the directory from which the server should look for requested files. The default should be the directory the server was run from.  
- `-logfile [file]`: Specify a file for log messages to be written out to. If no log file is specified, then log messages should only be printed on standard out.

## Behavior:

Your server must do the following:

- Your server must support multiple simultaneous clients or multiple connections from the same client.
- You only need to support the GET operation, other operations such as POST do not need to be supported. You must return the appropriate status code (501) in response to such requests to indicate this.
- You must send the date header.
- You must send the last-modified header.
- You must send a content-type header, but you only need to support the types for html, plain text, jpeg images, and pdf files. You may of course support others.
- You must send a header indicating the length of the content you are sending.
- You must return page contents and a 200 status code if the client requests a vaild document.
- You must return a 404 status code if the client requests and invalid document. Note that a 404 response has a body: you must include the error page to be displayed on the client.
- You must correctly interperit any if-modified-since header sent by the client, including returning the appropriate status code (304) if the page has not been modified, and detecting if the page has been modified on disk.
- You must support persistent connections. A browser may send several requests over the same HTTP connection (even before receiving any responses). If a recieved message contains a connection: close header, the connection must be closed immediately after handling the request. Otherwise, the connection must be kept open for 20 seconds, and closed if no messages have been recieved after this amount of time.
- Unsupported headers in requests must not cause your server to fail.
- Your server must print all requests it recieves to the log file, along with the headers (only) of responses it sends. Printing to the log must be thread-safe: a message printed in the handling of one request should not occur in the middle of a message from another.
- You must prevent your server from accessing files outside of its docroot directory, as this is a security risk. 
