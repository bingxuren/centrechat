#a testing client


from centreChat import*
import thread
import random
import time

dummy = client("dummy", "10.45.1.37")
thread.start_new_thread(dummy.handleMessages, ())
time.sleep(2)
while True:
	dummy.sendMessage(["I need some water!", "I am sure that you are right.", "I really dont' want to do this?", "Is there anyone here?", "Oranges are good", "Nice to meet you.", "I am thirsty..", "Good deal!", "bed time"][random.randint(0,8)])
	time.sleep(random.randint(10,130))

