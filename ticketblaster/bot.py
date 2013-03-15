import socket
import db
from datetime import datetime
from datetime import timedelta
import random


def ping(ircsock):
  """ Respond to server pings. If not the server will close the connection """
  ircsock.send("PONG :Pong\n")


def sendmsg(ircsock, chan, msg):
  """ Send message to channels """
  ircsock.send("PRIVMSG " + chan + " :" + msg + "\n")


def joinchan(ircsock, chan):
  """ Join IRC channel """
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
    sendmsg(ircsock, channel, msg)


def add(ircsock, channel, info):
  """ Add a new ticket """
  db.add(info)
  sendmsg(ircsock, channel, "Added new ticket!")


def show(ircsock, channel):
  """ Show current set of tickets """
  tickets = db.getall(ticket_type='active')
  sendmsg(ircsock, channel, "Current available tickets:")
  for ticket in tickets:
    show_one(ircsock, channel, ticket)


def show_one(ircsock, channel, ticket):
  """ Show one ticket """
  sendmsg(ircsock, channel, " - " + str(ticket[0]) +
          ": " + ticket[1].encode("utf-8"))


def done(ircsock, channel, index):
  """ Mark a ticket as finished """
  db.set('done', True, index)
  sendmsg(ircsock, channel, "Finished ticket: " + index)


def grab(ircsock, channel, owner, index):
  """ Take and assign a ticket to the messanger """
  if db.exists(index):
    db.grab(owner, index)
    sendmsg(ircsock, channel, "Grabbed ticket: " + index +
            ", go fix it!!!")
  else:
    sendmsg(ircsock, channel + "No such ticket...")


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
  return (unicode(msg[msg.upper().find(space_cmd) +
                      len(space_cmd):].strip(), 'UTF-8'))


def random_burp(ircsock, channel, last_burp):
  """
  Every working hour there is a possibility we burp out a ticket to do
  to remind everyone...
  """
  tickets = db.getall(ticket_type='active')
  if ((datetime.now().day != last_burp.day
       and datetime.now().hour != last_burp.hour
       and datetime.now().hour > 9
       and datetime.now().hour < 18
       and datetime.now().minute == 0
       and (random.randint(0, 2) > 0)
       and len(tickets) > 0)):
    # Display one random ticket to do
    sendmsg(ircsock, channel, "Need something to do?")
    show_one(ircsock, channel, tickets[random.randint(0, len(tickets)-1)])
    last_burp = datetime.now()
  return last_burp


def loop(server, port, channel, botnick):
  """
  Connect and authenticate towards server then proceeds to put itself
  into the "neverending-loop" against the irc server
  """
  # Keep track of when we last burped, init from yesterday to get
  # going.
  last_burp = datetime.today() - timedelta(hours=1, days=1)
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
    elif (is_command(ircmsg, botnick, "hello") or
          is_command(ircmsg, botnick, "help")):
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
