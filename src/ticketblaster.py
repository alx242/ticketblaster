#!/usr/bin/python
import sys
import socket
import string
import os

# Some basic variables used to configure the bot
server = "irc.hq.kred" # Server
channel = "#bob" # Channel
botnick = "Bob2" # Bot nick

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667))
ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :This bot is a result of a tutorial covered on http://shellium.org/wiki.\n")
ircsock.send("NICK "+ botnick +"\n")

# Respond to server pings.
def ping():
  ircsock.send("PONG :Pong\n")

# Send message to channels
def sendmsg(chan , msg):
  ircsock.send("PRIVMSG "+ chan +" :"+ msg +"\n")

# Join channel
def joinchan(chan):
  ircsock.send("JOIN "+ chan +"\n")

# Responds to a user that inputs "Hello Mybot"
def hello(newnick):
  ircsock.send("PRIVMSG "+ channel +" :Hello!\n")

# Connect and authenticate towards server
def main():
    joinchan(channel) # Join the channel using the functions we previously defined
    # Bot loop
    while 1: # Be careful with these! It might send you to an infinite loop
        ircmsg = ircsock.recv(2048) # receive data from the server
        ircmsg = ircmsg.strip('\n\r') # removing any unnecessary linebreaks.
        print(ircmsg) # Here we print what's coming from the server
        if ircmsg.find(":Hello "+ botnick) != -1: # If we can find "Hello Mybot" it will call the function hello()
            hello()
        if ircmsg.find("PING :") != -1: # if the server pings us then we've got to respond!
            ping()

if __name__ == "__main__":
    main()
