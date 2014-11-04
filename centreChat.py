
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


## testing
def testPacket():
    msg = packet("MSG")
    msg.setSequenceNumber(12386)
    msg.setContentLength(len("for my testing"))
    msg.setSender("ye.sheng")
    msg.setContent("for my testing")

    msg.setUserName("sapocaly")
    print msg.getString()


    msg1 = parsePacket(msg.getString())
    print msg1.getString()



##------------------------------------

class clientInfo:
    def __init__(self, name, glSQ, address):
        self.name = name
        self.globalSQ = glSQ
        self.ACK = -1
        self.SQ = 0
        self.address = address
        




















        
