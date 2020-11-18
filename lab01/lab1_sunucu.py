import socket
import sys
from time import time, ctime
import threading
import random

errCheckarr = ["TIC", "STA", "TRY", "QUI"]

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
		counter=10
		#try_count = random.randint(1, 20)
		while True:
			counter += 1
			try:
				# if try_count == 0:
				# 	self.conn.send(b"YOU LOSE\n")
				# 	try_count = random.randint(1, 20)
				# 	game_on = False
				# 	continue

				#while anlayamadığım bir şekilde çift dönüyor, dönüş mesajlarımın ikincisi anlamsız oluyor. onun harici çalışıyor

				data = self.conn.recv(1024)
				data_str = data.decode().strip()
				splitted = []
				if len(data_str) > 3:
					print(counter)
					a = data_str.split()
					splitted.append(a[0])
					splitted.append(int(a[1]))
					print(splitted)
				else:
					print(counter)
					splitted.append(data_str)
					print(splitted)
				if game_on == False:
					if splitted[0] == "TIC":
						self.conn.send(b"TOC\n")

					elif splitted[0] == "STA":
						self.conn.send(b"RDY\n")
						#self.conn.send(b"Remaning Try Count ->%s" % try_count)
						n = random.randint(1, 99)
						print("random sayi", n)
						game_on = True

					elif splitted[0] == "TRY":
						self.conn.send(b"GRR\n")

					elif splitted[0] not in errCheckarr :
						self.conn.send(b"ERR1\n")

				else:
					if splitted[0] == "TIC":
						self.conn.send(b"TOC\n")
					elif splitted[0] == "QUI":
						self.conn.send(b"BYE\n")
						game_on = False
					elif splitted[0] == "TRY" and splitted[1] < n :
						self.conn.send(b"LTH\n")
						# try_count -= 1
						#self.conn.send(b"Remaning Try Count ->%s" % try_count)
					elif splitted[0] == "TRY" and splitted[1] > n :
						self.conn.send(b"GTH\n")
						# try_count -= 1
						#self.conn.send(b"Remaning Try Count ->%s" % try_count)
					elif splitted[0] == "TRY" and splitted[1] == n :
						self.conn.send(b"WIN\n")
						# try_count -= 1
						#self.conn.send(b"Remaning Try Count ->%s" % try_count)
						game_on = False
						n = 100000
					elif splitted[0] not in errCheckarr:
						self.conn.send(b"ERR2\n")
			except:
				self.conn.send(b"PRR\n")

		self.conn.close()
		print(f"Thread kapanıyor : {self.threadID}")

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
