from multiprocessing import Lock, Process, Queue, current_process
import time
import sys
import string
import os

lock = Lock()

s = int(sys.argv[1])

n = int(sys.argv[2])

l = int(sys.argv[3])

# items for cyription
alphabet_string = string.ascii_lowercase
lower_Alph = list(alphabet_string)
upper_Alph = list(alphabet_string.upper())

for i in range(s):
    a = upper_Alph.pop(0)
    upper_Alph.append(a)

uncyriptedList = []
#cyriptedList = []

def worker(lock,work_queue, done_queue):
    while True:
        print("acaba cıktım mı")
        lock.acquire()
        if not work_queue.empty():
           data = work_queue.get()
           if data == "STOP":
               print("Process received quit message %s"%(os.getpid()))
               lock.release()
               break
           #print("%s is being processed by child pid %s" % (data, os.getpid()))
           cryped = encrypt(data)
           print(data, cryped, os.getpid())
           done_queue.put(cryped)
           lock.release()
        else:
           lock.release()

def encrypt(slice):
    s = ""
    for letter in slice:
        if letter in lower_Alph:
            s += upper_Alph[lower_Alph.index(letter)]
        else:
            s += letter
    return s


def main():

    with open("input.txt") as f:
        while True:
            c = f.read(l)
            if not c:
                print("EOF")
                break
            uncyriptedList.append(c)

    workers = n
    work_queue = Queue()
    done_queue = Queue()
    processes = []
    for slice in uncyriptedList:
        work_queue.put(slice)

    for w in range(workers):
        p = Process(target=worker, args=(lock, work_queue, done_queue))
        p.start()
        processes.append(p)
        work_queue.put('STOP')

    #wait for queue to empty
    print("waiting")
    while not work_queue.empty():
        pass

    print(work_queue.qsize(),done_queue.qsize())

    print("done queue ops")
    done_queue.put('STOP')
    s = ""
    for piece in iter(done_queue.get, 'STOP'):
        s += piece

    f2 = open("crypted_fork_20_10_40.txt", "w")
    f2.write(s)
    f2.close()

    #joining
    print("joining")
    print(len(processes))
    for p in processes:
        print(p)
        print("acaba joinliyor mu")
        p.join()
        print("acaba joinliyor mu after p.join()")

    print("exiting parent process")

if __name__ == '__main__':
    print("starting main")
    main()
    print("finishing main")