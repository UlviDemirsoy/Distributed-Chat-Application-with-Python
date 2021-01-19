import socket
import sys
import datetime
import threading
from time import time, ctime
import random
import queue

global fihrist
fihrist = dict()

global roomDict
roomDict = dict()

class readThread(threading.Thread):

	def __init__(self, tName, sock, tqueue, logQ):
		threading.Thread.__init__(self)
		self.name = "logged_out"
		self.conn = sock
		self.tqueue = tqueue
		self.logQ = logQ
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
			pass

		elif len(data) == 3:
			if data == "OKG" or data == "OKP" or data == "OKW" or data == "TON" or data == "ERR" or data == "OKR" or data == "KCK" or data == "TMM":
				pass
			elif data == "QUI":
				self.logQ.put(self.name + " USED QUI COMMAND" + str(datetime.datetime.now())+ "\n")
				self.tqueue.put(f"BYE {self.name}\n")
				self.logged_in = False
				if self.name in fihrist.keys():
					fihrist[self.name][0] = None
				self.name = "logged_out"
			elif data == "PIN":
				self.tqueue.put("PON\n")
			elif data == "LAR":
				if self.logged_in == True:
					self.logQ.put(self.name + " Listed all rooms" + str(datetime.datetime.now()) + "\n")
					msg = "OLR "
					for i in roomDict.keys():
						msg += i + ":"
					msg = msg[:-1]
					self.tqueue.put(msg + "\n")
				else:
					self.tqueue.put("LRR\n")

			elif data == "RIM":
				if self.logged_in == True:
					self.logQ.put(self.name + " Listed all rooms in which s/he is:" + str(datetime.datetime.now()) + "\n")
					msg = "RYI "
					print(fihrist[self.name][2])
					for i in fihrist[self.name][2]:
						msg += i+":"
					msg = msg[:-1]
					self.tqueue.put(msg + "\n")
				else:
					self.tqueue.put("LRR\n")

			else:
				self.tqueue.put("ERR\n")

		elif len(data.split()) > 1:
			#:
			splitted = data.split()
			if splitted[0] == "GNL":
				if self.logged_in == True:
					text = " ".join(splitted[1:])
					splittedd = text.split(":")
					roomname = splittedd[0]
					msg = splittedd[1]
					if roomname in roomDict.keys():
						if roomname in fihrist[self.name][2]:
							self.logQ.put(self.name + " send general message to room> " + roomname + str(datetime.datetime.now()) + "\n")
							names = []
							names.extend(roomDict[roomname][0])
							names.extend(roomDict[roomname][1])
							names.remove(self.name)
							msg = self.name + ":" + roomname + ":" + msg + "\n"
							for i in names:
								(fihrist[i][0]).put(msg)
							self.tqueue.put("OKG\n")
						else:
							self.tqueue.put("RNL\n")
					else:
						self.tqueue.put("NAR\n")
				else:
					self.tqueue.put("LRR\n")

			elif splitted[0] == "GLS":
				if self.logged_in == True:
					roomname = splitted[1]
					if roomname in roomDict.keys():
						if roomname in fihrist[self.name][2]:
							admins = roomDict[roomname][0]
							users = roomDict[roomname][1]
							msg = ""
							for i in admins:
								msg += "Admin:" + i + ":"
							for i in users:
								msg += "User:" + i + ":"
							msg = msg[:-1]
							msg = "LST " + roomname + " " + msg + "\n"
							self.tqueue.put(msg)
							self.logQ.put(self.name + " listed users of the room>"+ roomname + str(datetime.datetime.now()) + "\n")
						else:
							self.tqueue.put("RNL\n")
					else:
						self.tqueue.put("NAR\n")
				else:
					self.tqueue.put("LRR\n")

			elif splitted[0] == "NIC":

				if len(splitted[1].split(":")) > 1:

					info = splitted[1].split(":")
					id = info[0]
					passwd = info[1]

					if self.logged_in == True:
						#passwd değiştirme isteği
						self.logQ.put(self.name + " changed password:" + str(datetime.datetime.now()) + "\n")
						fihrist[id][1] = passwd
						self.tqueue.put("NPW " + passwd + "\n")
					else:
						if id in fihrist.keys():
							# login

							if fihrist[id][1] == passwd:
								self.logQ.put(id + " logged in" + str(datetime.datetime.now()) + "\n")
								self.name = id
								fihrist[id][0] = self.tqueue
								self.tqueue.put("LSC " + id + "\n")
								self.logged_in = True
							else:
								self.tqueue.put("REJ\n")
								self.logQ.put(id + " login failed" + str(datetime.datetime.now()) + "\n")
						else:
							#yeni kullanıcı
							self.logQ.put(id + " user created" + str(datetime.datetime.now()) + "\n")
							fihrist[id] = [self.tqueue, passwd, []]
							self.logged_in = True
							self.name = id
							self.tqueue.put("WEL " + id + "\n")
				else:
					self.tqueue.put("ERR\n")

			elif splitted[0] == "NRM":
				if self.logged_in == True:
					roomname = splitted[1]
					if roomname in roomDict.keys():
						#oda zaten var
						self.tqueue.put("RCC\n")
					else:
						roomDict[roomname] = [[self.name], [], []]
						fihrist[self.name][2].append(roomname)
						self.tqueue.put("NRC\n")
						self.logQ.put(self.name + " created room> "+ roomname + str(datetime.datetime.now()) + "\n")

				else:
					self.tqueue.put("LRR\n")

			elif splitted[0] == "REQ":
				if self.logged_in == True:
					roomname = splitted[1]
					if roomname in roomDict.keys():
						banlist = roomDict[roomname][2]
						admins = roomDict[roomname][1]
						users = roomDict[roomname][0]

						if self.name in banlist:
							self.tqueue.put("RRQ\n")
							self.logQ.put(self.name + " is in banned list of room "+ roomname + str(datetime.datetime.now()) + "\n")
						elif self.name in admins or self.name in users:
							self.tqueue.put("ALR\n")
						else:
							self.tqueue.put("WNR " + self.name + "\n")
							self.logQ.put(self.name + " created the room>"+ roomname + str(datetime.datetime.now()) + "\n")
							roomDict[roomname][1].append(self.name)
							fihrist[self.name][2].append(roomname)
							#acaba ekledi mi dict'e
							print(roomDict[roomname][1])

					else:
						self.tqueue.put("NAR\n")
				else:
					self.tqueue.put("LRR\n")

			elif splitted[0] == "KCK":
				if self.logged_in == True:
					info = splitted[1].split(":")
					id = info[0]
					roomname = info[1]
					if roomname in roomDict.keys():
						admins = roomDict[roomname][0]
						users = roomDict[roomname][1]
						if self.name in admins and id in users:
							self.tqueue.put("OKK " + id + "\n")
							fihrist[id][0].put("KFR " + roomname + "\n")
							roomDict[roomname][1].remove(id)
							fihrist[id][2].remove(roomname)

						else:
							self.tqueue.put("RJK\n")
					else:
						self.tqueue.put("NAR\n")
				else:
					self.tqueue.put("LRR\n")

			elif splitted[0] == "BAN":
				if self.logged_in == True:
					info = splitted[1].split(":")
					id = info[0]
					roomname = info[1]
					if roomname in roomDict.keys():
						admins = roomDict[roomname][0]
						users = roomDict[roomname][1]
						if self.name in admins and id in users:
							self.tqueue.put("OKB " + id + "\n")
							self.logQ.put(self.name + " banned " + id + " from " + roomname + str(datetime.datetime.now()) + "\n")
							fihrist[id][0].put("VAC " + roomname + "\n")
							roomDict[roomname][1].remove(id)
							roomDict[roomname][2].append(id)
							fihrist[id][2].remove(roomname)

						else:
							self.tqueue.put("RJB\n")
					else:
						self.tqueue.put("NAR\n")
				else:
					self.tqueue.put("LRR\n")

			elif splitted[0] == "CLR":
				if self.logged_in == True:
					roomname = splitted[1]
					if roomname in roomDict.keys():
						admins = roomDict[roomname][0]
						users = roomDict[roomname][1]

						if self.name in admins:
							self.tqueue.put("OKC\n")
							for i in admins:
								fihrist[i][0].put("RCD " + roomname + "\n")
								fihrist[i][2].remove(roomname)
							for i in users:
								fihrist[i][0].put("RCD " + roomname + "\n")
								fihrist[i][2].remove(roomname)
							del roomDict[roomname]

						else:
							self.tqueue.put("RJC\n")

					else:
						self.tqueue.put("NAR\n")
				else:
					self.tqueue.put("LRR\n")



			elif splitted[0] == "QUR":
				if self.logged_in == True:
					roomname = splitted[1]
					if roomname in roomDict.keys():

						admins = roomDict[roomname][0]
						users = roomDict[roomname][1]
						if self.name in users:
							self.tqueue.put("OKL\n")
							self.logQ.put(self.name + "quitted room> "+ roomname + " " + str(datetime.datetime.now()) + "\n")
							roomDict[roomname][1].remove(self.name)
							fihrist[self.name][2].remove(roomname)
						elif self.name in admins:
							self.tqueue.put("OKL\n")
							self.logQ.put(self.name + "quitted room> " + roomname + " " + str(datetime.datetime.now()) + "\n")
							roomDict[roomname][0].remove(self.name)
							fihrist[self.name][2].remove(roomname)
						else:
							self.tqueue.put("RJQ\n")
					else:
						self.tqueue.put("NAR\n")

				else:
					self.tqueue.put("LRR\n")

			elif splitted[0] == "MKA":
				if self.logged_in == True:
					info = splitted[1].split(":")
					roomname = info[0]
					id = info[1]
					if roomname in roomDict.keys():
						admins = roomDict[roomname][0]
						users = roomDict[roomname][1]
						if self.name in admins and id in users:
							self.tqueue.put("OKA " + id + "\n")
							roomDict[roomname][0].append(id)
							roomDict[roomname][1].remove(id)
						else:
							self.tqueue.put("RJA\n")
					else:
						self.tqueue.put("NAR\n")

				else:
					self.tqueue.put("LRR\n")


			elif splitted[0] == "PRV" and self.logged_in == True:
				mesaj = " ".join(splitted[1:])
				splitted2 = mesaj.split(':')
				mesaj = self.name+":" + splitted2[1]

				if splitted2[0] in fihrist.keys():
					self.tqueue.put("OKP\n")
					fihrist[splitted2[0]].put(mesaj+"\n")
					self.logQ.put(self.name + " USED PRV COMMAND SEND THE MSG: >> " + mesaj + " to user >>" + splitted2[0]+ " " + str(datetime.datetime.now())+ "\n")
				else:
					self.tqueue.put("NOP\n")
					self.logQ.put(self.name + " USED PRV BUT INVALID DESTINATION: " + str(datetime.datetime.now()) + "\n")



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