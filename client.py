#!/usr/bin/env python3
import os
import sys
import time
import socket
import threading

#TODO: create method that is called when an error occurs or the server closes

class Client:
	def __init__(self):
		try:
			host_addr = (input("Server IP [blank for local]: ") or "127.0.0.1", int(input("Server Port Number: ")))
		except ValueError:
			print("Invalid server port number.")
			sys.exit(1)

		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect(host_addr)
		except OSError:
			print("Can't connect to server. Invalid server IP or port number.")
			sys.exit(1)

		self.buff_size = 4096
		self.sending_msg = 0
		self.recv_que = []
		self.server_active = 1

		print("**If your selected user name is being used a random number will be added to the end of your user name**")
		self.user_name = ""

		while not self.user_name: self.user_name = input("User Name: ")

		try:
			self.sock.send(self.user_name.encode("utf-8"))
			intial_msg = self.sock.recv(self.buff_size).decode("utf-8").split("\0")
			welcome_msg = intial_msg[1]
			self.user_name = intial_msg[0]
		except (OSError, IndexError):
			print("Server error, may be closed.")
			self.sock.close()
			sys.exit(1)

		print("\n{}\nYour user name: {}\n".format(welcome_msg, self.user_name))

		self.recv_thread = threading.Thread(target=self.recv, daemon=True)
		self.recv_thread.start()
		self.show_thread = threading.Thread(target=self.show_msgs, daemon=True)
		self.show_thread.start()

		print("CTRL-C to enter a message.\n")

		while True and self.server_active:
			try:
				#means the code will stay in the loop
				#for 100s, giving the user the oppern
				#to raise a keyboard interrupt
				time.sleep(100)
			except KeyboardInterrupt:
				self.send()

		print("An error has occured, the server may be closed.")
		print("Client closed.")
		self.sock.close()

	def send(self):
		'Get users Message and sends to server'
		self.sending_msg = 1
		msg = input("\nMessage [leave blank to exit]\n: ").encode("utf-8")
		if not msg:
			#single null char represents the client closing
			self.sock.send("\0".encode("utf-8"))
			self.sock.close()
			print("Closed Client.")
			sys.exit(0)
		else:
			try:
				self.sock.send(msg)
				self.sending_msg = 0
			except OSError:
				self.server_active = 0

	def recv(self):
		'Recieves message from server and stores them in a queue'
		while True and self.server_active:
			try:
				reply = self.sock.recv(self.buff_size).decode("utf-8")
				if reply == "\0":
					self.server_active = 0
				else:
					self.recv_que.append(reply)
			except OSError:
				self.server_active = 0

	def show_msgs(self):
		'Prints messages currently in queue'
		while True and self.server_active:
			if self.recv_que and not self.sending_msg:
				tmp = [] + self.recv_que
				for i in range(len(tmp)):
					c = tmp[i].split("\0")
					print("{}: {}".format(c[0], c[1]))
					self.recv_que.remove(tmp[i])

if __name__ == '__main__':
	os.system("clear")
	Client()