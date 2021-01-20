#!/usr/bin/env python
"""
Author: Maryan Petryshyn
E-mail: maryan.petryshyn@outlook.com
"""
import time
import logging
import snap7
import sys

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.INFO)
#logger.setLevel(logging.WARNING)
#fh = logging.FileHandler('spam.log')
#fh.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#fh.setFormatter(formatter)
#logger.addHandler(fh)

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

sleepTime = 0.5
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

def WriteToPLC(DB,Start,Size):
	dataForPLC = bytearray()
	for i in range(Start,Start+Size):
		dataForPLC+=(DBlist[DB]['data'][i]).to_bytes(1, byteorder='big', signed=True)	
	client.write_area(snap7.types.S7AreaDB,DB,Start,dataForPLC)

if __name__ == '__main__':

	server = snap7.server.Server()
	server.set_param(6,server_WorkInterval)
	client = snap7.client.Client()

	client.connect(plc_ip,plc_rack,plc_slot,plc_tcpport)
	set_DBlist()
	load_DB_info()
	set_ServerBlocks()
	server.start_to(ip=server_ip,tcpport=server_tcpport)
	while True:
		while True:
			event = server.pick_event()
			if event:
				logger.info(server.event_text(event))
				if(event.EvtCode == 0x00040000):
					'''					
					print(event.EvtTime)
					print(event.EvtSender)
					print(event.EvtCode)
					print(event.EvtRetCode)
					print(event.EvtParam1)
					print(event.EvtParam2)
					print(event.EvtParam3)
					print(event.EvtParam4)
					print(server.event_text(event))
					'''
					WriteToPLC(event.EvtParam2,event.EvtParam3,event.EvtParam4)
			else:
				break
		load_DB_data()
		time.sleep(sleepTime)
	client.disconnect()