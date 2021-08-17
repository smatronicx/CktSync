#----------------
# This file is part of CktSync design manager
#----------------

import sys
import getpass

# Class for CDS client
class CDSClient():
  # Initialize
  def __init__(self):
    self.user = getpass.getuser()
    
  # Start cds client
  def Start(self):
    while(True):
      self.ReadPacket()
  
  # Read packet
  def ReadPacket(self):
    # Read requrest from skill
    pkt = sys.stdin.readline()
    pkt = '{}: {}'.format(self.user, pkt)
    self.WritePacket(pkt)
  
  # Write packet
  def WritePacket(self, pkt):
    sys.stdout.write(pkt)
    sys.stdout.flush()

CDSClient().Start()
