import socket
from centreChat import*
import select
import time
import thread


class client:
    def __init__(self, name, ip = "127.0.0.1", port = 43631):
        self.rcvBuffer = []             ## buffer for getMessage()
        self.sendingThreadCount = 0     ## count for current sending thread
        self.sqToServer = 0             ## sq# for th pck sending to server
        self.ackFromServer = -1          ## sq# for the ACK from server
        self.sqFromServer = 0           ## sq# for the pck from server (global sq#)
        self.userName = name            ## userName displayed to server and other clinets
        self.connected = False
        
        self.serverAddress = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", 0))
        self.address = ("127.0.0.1", self.sock.getsockname()[1])
        print self.address
        self.connectServer()
        



    def connectServer(self):
        self.sqToServer = 0             
        self.ackFromServer = -1         
        self.sqFromServer = 0
        self.sendingThreadCount = 0
        CG = packet("CG")
        CG.setUserName(self.userName)
        stringCG = CG.getString()
        inputList = [self.sock]
        for i in range(5):
            self.sock.sendto(stringCG, self.serverAddress)
            rlist, wlist, elist = select.select(inputList, [], [],1)
            if len(rlist) == 0:
                print "connection timeout! count: ",i
            else:
                tmpString = rlist[0].recv(2048)    # may want to check the address here
                CC = parsePacket(tmpString)
                self.sqFromServer = int(CC.getSequenceNumber()) # may want to also check the user name here
                print "connected to server.."
                self.connected = True
                break
    

    def privatedisconnect(self):
        CLOSE = packet("CLOSE")
        CLOSE.setUserName(self.userName)
        stringCLOSE = CLOSE.getString()
        inputList = [self.sock]
        for i in range(3):
            self.sock.sendto(stringCLOSE, self.serverAddress)
            rlist, wlist, elist = select.select(inputList, [], [],1)
            if len(rlist) == 0:
                print "disconnection timeout! count: ",i
            else:
                tmpString = rlist[0].recv(2048)    # may want to check the address here
                CLOSE = parsePacket(tmpString)
                if (CLOSE.request == "ACK"):
                    i = 1 - 1
                    self.ackFromServer = int(CLOSE.getSequenceNumber())
                if (CLOSE.request == "CLOSE"):
                    print "disconnected from the server.."
                    self.connected = False
                    break        
        if (self.connected):
            self.connected = False
            print "disconnected"
        self.sqToServer = 0             
        self.ackFromServer = 0          
        self.sqFromServer = 0
        self.sendingThreadCount = 0


    def sendMessage(self,msg):
        MSG = packet("MSG")
        MSG.setContent(msg)
        MSG.setSequenceNumber(str(self.sqToServer))
        MSG.setSender(self.userName)
        MSG.setContentLength(len(MSG.getContent()))
        self.sqToServer += 1
        while True:
            if ((int(MSG.getSequenceNumber()) - self.ackFromServer) < 5):
                print "\nsending:\n" + MSG.getString() + "\n"
                thread.start_new_thread(self.thread_send, (MSG,))
                break
            else:
                if self.connected:
                    print "occupied"
                    time.sleep(0.5)
                else:
                    return

    def thread_send(self, msgPCK):
        for i in range(3):
            if (self.connected):
                self.sock.sendto(msgPCK.getString(),self.serverAddress)
                time.sleep(1)## can work on this
                if (self.ackFromServer >= int(msgPCK.getSequenceNumber())):
                    print "\n" + "msg" + "  sent\n"
                    return
                print "\ntimeout, resend\n"
            else:
                print "not connected to server"
                return
        self.disconnectServer()


    def handleMessages(self):
        print "start handling messages"
        while True:
            rlist, wlist, elist = select.select([self.sock], [], [])
            pckString = rlist[0].recv(2048) ## same as discard
            if (self.connected):
                pck = parsePacket(pckString)
                if (pck.request == "CMD"):
                    print "\nGot a CMD\n"
                    self.handleCMD(pck)
                if (pck.request == "ACK"):
                    self.handleACK(pck)
                if (pck.request == "MSG"):
                    self.handleMSG(pck)


    def handleCMD(self, pck):
        if (pck.content == "disconnect"):
            print "\nHandling CMD for disconnection\n"
            self.privatedisconnect()

    def handleACK(self, pck):
        newACK = int(pck.getSequenceNumber())
        if (newACK > self.ackFromServer):
            self.ackFromServer = newACK

    def handleMSG(self, pck):
        sq = int(pck.getSequenceNumber())
        ACK = packet("ACK")
        ACK.setSender(self.userName)
        ACK.setSequenceNumber(sq)
        tmpMSG = (pck.getSender(), pck.getContent())
        if (sq == self.sqFromServer):
            self.sqFromServer += 1  #################mod part not finished yet###
            self.rcvBuffer.append(tmpMSG)
            print "\ngot a msg\n"
            print "sending a ack"
            self.sock.sendto(ACK.getString(), self.serverAddress)
        elif (sq < self.sqFromServer):
            self.sock.sendto(ACK.getString(), self.serverAddress)
        else:
            print "discard packet!"

    def disconnectServer(self):
        CMD = packet("CMD")
        CMD.setContent("disconnect")
        CMD.setContentLength(len(CMD.getContent()))
        self.sock.sendto(CMD.getString(), self.address)
        print "\nCMD sent for disconnecting\n"






##
##    ## get the next message from the buffer if the buffer is not empty
##    def getMessage(self):
##
##
##    ## send the message through a thread if it's connected
##    def sendMessage(self):


def main():
    cl = client("ye.sheng")
    thread.start_new_thread( cl.handleMessages, ())
    time.sleep(2)
    for i in range(13):
        cl.sendMessage(str(i))
    time.sleep(5)
    cl.disconnectServer()
    time.sleep(2)
    for msg in cl.rcvBuffer:
        print msg[0] + ":" + msg[1]







