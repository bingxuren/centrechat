#this is for seting up a server on my desktop
#clients within the centre network can connect to this server


from centreChat import*

s = server("10.45.1.37")
s.handleMessages()
