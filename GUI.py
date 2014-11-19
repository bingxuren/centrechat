##this is a simple GUI for testing


from graphics import*
from centreChat import*
import time
import thread
import random

code = raw_input("Please type your name: ")

c = client(str(code), "10.45.1.37")########
thread.start_new_thread(c.handleMessages, ())

win = GraphWin("chat",400,600)
win.setCoords(0,600,600,0)
textList = []
for i in range(12):
    textList.append(Text(Point(300,50 + i * 45), ""))
    textList[i].draw(win)

entry = Entry(Point(280,570),40)
entry.draw(win)
quit = Rectangle(Point(545,10),Point(599,30))
quit.draw(win)
Text(Point(572,20),"disconnect").draw(win)


button = Rectangle(Point(565,560), Point(595,580))
button.draw(win)

while True:
    for i in range(len(c.rcvBuffer)):
        if i < 12:
            toDis = str(c.rcvBuffer[len(c.rcvBuffer) - i - 1][0]) + ": " + c.rcvBuffer[len(c.rcvBuffer) - i - 1][1]
            textList[11 - i].setText(toDis)
    time.sleep(0.1)
    pt = win.checkMouse()
    if pt != None:
        x = pt.getX()
        y = pt.getY()
        if x > 565 and y < 595 and y > 560 and y < 580:
            string = entry.getText() + ""
            entry.setText("")
            c.sendMessage(string)
        if x > 545 and x < 600 and y > 10 and y < 30:
            c.disconnectServer()
            time.sleep(2)
            win.close()
            break
            
