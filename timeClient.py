from client import*
import time
import thread

c = client("ye's clock", "10.45.1.37")
thread.start_new_thread(c.handleMessages, ())
time.sleep(2)
while True:
	c.sendMessage(time.strftime(' %X %x %Z '))
	time.sleep(60)

	
