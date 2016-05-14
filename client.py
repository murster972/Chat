#!/usr/bin/env python3
import os
import sys
import time
import socket
import threading

#TODO: Clean up code

class Client:
	def __init__(self):
		try:
			host_addr = (input("Server IP [blank for local]: ") or "127.0.0.1", int(input("Server Port Number: ")))
			if host_addr[1] < 0 or host_addr[1] > 65535: raise ValueError()
		except ValueError:
			print("Invalid server port number, must be in range 0-65535.")
			sys.exit(1)

		self.buff_size = 4096
		self.sending_msg = 0
		self.recv_que = []
		self.server_active = 1
		self.closing = 0
		self.user_name = ""
		self.intial_msg = ""

		#enters username before connecting so the server doesnt have to deal wiht blank usernames
		while not self.user_name and self.server_active: self.user_name = input("User Name: ")
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect(host_addr)
		except (OSError, OverflowError) as e:
			print("Can't connect to server, because the following error occured:\n{}".format(e))
			sys.exit(1)

		try:
			self.sock.send(self.user_name.encode("utf-8"))
			print("Waiting for server to respond...")
			timer = threading.Thread(target=self.timeout, daemon=True)
			timer.start()

			#seperate thread for intial message as the program wasn't exiting if 
			#it timedout it was getting stuck on self.sock.recv()
			intial_msg_thread = threading.Thread(target=self.get_intial_msg, daemon=True)
			intial_msg_thread.start()

			while not self.intial_msg and self.server_active: pass

			#if statement allows timer thread to aquire lock and prevents 'fatal python error'
			if not self.server_active: self.inactive_server()

			welcome_msg = self.intial_msg[1]
			if not welcome_msg or not self.user_name: raise UsernameError()
			if self.user_name != self.intial_msg[0]:
				print("As the username you entered is being used a random number has been added to the end.")
				self.user_name = self.intial_msg[0]
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
				#for 2s, giving the user the oppern
				#to raise a keyboard interrupt
				time.sleep(2)
			except KeyboardInterrupt:
				self.send()

		self.inactive_server()

	def get_intial_msg(self):
		'gets the intial message from the server'
		self.intial_msg = self.sock.recv(self.buff_size).decode("utf-8").split("\0")

	def send(self):
		'Get users Message and sends to server'
		if self.server_active:
			self.sending_msg = 1
			try:
				msg = input("\nMessage [leave blank to exit]\n: ")
				msg = msg if msg else "\0"
				self.sock.send(msg.encode("utf-8"))
			except OSError:
				self.inactive_server()
			except KeyboardInterrupt:
				msg = "\0"
				self.sock.send(msg.encode("utf-8"))

			self.sending_msg = 0

			if msg == "\0":
				self.sock.close()
				print("Closed Client.")
				sys.exit(0)

	def recv(self):
		'Recieves message from server and stores them in a queue'
		while True and self.server_active:
			try:
				reply = self.sock.recv(self.buff_size).decode("utf-8")
				if reply == "\0":
					self.server_active = 0
					self.inactive_server()
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

	def inactive_server(self):
		if not self.closing:
			self.closing = 1
			print("\nServer error. The server may be closed.")
			if self.sending_msg:
				print("Press enter to continue...")
			self.sock.close()
			print("Closed client.")
			sys.exit(1)

	def timeout(self):
		'timesout if server doesnt send intial msg within ~15s'		
		time.sleep(5)

		if not self.intial_msg:
			print("timed out.")
			self.server_active = 0
			self.inactive_server()

if __name__ == '__main__':
	os.system("clear")
	Client()