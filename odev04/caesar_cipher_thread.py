import queue
import threading
import time
import sys
import string

exitFlag = 0

s = int(sys.argv[1])

n = int(sys.argv[2])

l = int(sys.argv[3])

#items for cyription
alphabet_string = string.ascii_lowercase
lower_Alph = list(alphabet_string)
upper_Alph = list(alphabet_string.upper())

for i in range(s):
    a = upper_Alph.pop(0)
    upper_Alph.append(a)



uncyriptedList = []
cyriptedList = []


with open("input.txt") as f:
    while True:
        c = f.read(l)
        if not c:
            print("EOF")
            break
        uncyriptedList.append(c)



class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q

    def run(self):
        print("Starting " + self.name)
        crypt(self.name, self.q)
        print("exiting"+ self.name)

def crypt(threadName, q):
    while True:
        queueLock.acquire()
        if not q.empty():
            data = q.get()
            if data == "Quit":
                print("%s have received quit request" % (threadName))
                queueLock.release()
                break
            print("%s is processins %s" % (threadName, data))
            s = ""
            for letter in data:
                if letter in lower_Alph:
                    s += upper_Alph[lower_Alph.index(letter)]
                else:
                    s += letter
            print(s)
            cyriptedList.append(s)
            queueLock.release()
        else:
            queueLock.release()
        time.sleep(0.001)

# threadList = ["thread-1", "thread-2", "thread-3"]
# nameList = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight"]
queueLock = threading.Lock()
workQueue = queue.Queue(len(uncyriptedList))
threads = []
# threadID = 1

#fill the queue
queueLock.acquire()
for slice in uncyriptedList:
    workQueue.put(slice)
queueLock.release()

#create new threads
i = 0
for i in range(s):
    thread = myThread(str(i+1), str(str(i+1)+". thread"), workQueue)
    thread.start()
    threads.append(thread)
    i += 1


#wait for queue to empty
while not workQueue.empty():
    pass

#notify it is time t exit
for t in threads:
    workQueue.put("Quit")

#wait for all threads to complate
for t in threads:
    t.join()

cyriptedText = ""
for i in cyriptedList:
    cyriptedText += i

f2 = open("crypted_thread_15_14_16.txt", "w")
f2.write(cyriptedText)
f2.close()



print("exiting main thread")