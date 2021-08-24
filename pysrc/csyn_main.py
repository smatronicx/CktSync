#----------------
# This file is part of CktSync design manager
#----------------

import cktsync
import os
import argparse
import sys

# Print help
def print_help():
  help_msg = '''
  usage: cktsync subcommands
  
  subcommands:
    server       Start CktSync Server
    project      Project management
  '''
  print(help_msg)

# Wrap arser to catch errors
def safe_parser():
  # Parse argument 
  if(len(sys.argv) < 2):
    # No arguments provided
    print_help()

  else:
    subcmd = sys.argv[1]
    # Start server
    if(subcmd == "server"):
      cktsync.CktSyncServer().ArgParser(sys.argv[2:])

    # Project manager
    elif(subcmd == "project"):
      cktsync.CktSyncProject().ArgParser(sys.argv[2:])

    # Print help
    else:
      print_help()
 
# Catch all expections
try:
  safe_parser()
except Exception as e:
  print(e)
