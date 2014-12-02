import socket
import select
import time
import thread
import threading
import random


class packet:
    def __init__(self, request):
        self.request = request
        self.sequenceNumber = None
        self.contentLength = None
        self.userName = None
        self.sender = None
        self.content = ""

    def getRequest(self):
        return self.request

    def getSequenceNumber(self):
        return self.sequenceNumber

    def getContentLength(self):
        return self.contentLength

    def getUserName(self):
        return self.userName

    def getSender(self):
        return self.sender

    def getContent(self):
        return self.content

    def setRequest(self, request):
        self.request = request

    def setSequenceNumber(self, sq):
        self.sequenceNumber = str(sq)

    def setContentLength(self, length):
        self.contentLength = str(length)

    def setUserName(self, name):
        self.userName = name

    def setSender(self, sender):
        self.sender = sender

    def setContent(self, content):
        self.content = content

    def getString(self):
        toReturn = ""
        tmpList1 = [self.request, self.sequenceNumber, self.contentLength, self.userName, self.sender]
        tmpList2 = ["", "Sequence-Number: ", "Content-Length: ", "User-Name: ", "Sender: "]
        for i in range(5):
            if (tmpList1[i] != None):
                toReturn += (tmpList2[i] + tmpList1[i] + "\r\n")
        toReturn += (self.content + "\r\n##")
        return toReturn



def parsePacket(pck):
    toReturn = packet(pck[:pck.find("\r\n")])
    if (pck.find("\r\nSequence-Number: ") != -1):
        toReturn.setSequenceNumber(pck[pck.find("\r\nSequence-Number: ")+ 19:pck.find("\r\n",pck.find("\r\nSequence-Number: ") + 17)])
        ##print toReturn.getSequenceNumber()
    if (pck.find("\r\nContent-Length: ") != -1):
        toReturn.setContentLength(pck[pck.find("\r\nContent-Length: ")+ 18:pck.find("\r\n",pck.find("\r\nContent-Length: ") + 16)])
        ##print toReturn.getContentLength()
    if (pck.find("\r\nUser-Name: ") != -1):
        toReturn.setUserName(pck[pck.find("\r\nUser-Name: ")+ 13:pck.find("\r\n",pck.find("\r\nUser-Name: ") + 11)])
        ##print toReturn.getUserName()
    if (pck.find("\r\nSender: ") != -1):
        toReturn.setSender(pck[pck.find("\r\nSender: ")+ 10:pck.find("\r\n",pck.find("\r\nSender: ") + 8)])
        ##print toReturn.getSender()
    if (toReturn.getContentLength() != None):
        l = int(toReturn.getContentLength())
        toReturn.setContent(pck[-l - 4 : pck.find("\r\n##")])
        ##print toReturn.getContent()
    ##print toReturn.getString()
    return toReturn



#--------------------------------------------------------------
class clientInfo:
    def __init__(self, name, glSQ, address):
        self.name = name
        self.globalSQ = glSQ
        self.ACK = -1
        self.SQ = 0
        self.address = address


#---------------------------------------------------------------
class ChatServer:
    def __init__(self, port, ip = "127.0.0.1"):
        self.clients = []       ## a list of clientInfo
        self.globalSQ = 0
        self.address = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.address)
        print self.sock.getsockname()[1]
        

    def getClients(self):
	l = []
	for client in self.clients:
		l.append(client.name)
	l.sort()
	return l


    def handleMessages(self):
        while True:
            rlist, wlist, elist = select.select([self.sock], [], [])
            pckString, clientAddress = rlist[0].recvfrom(1024)
            pck = parsePacket(pckString)
            print "\n-----------------------" + pckString + "---------------------\n"
            if (pck.request == "CG"):
                print "CG from " + str(clientAddress)
                self.handleCG(pck, clientAddress)
            if (pck.request == "CLOSE"):
                print "CLOSE from " + str(clientAddress)
                self.handleCLOSE(pck, clientAddress)
            if (pck.request == "MSG"):
                self.handleMSG(pck, clientAddress)
            if (pck.request == "ACK"):
                self.handleACK(pck, clientAddress)


    def handleCG(self, pck, clientAddress):
        CC = packet("CC")
        CC.setSequenceNumber(self.globalSQ)
        CC.setUserName(pck.getUserName())
        stringCC = CC.getString()
        self.sock.sendto(stringCC, clientAddress)
        tmpClient = clientInfo(pck.getUserName(), self.globalSQ, clientAddress)

        for client in self.clients:
            if client.address == tmpClient.address:
                self.clients.remove(client)             ## danger action, work on this later
                break
        self.clients.append(tmpClient)
        print pck.getUserName() + " connected to the server\n"

    def handleCLOSE(self, pck, clientAddress):
        CLOSE = packet("CLOSE")
        CLOSE.setUserName(pck.getUserName())
        stringCLOSE = CLOSE.getString()
        self.sock.sendto(stringCLOSE, clientAddress)
        for client in self.clients:
            if client.address == clientAddress:
                self.clients.remove(client)             ## danger action, work on this later
                break
        print pck.getUserName() + " left\n"


    def handleMSG(self, pck, clientAddress):
        print "\nMSG from " + pck.getSender() + "\n"
        sq = int(pck.getSequenceNumber())
        tmpClient = None
        for client in self.clients:
            if (client.address == clientAddress):
                tmpClient = client
                break
        if (tmpClient == None):
            return

        ACK = packet("ACK")
        ACK.setSender("SERVER")
        ##ACK.setSequenceNumber(sq)
        
        if (sq == tmpClient.SQ):
            tmpClient.SQ += 1  #################mod part not finished yet###
            self.broadcast(pck)
            print "sending ACK to " + pck.getSender() + "\n"
            ACK.setSequenceNumber(tmpClient.SQ - 1)##
            self.sock.sendto(ACK.getString(), clientAddress)
        if (sq < tmpClient.SQ):
            print "sending ACK to " + pck.getSender() + "\n"
            ACK.setSequenceNumber(tmpClient.SQ - 1)##
            self.sock.sendto(ACK.getString(), clientAddress)
        else:
            print "discard packet!"
            
    def broadcast(self, pck):
        pck.setSequenceNumber(self.globalSQ)
        sq = int(pck.getSequenceNumber())
        self.globalSQ += 1
        thread.start_new_thread(self.threadBroadcast,(pck, sq,))

    def threadBroadcast(self, pck, sq):
        tmpList = []
        for client in self.clients:############concurrency, work on this
            tmpList.append(client)
        for i in range(7):
            for client in tmpList:
                if (client in self.clients):
                    if (client.ACK < sq):
                        print "broadcast to " + client.name
                        self.sock.sendto(pck.getString(), client.address)
                    else:
                        tmpList.remove(client)
                else:
                    tmpList.remove(client)
            if (tmpList == []):
                print "\nbroadcasted\n"
                return
            time.sleep(0.4)
        for c in tmpList:
            print "\nbroadcasting failed to " + c.name
            if (c in self.clients):
                self.clients.remove(c)
                print c.name + " is removed from the clients"


    def handleACK(self, pck, clientAddress):
        tmpList = []
        for client in self.clients:
            tmpList.append(client)
        for client in tmpList:
            if (client.address == clientAddress):
                if (int(pck.getSequenceNumber()) > client.ACK):
                    client.ACK = int(pck.getSequenceNumber())
                    print "ACK from " + client.name
                    break



