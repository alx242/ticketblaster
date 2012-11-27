#!/usr/bin/env python
#
#
# The ticket blaster WSGI server
from wsgiref.simple_server import make_server
import urlparse
import ticketdb

html = """
<html>
<head>

<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js" type="text/javascript" charset="utf-8"></script>
<script src="http://www.appelsiini.net/download/jquery.jeditable.mini.js" type="text/javascript" charset="utf-8"></script>
<script type="text/javascript" charset="utf-8">
 $(document).ready(function() {
     $('.new').editable('/new', {
         style:  'inherit',
         method: 'POST'
     });
     $('.edit').editable('/edit', {
         style:  'inherit',
         method: 'POST'
     });
 });
</script>
</head>

<body>

T I C K E T B L A S T E R

<form method="POST" action="/new">
<p><input type="text" name="ticket"><input type="submit" value="Add"></p>
</form>

<p>
<b>Tickets</b>
%(tickets)s
</p>

</body>
</html>"""

import urllib

# The WSGI application
def application(env, start_response):
    body= ''  # b'' for consistency on Python 3.0
    try:
        length=int(env.get('CONTENT_LENGTH', '0'))
    except ValueError:
        length= 0
    if length!=0:
        body=env['wsgi.input'].read(length)

    # Add a new tickets
    if env['PATH_INFO'] == '/new':
        # ticketdb.add(body[0])
        print(body)

    # List old tickets
    oldtickets = ""
    for t in ticketdb.getall():
        oldtickets += ("<li>"
                       "<div class='edit' id='desc_"+str(t[0])+"'>"+t[1]+"</div>"
                       "<div class='edit' id='owner_"+str(t[0])+"'>"+t[1]+"</div>"
                       "</li>")

    if env['PATH_INFO'] == '/edit':
        response_body ="BABA"
    else:
        # Create main web interface
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
    print "TICKETBLASTER - WSGI> Server launched and ready to serve"
    httpd.serve_forever()

# Launch the server in case a recular call is done
if __name__ == '__main__':
    server()
