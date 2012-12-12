#!/usr/bin/env python
#
#
# The ticket blaster WSGI server
from wsgiref.simple_server import make_server
import urlparse
import cgi
import db
import urllib

unfinished = "Not finished"
finished   = "Done"
done_snowflake = {unfinished: 0,
                  finished:   1,
                  0:          unfinished,
                  1:          finished}

html = """
<html>
<head>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js" type="text/javascript" charset="utf-8"></script>
<script src="http://www.appelsiini.net/download/jquery.jeditable.mini.js" type="text/javascript" charset="utf-8"></script>
<script type="text/javascript" charset="utf-8">
 $(document).ready(function() {
     $('.edit').editable('/edit', {
         style:  "inherit",
         method: "POST"
     });
     $('.done').editable('/edit', {
         type:   "select",
         style:  "inherit",
         data:   "{'%(finished)s':'%(finished)s','%(unfinished)s':'%(unfinished)s'}",
         submit: "OK",
         method: "POST"
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
%(tickets)s
</p>

</body>
</html>"""


"""
Generate tables of old tickets to edit or set as done
"""
def tickets_table(rows):
    info_style = "class='edit' style='display: inline' id='info_%(index)s'>"
    res = "<table>"
    if len(rows) > 0:
        res += "<tr><th></th><th></th><th>Description</th><th>Owner</th><th>Done</th></tr>"
    for t in rows:
        res += ("<tr>"
                "<td>"+str(t[0])+"</td>"
                "<td> - </td>"
                "<td class='edit' style='display: inline' id='info_"+  str(t['id'])+"'>"+cgi.escape(str(t['info']))+"</td>"
                "<td class='edit' style='display: inline' id='owner_"+ str(t['id'])+"'>"+cgi.escape(str(t['owner']))+"</td>"
                "<td class='done' style='display: inline' id='done_"+  str(t['id'])+"'>"+done_snowflake[t['done']]+"</td>"
                "</tr>")
    res += "</table>"
    return res

"""
The WSGI application
"""
def application(env, start_response):
    body= ''
    try:
        length=int(env.get('CONTENT_LENGTH', '0'))
    except ValueError:
        length= 0
    if length != 0:
        body=env['wsgi.input'].read(length)

    args = urlparse.parse_qs(body)

    # Add a new tickets
    if env['PATH_INFO'] == '/new':
        db.add(args.get("ticket")[0])

    # List old tickets
    oldtickets = tickets_table(db.getall())

    if env['PATH_INFO'] == '/edit':
        # Tiny edit (inlined)
        print("Args: "+str(args))
        target, index = args.get('id')[0].split('_')
        value = args.get('value')[0]
        if target == "done":
            db.set(target, done_snowflake[value], index)
        else:
            db.set(target, value, index)
        response_body = cgi.escape(value)
    else:
        # Redraw main interface
        response_body = html % {"tickets":    str(oldtickets),
                                "finished":   finished,
                                "unfinished": unfinished}

    status = '200 OK'
    response_headers = [('Content-Type', 'text/html'),
                        ('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)
    return [response_body]

"""
Server launcher
"""
def server():
    # WSGI server, passes request to application
    httpd = make_server(
        '0.0.0.0',   # Hostname
        8051,        # Port
        application  # Function to handle request
        )
    print "TICKETBLASTER - WSGI> Server launched and ready to serve"
    httpd.serve_forever()

"""
Launch the server in case a recular call is done
"""
if __name__ == '__main__':
    server()
