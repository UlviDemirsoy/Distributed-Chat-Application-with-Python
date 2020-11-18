import socket
import sys
from time import time, ctime
import threading
import random



# global game_on
# game_on = False


class connThread(threading.Thread):
	def __init__(self, threadID, conn, c_addr):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.conn = conn
		self.c_addr = c_addr

	def run(self):
		self.conn.send("Sayi Bulmaca Oyunununa Hos geldiniz!\n".encode())
		print(f"Bağlantı kuruldu: {str(self.c_addr)}")

		game_on = False
		n = 100000

		while True:
			data = self.conn.recv(1024)
			data_str = data.decode().strip()
			splitted = ["", ""]
			if len(data_str) > 3:
				a = data_str.split()
				splitted[0] = a[0]
				splitted[1] = a[1]
			else:
				splitted[0] = data_str
			# if splitted[1].isdigit() == False:
			# 	self.conn.send(b"PRR\n")
			# 	continue

			if game_on == False:
				if splitted[0] == "TIC":
					self.conn.send(b"TOC\n")
				elif splitted[0] == "STA":
					self.conn.send(b"Oyun basliyor\n")
					n = random.randint(1, 99)
					game_on = True
					continue
				elif splitted[0] == "TRY":
					self.conn.send(b"GRR\n")
				# else:
				# 	self.conn.send(b"ERR1\n")

			elif game_on == True:
				if splitted[0] == "TIC":
					self.conn.send(b"TOC\n")
				elif splitted[0] == "QUI":
					self.conn.send(b"BYE\n")
					game_on = False
				elif splitted[0] == "TRY" and int(splitted[1]) < n :
					self.conn.send(b"LTH\n")
				elif splitted[0] == "TRY" and int(splitted[1]) > n :
					self.conn.send(b"GTH\n")
				elif splitted[0] == "TRY" and int(splitted[1]) == n :
					self.conn.send(b"WIN\n")
					n = 100000
				# else:
				# 	self.conn.send(b"ERR2\n")


		self.conn.close()
		print(f"Thread kapanıyor : {self.threadID} ")

s = socket.socket()

ip = "0.0.0.0"
port = int(sys.argv[1])

addr_server = (ip, port)
s.bind(addr_server)

s.listen(5)

counter = 0
threads = []

while True:
	conn, addr = s.accept() # blocking, bekleme
	t = connThread(counter, conn, addr)
	threads.append(t)
	t.start()
	counter += 1


s.close()
