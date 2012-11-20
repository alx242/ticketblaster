import socket
import sqlite3
import sys
import getopt

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
  ircsock.send("PRIVMSG "+ channel +" :Hello!\n")

def connect():
  return sqlite3.connect('ticketblaster.db')

def insert(ircsock, channel, info):
  dbcon = connect()
  cur = dbcon.cursor()
  cur.execute("INSERT INTO ticket(info) VALUES('%(info)s')" % {"info": info})
  dbcon.commit()
  dbcon.close()
  ircsock.send("PRIVMSG "+ channel +" :Inserted new ticket!\n")

def show(ircsock, channel):
  dbcon = connect()
  cur = dbcon.cursor()
  cur.execute("SELECT * FROM ticket")
  rows = cur.fetchall()
  ticket = ""
  for row in rows:
    ircsock.send("PRIVMSG "+ channel +" : - " + row[1] + " \n")

# Connect and authenticate towards server
def bot(server, port, channel, botnick):
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
    if ircmsg.find(": Hello") != -1:
      hello(ircsock, channel)

    # If the server pings us then we've got to respond!
    if ircmsg.find("PING :") != -1:
      ping(ircsock)

    # Insert a new ticket
    if ircmsg.upper().find(": INSERT") != -1:
      insert(ircsock, channel, ircmsg[ircmsg.upper().find(": INSERT")+8:])

    # Get all
    if ircmsg.upper().find(": SHOW") != -1:
      show(ircsock, channel)

# Main initiatior of the ticketblaster bot
def main(argv):
  usage = 'ticketblaster.py -s <server> -c <channel> -b <bot> -p <port>'
  try:
    opts, args = getopt.getopt(argv,"hs:c:b:p::",["server=","channel=","bot=","port="])
  except getopt.GetoptError:
    print usage
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print usage
      sys.exit()
    elif opt in ("-s", "--server"):
      server = arg
    elif opt in ("-c", "--channel"):
      channel = arg
    elif opt in ("-b", "--bot"):
      botnick = arg
    elif opt in ("-p", "--port"):
      port = arg
  bot(server, int(port), "#"+channel, botnick)

if __name__ == "__main__":
  main(sys.argv[1:])
