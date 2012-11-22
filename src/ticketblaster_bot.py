import socket
import ticketdb

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
         "delete <TICKET ID> - Delete a specific ticket (NOT IMPLEMENTED YET!)\n")
  for msg in msgs:
    ircsock.send("PRIVMSG "+ channel +" :"+msg)

def add(ircsock, channel, info):
  ticketdb.add(info)
  ircsock.send("PRIVMSG "+ channel +" :Added new ticket!\n")

def show(ircsock, channel):
  tickets = ticketdb.getall()
  for ticket in tickets:
    ircsock.send("PRIVMSG "+ channel +" : - " + ticket[1] + " \n")

# Connect and authenticate towards server
def loop(server, port, channel, botnick):
  ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  ircsock.connect((server, port))
  ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :BOOOOT!\n")
  ircsock.send("NICK "+ botnick +"\n")
  joinchan(ircsock, channel) # Join the channel using the functions we previously defined

  # Bot loop
  while 1: # Be careful with these! It might send you to an infinite loop
    ircmsg = ircsock.recv(2048) # receive data from the server
    ircmsg = ircmsg.strip('\n\r') # removing any unnecessary linebreaks.
    print(ircmsg) # Here we print what's coming from the server

    # If we can find "Hello Mybot" it will call the function hello()
    if ircmsg.upper().find(": HELLO") != -1:
      hello(ircsock, channel)

    # If the server pings us then we've got to respond!
    if ircmsg.find("PING :") != -1:
      ping(ircsock)

    # Add a new ticket
    if ircmsg.upper().find(": ADD") != -1:
      add(ircsock, channel, ircmsg[ircmsg.upper().find(": ADD")+5:])

    # Get all
    if ircmsg.upper().find(": SHOW") != -1:
      show(ircsock, channel)

