import socket
from centreChat import*
import select
import time
import thread



sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", 0))
while True:
    string = raw_input(":  ")
    sock.sendto(string, ("127.0.0.1", 63122))
