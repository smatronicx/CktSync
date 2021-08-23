#----------------
# This file is part of CktSync design manager
#----------------

import os
from multiprocessing.connection import Listener

# Class for CktSync Client
class CktSyncServer():
  # Initialize
  def __init__(self):
    # Need server ip and port to start client
    self.server_ip = os.environ.get("CKTSYNC_SERVER")
    self.server_port = os.environ.get("CKTSYNC_PORT")
    if(self.server_ip is None or self.server_port is None):
      raise ValueError('CKTSYNC_SERVER or CKTSYNC_PORT is not defined.')
    
    self.server_port = int(self.server_port)
     
  # Start Server
  def Start(self):
    server_address = (self.server_ip, self.server_port)
    csynserver = Listener(server_address)
    while(True):
      csynclient = csynserver.accept()
      cmd = csynclient.recv()
      resp = self.ParseCommand(cmd) 
      csynclient.send(resp)
      csynclient.close()
  
  # Parse command
  def ParseCommand(self, cmd):
    return 'srv:{}'.format(cmd)

CktSyncServer().Start()
