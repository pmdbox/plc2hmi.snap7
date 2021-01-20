import time
import snap7

client = snap7.client.Client()
client.connect('192.168.2.224', 0, 2)

def get_db1():
    all_data = client.db_get(1)

get_db1()
client.disconnect()    