#!/usr/bin/env python
"""
Author: Maryan Petryshyn
"""
import time
import logging
import snap7
import sys

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

DBlist = [25,27,33,140]

tcpport = 102
ip = '192.168.2.32'

def mainloop():
    server = snap7.server.Server()
    size = 20
    DBdata = (snap7.snap7types.wordlen_to_ctypes[snap7.snap7types.S7WLByte] * size)()
    MKdata = (snap7.snap7types.wordlen_to_ctypes[snap7.snap7types.S7WLByte] * size)()
    PAdata = (snap7.snap7types.wordlen_to_ctypes[snap7.snap7types.S7WLByte] * size)()
    PEdata = (snap7.snap7types.wordlen_to_ctypes[snap7.snap7types.S7WLByte] * size)()
    TMdata = (snap7.snap7types.wordlen_to_ctypes[snap7.snap7types.S7WLByte] * size)()
    CTdata = (snap7.snap7types.wordlen_to_ctypes[snap7.snap7types.S7WLByte] * size)()
    server.register_area(snap7.snap7types.srvAreaDB, 100, DBdata)
    server.register_area(snap7.snap7types.srvAreaMK, 100, MKdata)
    server.register_area(snap7.snap7types.srvAreaPA, 100, PAdata)
    server.register_area(snap7.snap7types.srvAreaPE, 100, PEdata)
    server.register_area(snap7.snap7types.srvAreaTM, 100, TMdata)
    server.register_area(snap7.snap7types.srvAreaCT, 100, CTdata)
    server.start_to(ip=ip,tcpport=tcpport)
    while True:
        while True:
            event = server.pick_event()
            if event:
                logger.info(server.event_text(event))
                '''
                for i in MKdata:
                	print(i,' ')
                	'''
                print(MKdata[0])	
                print(MKdata[1])	

            else:
                break
        time.sleep(1)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        snap7.common.load_library(sys.argv[1])
    mainloop()
