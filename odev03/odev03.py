import string
import re
import math
import numpy as np
import sys
from matplotlib import pyplot as plt

f = open("data\lab8_2.10-10.08-1.49.mbd", "r")
myArr = []
for line in f:
    line = line.strip('\n')
    line = line.split(",")
    myArr.append(line)

listofpairs = []
for i in myArr:
    listofpairs.append(i[1]+", "+i[2])
setofpairs = set(listofpairs)
listofpairs = list(setofpairs)

#dict to store repetition information
mydict1 = dict()

#RSSI Hıstograms
fig1, axes = plt.subplots(nrows=2, ncols=4)
fig1.tight_layout(pad=1.0)
index=1
for pair in listofpairs:

    # finding the max and the min
    max = -sys.maxsize - 1
    min = sys.maxsize
    for data in myArr:
        if pair == data[1] + ", " + data[2]:
            if int(data[-1]) > max:
                max = int(data[-1])
            if int(data[-1]) < min:
                min = int(data[-1])
    reps = range(min, max)
    counter = [0] * len(reps)

    # counting repetitions for each sensor and transmitter pair
    for data in myArr:
        for val in reps:
            if pair == data[1]+", "+data[2]:
                if val == int(data[-1]):
                    counter[reps.index(val)] += 1
   # print(pair)
   # print(reps)
   # print(counter)

    mytuple = (reps,counter)
    newelement = { pair:mytuple}
    mydict1.update(newelement)

#adding sub plots with index
    plt.subplot(2, 4, index)
    plt.bar(reps, counter, width=0.5, align='center', alpha=0.75)
    plt.title(pair, {'fontsize': 7, 'fontweight': "medium"})
    # pltname = pair+".png"
    # plt.savefig(pltname)
    # plt.show()
    index += 1
#saving image
plt.suptitle("RSSI Histogramı")
fig1.tight_layout(pad=1.0)
fig1.subplots_adjust(top=0.88)
plt.savefig("grafik1.png")

#ranges, repetitions and sensor-transmitter pairs
#print(mydict1)

#dict to store timestamps
mydict2 = dict()


#collecting timestamp data
for pair in listofpairs:

    timeStamps = []
    for data in myArr:
        if pair == data[1] + ", " + data[2]:
            timeStamps.append(data[0])

    newelement = {pair:timeStamps}
    mydict2.update(newelement)


#dict to store frequencies
mydict3 = dict()

#calculating frequencies
wsize = 100
for key, data in mydict2.items():

    window = []
    freqs= []

    for i in range(len(data)):
        if i < 100:
            window.append(float(data[i]))
        if i >= 100:
            fq = float(wsize) / (window[-1] - window[0])
            freqs.append(fq)
            window.append(float(data[i]))
            window.pop(0)
    newelement = {key: freqs}
    mydict3.update(newelement)

#clearing the old graphics and setting the news
plt.close(fig1)
fig2, axes = plt.subplots(nrows=2, ncols=4)
fig2.tight_layout(pad=1.0)

#drawing grafik2
i = 1
for x ,y in mydict3.items():
    plt.subplot(2, 4, i)
    i += 1
    val_list = y
    plt.plot(range(len(y)), y)
    plt.title(x, {'fontsize': 7, 'fontweight': "medium"})

fig2.suptitle("Anlık Frekans Değişimi", fontsize=10)
fig2.tight_layout(pad=1.0)
fig2.subplots_adjust(top=0.88)
plt.savefig("grafik2.png")



#drawing and constructing grafik3
plt.close(fig2)
fig3, axes = plt.subplots(nrows=2, ncols=4)
fig3.tight_layout(pad=1.0)

ranges = np.arange(1.5, 2.5, 0.05)

index=1
for x ,y in mydict3.items():
    counter = [0]*len(ranges)

    for i in range(len(ranges)-1):
        for number in y:
            if ranges[i]<number and  number<ranges[i+1]:
                counter[i] += 1


    plt.subplot(2, 4, index)
    index += 1
    plt.bar(ranges, counter, width=0.05, align='edge', alpha=0.75)
    plt.title(x, {'fontsize': 7, 'fontweight': "medium"})


fig3.suptitle("Anlık Frekans Histogramı", fontsize=10)
fig3.tight_layout(pad=1.0)
fig3.subplots_adjust(top=0.88)
plt.savefig("grafik3.png")