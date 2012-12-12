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
         "add <TICKET INFO>  - Add a new ticket\n",
         "show               - Display all current tickets\n",
         "grab <TICKET ID>   - Assign ticket a owner\n",
         "delete <TICKET ID> - Delete a specific ticket (NOT IMPLEMENTED YET!)\n\n"
	 "Also check out my webserver running on http://%s:8051" 
         % socket.gethostbyaddr(socket.gethostname())[0])
  for msg in msgs:
    ircsock.send("PRIVMSG "+channel+" :"+msg)

def add(ircsock, channel, info):
  db.add(info)
  ircsock.send("PRIVMSG "+channel+" :Added new ticket!\n")

def show(ircsock, channel):
  tickets = db.getall()
  ircsock.send("PRIVMSG "+channel+" :Current available tickets:\n")
  for ticket in tickets:
    ircsock.send("PRIVMSG "+channel+" : - "+str(ticket[0])+
                 ": "+ticket[1].encode("utf-8")+"\n")

def delete(ircsock, channel, id):
  db.set('deleted', True, id)
  ircsock.send("PRIVMSG "+ channel +" : Removed ticket: "+id+" \n")

def grab(ircsock, channel, owner, id):
  if db.exists(id):
    db.grab(owner, id)
    ircsock.send("PRIVMSG "+channel+" : Grabbed ticket: "+id+
                 ", go fix it!!! \n")
  else:
    ircsock.send("PRIVMSG "+channel+" : No such ticket...\n")
    

def is_command(msg, botnick, command):
  return msg.upper().find(botnick.upper()+": "+command.upper()) != -1

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
      add(ircsock, channel, ircmsg[ircmsg.upper().find(" ADD")+4:])

    # Get all
    elif is_command(ircmsg, botnick, "show"):
      show(ircsock, channel)

    # Delete a ticket
    elif is_command(ircmsg, botnick, "del"):
      delete(ircsock, channel, ircmsg[ircmsg.upper().find(" DEL")+4:])

    # Grab a ticket
    elif is_command(ircmsg, botnick, "grab"):
      grab(ircsock, channel,
           ircmsg[ircmsg.upper().find(":")+1:ircmsg.upper().find("!")],
           ircmsg[ircmsg.upper().find(" GRAB")+5:])

