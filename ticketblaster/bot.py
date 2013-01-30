import socket
import db
from datetime import datetime
import random


def ping(ircsock):
  """ Respond to server pings. If not the server will close the connection """
  ircsock.send("PONG :Pong\n")


def sendmsg(ircsock, chan, msg):
  """ Send message to channels """
  ircsock.send("PRIVMSG " + chan + " :" + msg + "\n")


def joinchan(ircsock, chan):
  """ Join channel """
  ircsock.send("JOIN " + chan + "\n")


def hello(ircsock, channel):
  """ Responds to a user that inputs "Hello Mybot" """
  msgs = ("Hello! I currently accept these commands:\n",
          "add <TICKET INFO> - Add a new ticket\n",
          "show              - Display all current tickets\n",
          "grab <TICKET ID>  - Assign ticket a owner\n",
          "done <TICKET ID>  - Mark a ticket as finished\n\n"
          "Also check out my webserver running on http://%s:8051"
          % socket.gethostbyaddr(socket.gethostname())[0])
  for msg in msgs:
    ircsock.send("PRIVMSG " + channel + " :" + msg)


def add(ircsock, channel, info):
  """ Add a new ticket """
  db.add(info)
  ircsock.send("PRIVMSG " + channel + " :Added new ticket!\n")


def show(ircsock, channel):
  """ Show current set of tickets """
  tickets = db.getall(ticket_type='active')
  ircsock.send("PRIVMSG " + channel + " :Current available tickets:\n")
  for ticket in tickets:
    ircsock.send("PRIVMSG " + channel + " : - " + str(ticket[0]) +
                 ": " + ticket[1].encode("utf-8") + "\n")


def done(ircsock, channel, id):
  """ Mark a ticket as finished """
  db.set('done', True, id)
  ircsock.send("PRIVMSG " + channel + " : Finished ticket: " + id + " \n")


def grab(ircsock, channel, owner, id):
  """ Take and assign a ticket to the messanger """
  if db.exists(id):
    db.grab(owner, id)
    ircsock.send("PRIVMSG " + channel + " : Grabbed ticket: " + id +
                 ", go fix it!!! \n")
  else:
    ircsock.send("PRIVMSG " + channel + " : No such ticket...\n")


def is_command(msg, botnick, command):
  """ Check if this is a message includes a specific command """
  return msg.upper().find(botnick.upper() + ": " + command.upper()) != -1


def nick_pars(msg):
  """ Find the sending nick in message """
  return msg[msg.upper().find(":") + 1:msg.upper().find("!")].strip()


def info_parse(msg, cmd):
  """
  Get the info part of a message (whatever comes after a command)
  E.g: " GRAB 1", " ADD Fix coffe"...
  """
  space_cmd = " " + cmd.upper()  # All commands must begin with a space
  return msg[msg.upper().find(space_cmd) + len(space_cmd):].strip()


def random_burp(ircsock, channel, last_burp):
  """
  Every hour there is a possibility we burp out the current tickets to
  remind everyone there is something to do
  """
  tickets = db.getall(ticket_type='active')
  if (datetime.now().hour != last_burp
      and datetime.now().minute == 0
      and random.randint(0, 2) > 0
      and len(tickets) > 0):
    ircsock.send("PRIVMSG " + channel +
                 " :Wake up there are tickets to be done!!!\n\n")
    show(ircsock, channel)
    last_burp = datetime.now().hour
  return last_burp


def loop(server, port, channel, botnick):
  """
  Connect and authenticate towards server then proceeds to put itself
  into the "neverending-loop" against the irc server
  """
  last_burp = 0  # Keep track of when we last burped
  ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  ircsock.connect((server, port))
  ircsock.send("USER " + botnick +
               " " + botnick +
               " " + botnick +
               " :BOOOOT!\n")
  ircsock.send("NICK " + botnick + "\n")
  # Join the channel using the functions we previously defined
  joinchan(ircsock, channel)
  # Bot loop
  while True:
    ircmsg = ircsock.recv(2048)  # Receive data from the server
    ircmsg = ircmsg.strip('\n\r')  # Removing any unnecessary linebreaks.
    print(ircmsg)  # Print whatever the server say on stdout
    last_burp = random_burp(ircsock, channel, last_burp)
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
