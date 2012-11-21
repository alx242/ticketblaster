#!/usr/bin/env python

import sys
import getopt
import ticketblaster_bot

# Main initiatior of the ticketblaster bot
def main(argv):
  usage   = 'ticketblaster.py -s <server> -c <channel> -b <bot> -p <port>'
  server  = ''
  channel = ''
  botnick = ''
  port    = 6667
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
  
  ticketblaster_bot.loop(server, int(port), "#"+channel, botnick)

if __name__ == "__main__":
  main(sys.argv[1:])
