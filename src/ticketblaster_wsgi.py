#!/usr/bin/env python
#
#
# The ticket blaster WSGI server
from wsgiref.simple_server import make_server
from urlparse import parse_qs
import ticketdb

html = """
<html>
<body>
T I C K E T B L A S T E R
<form method="get" action="">
<p><input type="text" name="ticket"> <input type="submit" value="Add"></p>
</form>

<p>
<b>Tickets</b>
%(tickets)s
</p>

</body>
</html>"""


# The WSGI application
def application(environ, start_response):
    # Get all inputs
    d = parse_qs(environ['QUERY_STRING'], keep_blank_values=1)
    newticket = d.get("ticket")
    # Add a new ticket
    print "Ticket: %s" % newticket
    if newticket != None and isinstance(newticket, list):
        print "Added new ticket"
        ticketdb.add(newticket[0])

    # List old tickets
    oldtickets = ""
    for t in ticketdb.getall():
        oldtickets += "<li>"+t[1]+"</li>"
    print "Old tickets: "+oldtickets
    print type(oldtickets)
    # Create web interface
    response_body = html % {"tickets": str(oldtickets)}
    status = '200 OK'
    response_headers = [('Content-Type', 'text/html'),
                        ('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)
    return [response_body]

def server():
    # WSGI server, passes request to application
    httpd = make_server(
        'localhost', # Hostname
        8051,        # Port
        application  # Function to handle request
        )
    httpd.serve_forever()

# Launch the server in case a recular call is done
if __name__ == '__main__':
    server()
