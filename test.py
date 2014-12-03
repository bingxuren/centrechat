#NOTE:this tester is only for the current version, this may not work with other
#students' code since we may handle connect and disconnect differently

from centrechat import*
import thread
import time
import random

s = ChatServer(1234)
thread.start_new_thread(s.handleMessages,())
time.sleep(1)
clientList = []
for i in range(4):
    client = ChatClient("127.0.0.1",1234,"dummy")
    clientList.append(client)
    thread.start_new_thread(client.handleMessages,())

#send radom message for testing
for i in range(10):
    random.shuffle(clientList)
    clientList[0].lossySend(str(i))

time.sleep(6)
curBuffer = clientList[0].rcvBuffer
for client in clientList:
    print client.rcvBuffer
    if client.rcvBuffer != curBuffer:
        print "fail"
    else:
        print "good"
print "finished"