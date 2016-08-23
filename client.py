#-*- coding: utf-8 -*-

import socket, select, string, sys
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


def prompt() :
	sys.stdout.write('<You> ')
	sys.stdout.flush()
 
#main function
if __name__ == "__main__":
	key = raw_input("Enter key:")
	cipher = AESCipher(key)
	
	if(len(sys.argv) < 3) :
		print 'Usage : python telnet.py hostname port'
		sys.exit()
	 
	host = sys.argv[1]
	port = int(sys.argv[2])
	 
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)
	 
	# connect to remote host
	try :
		s.connect((host, port))
	except :
		print 'Unable to connect'
		sys.exit()
	 
	print 'Connected to remote host. Start sending messages'
	prompt()
	 
	while 1:
		socket_list = [sys.stdin, s]
		 
		# Get the list sockets which are readable
		read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
		
		for sock in read_sockets:
			#incoming message from remote server
			if sock == s:
				msg = receive(sock)
				if not msg :
					print '\nDisconnected from chat server'
					sys.exit()
				else :
					#print data
					sys.stdout.write(msg)
					prompt()
			 
			#user entered a message
			else :
				msg = sys.stdin.readline()
				send(s, msg)
				prompt()
