#-*- coding: utf-8 -*-

import socket, select
from random import randint
from AESCipher import AESCipher

RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
	

def send(sock, msg):
	try:
		msg = cipher.encrypt(msg)
	except:
		print "Encrypt error..."
		return 
	sock.send(msg)

def receive(sock):
	msg = sock.recv(RECV_BUFFER)
	try:
		msg = cipher.decrypt(msg)
	except:
		print "Decrypt error..."
		return 
	return msg.encode('utf-8')
 
#Function to broadcast chat messages to all connected clients
def broadcast_data (sock, msg):
	#Do not send the message to master socket and the client who has send us the message
	for socket in CONNECTION_LIST:
		if socket != server_socket and socket != sock :
			try:
				send(socket, msg)
			except :
				# broken socket connection may be, chat client pressed ctrl+c for example
				socket.close()
				CONNECTION_LIST.remove(socket)
 
if __name__ == "__main__":
	key = raw_input("Enter key:")
	cipher = AESCipher(key)
	
	# List to keep track of socket descriptors
	CONNECTION_LIST = []
	IP = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
	PORT = 9000
	 
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# this has no effect, why ?
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((IP, PORT))
	server_socket.listen(10)
 
	# Add server socket to the list of readable connections
	CONNECTION_LIST.append(server_socket)
 
	print "Chat server started on ip and port " + str(IP) + " " + str(PORT)
 
	while 1:
		# Get the list sockets which are ready to be read through select
		read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
 
		for sock in read_sockets:
			#New connection
			if sock == server_socket:
				# Handle the case in which there is a new connection recieved through server_socket
				sockfd, addr = server_socket.accept()
				CONNECTION_LIST.append(sockfd)
				print "Client (%s, %s) connected" % addr
				 
				broadcast_data(sockfd, "[%s:%s] entered room\n" % addr)
			 
			#Some incoming message from a client
			else:
				# Data recieved from client, process it
				try:
					#In Windows, sometimes when a TCP program closes abruptly,
					# a "Connection reset by peer" exception will be thrown
					msg = receive(sock)
					if msg:
						msg = "\r" + '<' + str(sock.getpeername()) + '> ' + msg
						broadcast_data(sock, msg)
				except:
					broadcast_data(sock, "Client (%s, %s) is offline" % addr)
					print "Client (%s, %s) is offline" % addr
					sock.close()
					CONNECTION_LIST.remove(sock)
					continue
	 
	server_socket.close()
