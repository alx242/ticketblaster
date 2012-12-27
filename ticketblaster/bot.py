import socket
import db

# Respond to server pings.
def ping(ircsock):
  ircsock.send("PONG :Pong\n")

# Send message to channels
def sendmsg(chan , msg):
  ircsock.send("PRIVMSG "+ chan +" :"+ msg +"\n")

# Join channel
def joinchan(ircsock, chan):
  ircsock.send("JOIN "+ chan +"\n")

# Responds to a user that inputs "Hello Mybot"
def hello(ircsock, channel):
  msgs = ("Hello! I currently accept these commands:\n",
          "add <TICKET INFO> - Add a new ticket\n",
          "show              - Display all current tickets\n",
          "grab <TICKET ID>  - Assign ticket a owner\n",
          "done <TICKET ID>  - Mark a ticket as finished\n\n"
          "Also check out my webserver running on http://%s:8051"
          % socket.gethostbyaddr(socket.gethostname())[0])
  for msg in msgs:
    ircsock.send("PRIVMSG "+channel+" :"+msg)

# Add a new ticket
def add(ircsock, channel, info):
  db.add(info)
  ircsock.send("PRIVMSG "+channel+" :Added new ticket!\n")

# Show current set of tickets
def show(ircsock, channel):
  tickets = db.getall()
  ircsock.send("PRIVMSG "+channel+" :Current available tickets:\n")
  for ticket in tickets:
    ircsock.send("PRIVMSG "+channel+" : - "+str(ticket[0])+
                 ": "+ticket[1].encode("utf-8")+"\n")

# Mark a ticket as finished
def done(ircsock, channel, id):
  db.set('done', True, id)
  ircsock.send("PRIVMSG "+ channel +" : Finished ticket: "+id+" \n")

# Take and assign a ticket to the messanger
def grab(ircsock, channel, owner, id):
  if db.exists(id):
    db.grab(owner, id)
    ircsock.send("PRIVMSG "+channel+" : Grabbed ticket: "+id+
                 ", go fix it!!! \n")
  else:
    ircsock.send("PRIVMSG "+channel+" : No such ticket...\n")

# Check if this is a message includes a specific command
def is_command(msg, botnick, command):
  return msg.upper().find(botnick.upper()+": "+command.upper()) != -1

# Find the sending nick in message
def nick_pars(msg):
  return msg[msg.upper().find(":")+1:msg.upper().find("!")].strip()

# Get the info part of a message (whatever comes after a command)
#
# E.g: " GRAB 1", " ADD Fix coffe"...
def info_parse(msg, cmd):
  space_cmd = " "+cmd.upper() # All commands must begin with a space
  return msg[msg.upper().find(space_cmd)+len(space_cmd):].strip()

# Connect and authenticate towards server
def loop(server, port, channel, botnick):
  ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  ircsock.connect((server, port))
  ircsock.send("USER "+botnick+
               " "+botnick+
               " "+botnick+
               " :BOOOOT!\n")
  ircsock.send("NICK "+botnick+"\n")
  joinchan(ircsock, channel) # Join the channel using the functions we previously defined

  # Bot loop
  while 1: # Be careful with these! It might send you to an infinite loop
    ircmsg = ircsock.recv(2048) # receive data from the server
    ircmsg = ircmsg.strip('\n\r') # removing any unnecessary linebreaks.
    print(ircmsg) # Here we print what's coming from the server

    # If the server pings us then we've got to respond!
    if ircmsg.find("PING :") != -1:
      ping(ircsock)

    # If we can find "Hello Mybot" it will call the function hello()
    elif is_command(ircmsg, botnick, "hello"):
      hello(ircsock, channel)

    # Add a new ticket
    elif is_command(ircmsg, botnick, "add"):
      add(ircsock, channel, info_parse(ircmsg, "add"))

    # Get all
    elif is_command(ircmsg, botnick, "show"):
      show(ircsock, channel)

    # Finish a ticket
    elif is_command(ircmsg, botnick, "done"):
      done(ircsock, channel, info_parse(ircmsg, "done"))

    # Grab a ticket
    elif is_command(ircmsg, botnick, "grab"):
      grab(ircsock, channel, nick_pars(ircmsg), info_parse(ircmsg, "grab"))

