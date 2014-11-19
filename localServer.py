#this is for seting up a server on local netowork
#clients within the local network can connect to this server


from centreChat import*

s = server("127.0.0.1")
s.handleMessages()
