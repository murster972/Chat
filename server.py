#!/usr/bin/env python3
import os
import sys
import socket
from random import randint
from threading import Thread

class Server:
	def __init__(self):
		welcome_msg = """
 __________________________________________________________
|  ___       ___        ______   _   _   ______   _______  |
| |   \     /   |  __  |  ____| | |_| | |  __  | |__   __| |
| | |\ \   / /| | |__| | |      |  _  | | |__| |    | |    |
| | | \ \ / / | |      | |____  | | | | |  __  |    | |    |
| |_|  \___/  |_|      |______| |_| |_| |_|  |_|    |_|    |
|                                                          |
|_________________________ SERVER _________________________|
"""
		print(welcome_msg)

		#49152–65535 are dynamic and private ports
		addr = [input("Server IP [blank for local]: ") or "127.0.0.1", input("Set Port Number [blank for random]: ") or randint(49152, 65536)]
		if not isinstance(addr[1], int):
			print("Invalid port number, a port random number between 49152-65536 will be used instead.")
			addr[1] = randint(49152, 65536)
		addr = tuple(addr)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			self.sock.bind(addr)
		except OSError as e:
			print(e)
			print("Unable to bind server to {}".format(str(addr)))
			self.sock.close()
			sys.exit(1)

		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.listen(5)

		self.clients = []
		self.client_msgs = []
		self.buff_size = 4096
		self.client_numbers = 0
		self.client_user_names = {}

		while True:
			try:
				print("Server Listening on {} waiting for client to connect.".format(str(addr)))
				client, client_addr = self.sock.accept()
				self.client_numbers += 1
				self.clients.append((client, self.client_numbers))
				print("\nClient connected {} {}\n".format(str(self.client_numbers), client_addr))
				client_thread = Thread(target=self.handle_client, args=[(client, self.client_numbers)], daemon=True)
				client_thread.start()
			except (KeyboardInterrupt, OSError):
				break

		for i, j in self.clients: i.send("\0".encode("utf-8"))
		self.sock.close()
		print("Server Closed.")

	def handle_client(self, client):
		client_sock, client_num = client
		cur_clients = [x[1] for x in self.clients]
		
		user_name = client_sock.recv(self.buff_size).decode("utf-8")
		cur_users = [self.client_user_names[x] for x in self.client_user_names]

		while user_name in cur_users:
			user_name += str(randint(0, 9999))

		self.client_user_names[client_num] = user_name
		print("\nUSER: {}, has connected to the server.\n".format(user_name))

		cur_users = [self.client_user_names[x] for x in self.client_user_names]
		client_sock.send("{}\0CONNECTED TO SERVER. \nUSERS CONNECTED: {}".format(user_name, str(cur_users)).encode("utf-8"))

		self.client_msgs.append(("User-Name: {}, has connected".format(user_name), -1))
		recv_thread = Thread(target=self.recv_client_msgs, args=[client_sock, client_num], daemon=True)
		recv_thread.start()
		send_thread = Thread(target=self.send_client_msgs, daemon=True)
		send_thread.start()

	def recv_client_msgs(self, client_sock, client_num):
		client = (client_sock, client_num)
		'receives client msgs and stores them in client_msgs'
		while True:
			msg = client_sock.recv(self.buff_size).decode("utf-8")
			if msg == "\0":
				#single null char represents the client closing
				break
			elif msg:
				self.client_msgs.append((msg, client_num))

		self.remove_client(client_sock, client_num)

	def send_client_msgs(self):
		'send msgs to every client, except client who sent the msg'
		while True:
			if self.client_msgs:
				tmp = [] + self.client_msgs
				for m, n in tmp:
					self.client_msgs.remove((m, n))
					for c1, n1 in self.clients:
						if n1 != n:
							name = "SERVER MESSAGE" if n == -1 else self.client_user_names[n]
							m_send = name + "\0" + m
							try:
								c1.send(m_send.encode("utf-8"))
							except OSError:
								self.remove_client(c1, n1)

	def remove_client(self, client, client_num):
		try:
			self.clients.remove((client, client_num))
			user = self.client_user_names[client_num]
			del self.client_user_names[client_num]
		except KeyError:
			#client had not choosen a username
			pass
		print("Client: {}, {} has disconnected.".format(client_num, user))

if __name__ == '__main__':
	os.system("clear")
	Server()