from client import*
import random
import time
import thread

cList = []

for i in range(3):
	cList.append(client("testClient" + str(i), "10.45.1.37"))
	thread.start_new_thread(cList[i].handleMessages, ())
time.sleep(1)

for i in range(20):
	for c in cList:
		c.sendMessage("I am the best.")
	time.sleep(0.3)

for c in cList:
	c.disconnectServer()
time.sleep(2)

