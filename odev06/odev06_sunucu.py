import socket
import sys
import datetime
import threading
from time import time, ctime
import random
import queue

global fihrist
fihrist = dict()

class readThread(threading.Thread):

	def __init__(self, tName, sock, tqueue, logQ):
		threading.Thread.__init__(self)
		self.name = tName
		self.conn = sock
		self.tqueue = tqueue
		self.logQ= logQ
		self.control = False
		self.logged_in = False

	def run(self):
		print("ReaderThread starting")
		self.control = True
		while self.control:
			data = self.conn.recv(1024)
			data = data.decode()
			self.parsers(data)

	def parsers(self, message):
		data = message

		if len(data) == 0:
			self.tqueue.put("LRR\n")

		elif len(data) == 3:
			if data == "OKG" or data == "OKP" or data == "OKW" or data == "TON" or data == "ERR":
				pass
			elif data == "QUI":
				self.logQ.put(self.name + " USED QUI COMMAND" + str(datetime.datetime.now())+ "\n")
				self.tqueue.put(f"BYE {self.name}\n")
				#self.control = False
				self.logged_in = False
				if self.name in fihrist.keys():
					del fihrist[self.name]
			elif data == "PIN":
				self.tqueue.put("PON\n")
			elif data == "GLS" and self.logged_in == True:
				self.logQ.put(self.name + " USED GLS COMMAND" + str(datetime.datetime.now())+ "\n")
				if len(fihrist.keys()) > 0:
					liste = ""
					for i in fihrist.keys():
						liste += i+":"

					liste = liste[:-1]
					msg = "LST " + liste
					self.tqueue.put(msg+"\n")

				else:
					self.tqueue.put("LST\n")
			else:
				self.tqueue.put("ERR\n")
		elif len(data.split()) > 1:
			#:
			splitted = data.split()
			if splitted[0] == "GNL" and self.logged_in == True:

				mesaj = " ".join(splitted[1:])
				mesaj = self.name + ":" + mesaj
				for i in fihrist.values():
					i.put(mesaj+"\n")
				self.tqueue.put("OKG\n")
				self.logQ.put(self.name + " USED GNL COMMAND SEND THE MSG:" + mesaj + str(datetime.datetime.now()) + "\n")

			elif splitted[0] == "PRV" and self.logged_in == True:
				mesaj = " ".join(splitted[1:])
				splitted2 = mesaj.split(':')
				mesaj = self.name+":" + splitted2[1]

				if splitted2[0] in fihrist.keys():
					self.tqueue.put("OKP\n")
					fihrist[splitted2[0]].put(mesaj+"\n")
					self.logQ.put(self.name + " USED PRV COMMAND SEND THE MSG: >>" + mesaj + "to user >>" + splitted2[0] + str(datetime.datetime.now())+ "\n")
				else:
					self.tqueue.put("NOP\n")
					self.logQ.put(self.name + " USED PRV BUT INVALID DESTINATION:" + str(datetime.datetime.now())+ "\n")

			elif splitted[0] == "NIC":

				if splitted[1] not in fihrist.keys():
					self.name = splitted[1]
					self.logged_in = True
					fihrist[splitted[1]] = self.tqueue
					self.tqueue.put("WEL "+splitted[1]+"\n")
					self.logQ.put(self.name + " user created" + str(datetime.datetime.now())+ "\n")
				else:
					self.tqueue.put("REJ "+splitted[1]+"\n")
			else:
				self.conn.send(b"ERR\n")


class writeThread(threading.Thread):
	def __init__(self, tName, sock, tqueue, logQ):
		threading.Thread.__init__(self)
		self.conn = sock
		self.tqueue = tqueue
		self.name = tName
		self.logQ = logQ

	def run(self):
		print("WriterThread starting")

		while True:
			try:
				if self.tqueue.empty():
					pass
				else:
					data = self.tqueue.get()
					self.conn.send(data.encode())
			except: 
				print("WriterThread failed")
				break   
		print("WriterThread kapanıyor")

class loggerThread(threading.Thread):

	def __init__(self, logQ, FName):
		threading.Thread.__init__(self)
		self.logQ = logQ
		self.file = FName

	def run(self):
		print("LoggerThread starting")
		with open(self.file, "w") as file:
			while True:
				logData = self.logQ.get()
				file.write(str(logData))
				file.flush()

def main():
	if not len(sys.argv) == 3:
		print("Insufficient parameters")
		return
	print("Server started")
	s = socket.socket()
	host = sys.argv[1]
	port = int(sys.argv[2])

	s.bind((host,port))
	s.listen(5)

	counter = 0

	logQueue = queue.Queue()
	logThread = loggerThread(logQueue, str(counter))
	logThread.start()

	while True:
		conn, addr = s.accept()
		print(addr)
		tQueue = queue.Queue()
		rThread = readThread(counter, conn, tQueue, logQueue)
		rThread.start()
		wThread = writeThread(counter, conn, tQueue, logQueue)
		wThread.start()
		counter += 1

	s.close()

if __name__ == '__main__':
	main()