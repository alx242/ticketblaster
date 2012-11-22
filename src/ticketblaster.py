#!/usr/bin/env python

import sys
import getopt
import ticketblaster_bot
from multiprocessing import Process

def usage(Exit):
  usage = "ticketblaster.py -s <server> -c <channel> -b <bot> -p <port>"
  print usage
  sys.exit(Exit)

# Main initiatior of the ticketblaster bot
def main(argv):
  server  = ""
  channel = "bob"
  botnick = "bob"
  port    = 6667
  try:
    opts, args = getopt.getopt(argv,"hs:c:b:p::",["server=","channel=","bot=","port="])
  except getopt.GetoptError:
    usage(2)
  for opt, arg in opts:
    if opt == "-h":
      usage(0)
    elif opt in ("-s", "--server"):
      server = arg
    elif opt in ("-c", "--channel"):
      channel = arg
    elif opt in ("-b", "--bot"):
      botnick = arg
    elif opt in ("-p", "--port"):
      port = arg
  if server == "":
    usage(2)

  bot  = Process(target=ticketblaster_bot.loop,
                 args=(server, int(port), "#"+channel, botnick))
  # wsgi = Process(target=ticketblaster_wsgi.server)
  bot.start() # Launch bot
  bot.join()  # Wait for child process to quite

  

if __name__ == "__main__":
  main(sys.argv[1:])
