from client import*
import random
import time
import thread

cList = []

for i in range(8):
	cList.append(client("testClient" + str(i), "10.45.1.37"))
	thread.start_new_thread(cList[i].handleMessages, ())
time.sleep(1)

for i in range(20):
	for c in cList:
		c.sendMessage(str(i))
	time.sleep(0.6)

for c in cList:
	c.disconnectServer()
time.sleep(2)

for c in cList:
	print "-------------"
	for l in c.rcvBuffer:
		print str(l[0]) + ":" + str(l[1])
