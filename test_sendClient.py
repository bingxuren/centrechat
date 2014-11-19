from centreChat import*
import thread
import time

c = client("singer", "10.45.1.37")
thread.start_new_thread(c.handleMessages, ())
time.sleep(1)
while True:
    c.sendMessage(raw_input("send:  "))
    
