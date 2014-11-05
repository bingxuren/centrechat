import socket
from centreChat import*
import select
import time
import thread

class server:
    def __init__(self, ip = "127.0.0.1", port = 43631):
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
                self.handleCG(pck, clientAddress)
            if (pck.request == "CLOSE"):
                self.handleCLOSE(pck, clientAddress)
            if (pck.request == "MSG"):
                self.handleMSG(pck, clientAddress)
            if (pck.request == "ACK"):
                print "ack from " + str(clientAddress)
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
        print "\ngot a msg from " + pck.getSender() + "\n"
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
        ACK.setSequenceNumber(sq)
        
        if (sq == tmpClient.SQ):
            tmpClient.SQ += 1  #################mod part not finished yet###
            self.broadcast(pck)
            print "sendingACK"
            self.sock.sendto(ACK.getString(), clientAddress)
        if (sq < tmpClient.SQ):
            print "sendingACK"
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
                    print "got an ACK from " + client.name
                    break





def main():
    sv = server("10.45.1.37")
    sv.handleMessages()

if __name__ == "__main__":
	main()
