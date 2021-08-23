#----------------
# This file is part of CktSync design manager
#----------------

import os
from multiprocessing.connection import Client

# Class for CktSync Client
class CktSyncClient():
  # Initialize
  def __init__(self):
    # Need server ip and port to start client
    self.server_ip = os.environ.get("CKTSYNC_SERVER")
    self.server_port = os.environ.get("CKTSYNC_PORT")
    if(self.server_ip is None or self.server_port is None):
      raise ValueError('CKTSYNC_SERVER or CKTSYNC_PORT is not defined.')
      
    self.server_port = int(self.server_port)

  # Send command to server and get response
  def SendCommand(self, cmd):
    server_address = (self.server_ip, self.server_port)
    # Check if server is running
    try:
      csynclient = Client(server_address)
    except:
      print("No server")
      return
    # conn.send('close')
    csynclient.send(cmd)
    resp = csynclient.recv()
    csynclient.close()
    return resp
