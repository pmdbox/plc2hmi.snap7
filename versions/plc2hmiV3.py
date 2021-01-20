#!/usr/bin/env python
"""
Author: Maryan Petryshyn
E-mail: maryan.petryshyn@outlook.com
"""
import time
import logging
import snap7
import sys
from collections import deque

logging.basicConfig()
logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.INFO)
logger.setLevel(logging.WARNING)


#Settings
server_ip = '192.168.2.32'
server_tcpport = 102
server_WorkInterval = 0

plc_ip = '192.168.2.112'
plc_rack = 0
plc_slot = 2
plc_tcpport = 102

DBlistNumbers = [25,27,77]
DBlist = {}
writesqueue = deque()

sleepTime = 0.5
processEventLog = False
eventCounter = 0
# End of Settings

def set_DBlist():
	for i in DBlistNumbers:
		DBlist[i] = { 'length': 0, 'data': ''}

def load_DB_info():
	for DBnumber, DBdata in DBlist.items():
		blockinfo = client.get_block_info('DB',DBnumber)
		DBdata['length'] = blockinfo.MC7Size
		DBdata['data'] = (snap7.snap7types.wordlen_to_ctypes[snap7.snap7types.S7WLByte] * blockinfo.MC7Size)()		

def load_DB_data():
	for DBnumber, DBdata in DBlist.items():	
		temp = client.db_read(DBnumber,0,DBdata['length'])
		for i in range(len(temp)):
			DBdata['data'][i] = temp[i]

def set_ServerBlocks():
	for DBnumber, DBdata in DBlist.items():
		server.register_area(snap7.snap7types.srvAreaDB, DBnumber, DBdata['data'])

def WriteToPLC(DB,Start,dataForPLC):	
	client.write_area(snap7.types.S7AreaDB,DB,Start,dataForPLC)

def eventCallback(event):
	logging.debug(event)

	DB = event.EvtParam2
	Start = event.EvtParam3
	Size = event.EvtParam4

	dataForPLC = bytearray()
	for i in range(Start,Start+Size):
		dataForPLC+=(DBlist[DB]['data'][i]).to_bytes(1, byteorder='big', signed=True)	
	writesqueue.append([DB,Start,dataForPLC])	


if __name__ == '__main__':

	server = snap7.server.Server()
	server.set_param(6,server_WorkInterval)
	client = snap7.client.Client()

	client.connect(plc_ip,plc_rack,plc_slot,plc_tcpport)
	set_DBlist()
	load_DB_info()
	set_ServerBlocks()
	server.start_to(ip=server_ip,tcpport=server_tcpport)
	server.set_mask(snap7.snap7types.mkEvent,0x00040000)
	#server.set_mask(snap7.snap7types.mkLog,0x00040000)
	server.set_events_callback(eventCallback)
	while True:
		eventCounter = 0

		while processEventLog:
			event = server.pick_event()
			if event:
				logger.info(server.event_text(event))
				eventCounter = eventCounter + 1
			else:
				break

		while True:
			try:
				writableElementToPLC=(writesqueue.popleft())
				WriteToPLC(writableElementToPLC[0],writableElementToPLC[1],writableElementToPLC[2])
				eventCounter = eventCounter + 1
			except IndexError:
				logger.info("No writable rows.")
				break

		logger.info("Read/write events/sec: "+str(eventCounter/sleepTime))
	
		load_DB_data()
		time.sleep(sleepTime)
	client.disconnect()