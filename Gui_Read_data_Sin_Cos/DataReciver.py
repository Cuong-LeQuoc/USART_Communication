import time
import csv
import os
import cupy as cp
import numpy as np

class DataPool:
    def __init__(self):
        self.showData = False
        self.viewing = False
        self.saving = False

        self.fileName = "saveData"
        self.pathDirectory = ""

        self.state = [0, 0] # [sin, cos]
        self.msg = ['0', '0']

        self.timeDisplay = 8
        self.timeUpdateView = 100

        self.timeLine = 0

        self.timeList = []
        self.sinList = []
        self.cosList = []
        self.voltage = 0

    def vaildData(self):
        if (len(self.msg) == 2) and (self.msg[0] != 'S'):
            self.state[0] = float(self.msg[0])
            self.state[1] = float(self.msg[1])
            return True
        return False
    
    def setRefTime(self):
        if len(self.timeList) == 0:
            self.refTime = time.perf_counter()
        else:
            self.refTime = time.perf_counter() - self.timeList[len(self.timeList)-1]

    def updateData(self):
        self.timeLine = len(self.timeList)

        if self.timeLine == 0:
            self.timeList.append(0)
        else:
            self.timeList.append(time.perf_counter() - self.refTime)
        self.sinList.append(self.state[0])
        self.cosList.append(self.state[1])

    def adjustData(self):
        if len(self.timeList) == self.timeDisplay*1000:
            self.timeList.pop(0)
            self.sinList.pop(0)
            self.cosList.pop(0)
        return True

    def getPath(self, directory, file):
        self.pathDirectory = directory
        self.fileName = file

    def writeData(self):
        data = [self.timeList[self.timeLine],
                self.voltage,
                self.sinList[self.timeLine],
                self.cosList[self.timeLine]]
        filePath = os.path.join(self.pathDirectory, self.fileName + '.csv')
        print(self.pathDirectory)
        print(filePath)

        if not os.path.exists(self.pathDirectory):
            os.makedirs(self.pathDirectory)

        with open(filePath, mode='a', newline='') as file:
            writer = csv.writer(file)

            if file.tell() == 0:
                writer.writerow(["time", "sin", "cos"])

            writer.writerow(data)
            file.flush()
