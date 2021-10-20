#----------------
# This file is part of CktSync design manager
#----------------

import os
import sys
import getpass

import cktsync

# Class for CDS client
class CDSClient():
    # Initialize
    def __init__(self):
        self.user = getpass.getuser()
        self.csynclient = cktsync.CktSyncClient()

    # Start cds client
    def Start(self):
        while(True):
            self.ReadPacket()

    # Read packet
    def ReadPacket(self):
        # Read requrest from skill
        pkt = sys.stdin.readline()
        cmd_dict = self.CreateCmd(pkt)
        resp_dict = self.csynclient.SendCommand(cmd_dict)
        resp_code = resp_dict['errcode']
        resp_msg = self.CSVEscape(resp_dict['msg'] )
        resp_str = '{},{}\n'.format(resp_code, resp_msg)
        self.WritePacket(resp_str)

    # Write packet
    def WritePacket(self, pkt):
        sys.stdout.write(pkt)
        sys.stdout.flush()

    # Convert packet to command
    def CreateCmd(self, pkt):
        pktlist = self.CSV2List(pkt.strip())
        cmd = pktlist[0]
        cmd_dict = {}
        cmd_dict['user'] = self.user
        if(cmd == 'cellci'):
            # Cell checkin
            cmd_dict['cmd'] = cmd
            cmd_dict['libpath'] = pktlist[1]
            cmd_dict['cellname'] = pktlist[2]
            cmd_dict['cellview'] = pktlist[3]
            cmd_dict['cimsg'] = pktlist[4]

        if(cmd == 'cellco'):
            # Cell checkout
            cmd_dict['cmd'] = cmd
            cmd_dict['libpath'] = pktlist[1]
            cmd_dict['cellname'] = pktlist[2]
            cmd_dict['cellview'] = pktlist[3]

        if(cmd == 'cellcanco'):
            # Cell checkout
            cmd_dict['cmd'] = cmd
            cmd_dict['libpath'] = pktlist[1]
            cmd_dict['cellname'] = pktlist[2]
            cmd_dict['cellview'] = pktlist[3]

        if(cmd == 'update'):
            # Update
            cmd_dict['cmd'] = cmd
            cmd_dict['libpath'] = pktlist[1]
            cmd_dict['cellname'] = pktlist[2]
            cmd_dict['cellview'] = pktlist[3]

        return cmd_dict

    # CSV to list
    def CSV2List(self, csvstr):
        rtnlist = []
        rtnitem = ''
        while(csvstr.find(',') != -1):
            idx = csvstr.index(',')
            if(idx == 0):
                # Empty string
                rtnlist.append(rtnitem)
                csvstr = csvstr[idx+1:]
                rtnitem = ''
            else:
                if(csvstr[idx-1] == '\\'):
                    rtnitem = rtnitem+csvstr[:idx+1]
                    csvstr = csvstr[idx+1:]
                    print(rtnitem)
                else:
                    rtnitem = rtnitem+csvstr[:idx]
                    csvstr = csvstr[idx+1:]
                    rtnlist.append(rtnitem)
                    rtnitem = ''

        rtnitem = rtnitem+csvstr
        rtnlist.append(rtnitem)

        return rtnlist

    # Escape CSV String
    def CSVEscape(self, csvstr):
        # Escape \n
        csvstr = csvstr.replace('\n', '\\n')
        # Escape ,
        csvstr = csvstr.replace(',', '\\,')
        return csvstr


CDSClient().Start()