#----------------------------------------------------------

class ChatClient:
    def __init__(self, ip, port, name):
        self.lock = threading.RLock()
        self.windowSize = 5             ## how many threads are used for sending messages
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
        if len(msg) > 1000:
            print "message too large"
            return
        MSG = packet("MSG")
        MSG.setContent(msg)
        MSG.setSequenceNumber(str(self.sqToServer))
        MSG.setSender(self.userName)
        MSG.setContentLength(len(MSG.getContent()))
        self.sqToServer += 1
        while True:
            if ((int(MSG.getSequenceNumber()) - self.ackFromServer) < self.windowSize):
                print "\nsending:\n" + MSG.getString() + "\n"
                thread.start_new_thread(self.thread_send, (MSG,))
                break
            else:
                if self.connected:
                    print "waiting for window"
                    time.sleep(0.5)
                else:
                    return

    def lossySend(self,msg):  # use lossy_thread_send
        MSG = packet("MSG")
        MSG.setContent(msg)
        MSG.setSequenceNumber(str(self.sqToServer))
        MSG.setSender(self.userName)
        MSG.setContentLength(len(MSG.getContent()))
        self.sqToServer += 1
        while True:
            if ((int(MSG.getSequenceNumber()) - self.ackFromServer) < self.windowSize):
                print "\nsending:\n" + MSG.getString() + "\n"
                thread.start_new_thread(self.lossy_thread_send, (MSG,))
                break
            else:
                if self.connected:
                    print "waiting for window"
                    time.sleep(0.5)
                else:
                    return


    def lossy_thread_send(self, msgPCK):
        for i in range(6):  ##to have a better chance get all the messages sent
            if (self.connected):
                if random.randint(1,5) >= 3:
                    self.sock.sendto(msgPCK.getString(),self.serverAddress)
                time.sleep(1)## can work on this
                if (self.ackFromServer >= int(msgPCK.getSequenceNumber())):
                    print "\n" + "msg" + "  sent\n"
                    return
                print "\ntimeout, resend\n"
            else:
                print "not connected to server"
                return
        self.disconnect()




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
        self.disconnect()


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

    def getMessage(self):
        ##print "locked by get"
        self.lock.acquire()
        if len(self.rcvBuffer) > 0:
            toReturn = self.rcvBuffer[0]
            self.rcvBuffer.remove(toReturn)
            self.lock.release()
            ##print "unlocked by get"
            return toReturn
        else:
            self.lock.release()
            ##print "unlocked by get"
            return None
    

    def handleMSG(self, pck):
        sq = int(pck.getSequenceNumber())
        ACK = packet("ACK")
        ACK.setSender(self.userName)
        ##ACK.setSequenceNumber(sq)
        tmpMSG = (pck.getSender(), pck.getContent())
        if (sq == self.sqFromServer):
            self.sqFromServer += 1  #################mod part not finished yet###
            ##print "locked by handle"
            self.lock.acquire()##
            self.rcvBuffer.append(tmpMSG)
            self.lock.release()##
            ##print "unlocked by handle"
            print "\ngot a msg\n"
            print "sending a ack"
            ACK.setSequenceNumber(self.sqFromServer - 1)
            self.sock.sendto(ACK.getString(), self.serverAddress)
        elif (sq < self.sqFromServer):
            ACK.setSequenceNumber(self.sqFromServer - 1)
            self.sock.sendto(ACK.getString(), self.serverAddress)
        else:
            print "discard packet!"

    def disconnect(self):
        CMD = packet("CMD")
        CMD.setContent("disconnect")
        CMD.setContentLength(len(CMD.getContent()))
        self.sock.sendto(CMD.getString(), self.address)
        print "\nCMD sent for disconnecting\n"














        
