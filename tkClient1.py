from Tkinter import *

from idlelib.WidgetRedirector import WidgetRedirector

import thread
import time
import centrechat
import random

#PORT = random.randint(5000,10000)

PORT = 5051

class ReadOnlyText(Text):
     def __init__(self, *args, **kwargs):
         Text.__init__(self, *args, **kwargs)
         self.redirector = WidgetRedirector(self)
         self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
         self.delete = self.redirector.register("delete", lambda *args, **kw: "break")




class ChatGui(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.client = None
        self.running = True
        self.pack()
        self.createWidgets()
    


    def getMessages(self):
         if(self.client == None):
              self.quit()
              return
         while(self.running):
              mess = self.client.getMessage()
              if(mess != None):
                   print "I got a message",mess
                   self.text.insert(END,mess[0]+":","handle")
                   self.text.insert(END,"  "+mess[1]+"\n")
              time.sleep(.1)
         print "closing listener" 


     
    def sendMessage(self):
        if(self.client ==None):
             return
        val =self.tField.get().strip()

        if(val !=""):
             self.client.sendMessage(val)
             self.tField.delete(0,END)

    def joinServer(self):
        

        handle = self.tHandle.get().strip()
        host = self.tHost.get().strip()
        if(handle == "" or host==""):
            return
        else:
            print "Joining Now",handle,host
            ##create client
            self.client = centrechat.ChatClient(host,PORT,handle)
            thread.start_new_thread(self.client.handleMessages,())

            ##create listener
            thread.start_new_thread(self.getMessages,())
            time.sleep(.1)

            #activate buttons  
            self.join_button["state"]=DISABLED
  
            self.leave_button["state"]=NORMAL
            self.send_button["state"]=NORMAL


    def leaveServer(self):
          print "Leaving Now"
          self.running=False
          if(self.client!=None):
               self.client.disconnect()
               time.sleep(3)
          self.quit()

    def createWidgets(self):
        top = Frame(self)

        self.tHandle = Entry(top)
        self.tHandle["width"] = 30

        label = Label(top,text="User")
        atHost = Label(top,text="@")
        self.tHost = Entry(top)
        self.tHost.insert(END,"localhost")
        self.tHost["width"] = 30

        
        self.join_button = Button(top)
        self.join_button["text"] = "Join"
        self.join_button["command"]=self.joinServer


        self.leave_button = Button(top)
        self.leave_button["text"] = "Leave"
        self.leave_button["command"]=self.leaveServer
        self.leave_button["state"]=DISABLED
        
        self.join_button.pack(side=LEFT)
        label.pack(side=LEFT)
        self.tHandle.pack(side=LEFT)
        atHost.pack(side=LEFT)
        self.tHost.pack(side=LEFT)
        self.leave_button.pack(side=LEFT)

        top.pack()

        middle = Frame(self)

        scrollbar = Scrollbar(middle)
        self.text = ReadOnlyText(middle,wrap=WORD,yscrollcommand=scrollbar.set)
        self.text.tag_configure("handle",foreground='red')
        #self.text.config(state=DISABLED)

        self.text.pack(side=LEFT)
        scrollbar.pack(side=RIGHT,fill=Y)

        middle.pack()

        bottom = Frame(self)
        self.tField = Entry(bottom)
        self.tField["width"] = 100

        self.send_button = Button(bottom)
        self.send_button["text"] = "Send Message"
        self.send_button["command"]=self.sendMessage
        self.send_button["state"]=DISABLED

        self.send_button.pack(side=LEFT)
        self.tField.pack(side=LEFT,fill=X)
        
        bottom.pack()
        
        
     
     



def runClient():
     root = Tk()
     app = ChatGui(master=root)
     app.mainloop()
     root.destroy()
        

        
def main():        
     #start a server
     ##S=centrechat.ChatServer(PORT)
     ##thread.start_new_thread(S.handleMessages,())
     ##time.sleep(1)

     #thread.start_new_thread(runClient,())
     
     runClient()


if __name__ == '__main__':
    try:
         main()
    except:
        import sys
        print sys.exc_info()[0]
        import traceback
        print traceback.format_exc()
        print "Press Enter to continue ..." 
        raw_input() 
