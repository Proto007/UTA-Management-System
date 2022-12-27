from datetime import datetime 
from enum import Enum
import time                                                                                                         #For sleep function(Debug Use)


'''
Probably good global variables

'''

'''
TODO:
- Edit the Buffer Period Time
    -Currently set to 5 seconds
- Set Intervals to reset the Check Ins(2 weeks)
-getTotalTimeWorked turn to tuple of hours, minutes


-need a function which can combine check in times ((10:45 - 11:30) + (12:00 - 12:30) = (10:45 - 12:00)) for the same day
-need a function which can combine all the data into 1 row of a CSV/df
    -Need format, Ideally:
        - (Last, First, Mon#1 Check-In, Mon#1 Check-Out, Tues#1 Check-In, Tues#1 Check-Out, ... , Fri#2 Check-Out)


First check in = how many shifts yer working (2)
Calculate estimated check out time and 

Put in CSV File


No more check - out system

Ko Button

If user checks in and doesn't have a shift at the current time, then they are given a choice of who they want to cover
'''
import pandas as pd
pd.options.mode.chained_assignment = None

class Activity(Enum):
    CHECK_IN = 1
    COVERING = 2


class UTA:
    #called via Admin UI to create Students
    def __init__(self, Name, EMPLID):                                                                               #Initialization of Student
        self._name = Name
        self._empl = EMPLID
        self._checkInArr = list()                                                                                   #Check In Array Format [datetime, Mode]
        self._schedule = self.getSchedule()
    

    def __str__(self):                                                                                              #String format of Student Obj(Only for Admin Terminal)
        outputStr = "Student: {}\nEMPLID: {}".format(self._name,self._empl)                                         #Header lines Name/ID
        for checkIn in self._checkInArr:
            outputStr+= "\n{} At: {} {}".format("Check in" if checkIn[1] == Activity.CHECK_IN else "Covering", checkIn[0].strftime("%A"),checkIn[0])                               #List of check ins
        return outputStr


    @staticmethod
    def validateInput(listToUse, activity):
        if(not len(listToUse) and activity == Activity.CHECK_IN):                                                   #Allows first check in if list is empty
            return True

        differenceInSeconds = (datetime.now() - listToUse[-1][0]).total_seconds()                                   
        if(differenceInSeconds > 5):                                                                                #Makes sure user doesn't check in/out too fast
            return True
        else:                                                                               
            #Prompt user that they are on cooldown
            return False


    #Called via Kiosk UI
    def checkIn(self):
        if(self.validateInput(self._checkInArr, Activity.CHECK_IN)):
            self._checkInArr.append([datetime.now(),Activity.CHECK_IN])


    def clearCheckIns(self):
        self._checkInArr = list()


    def getTotalTimeWorked(self):
        totalTimeWorked = 0
        for checkInTime, checkOutTime in zip(self._checkInArr, self._checkInArr[1:]):
            totalTimeWorked+=(checkOutTime[0] - checkInTime[0]).total_seconds()
        return totalTimeWorked

    #maybe can be done via Admin Kiosk?
    #privatize it if not done
    def getSchedule(self):
        schedule = list()
        df = pd.read_csv("https://docs.google.com/spreadsheets/d/1NZP84iehcwRFmXVLQR2tMzcpz4qUhado/export?format=csv&gid=387283422", index_col=0) #stores the CSV file into a data frame
        #note when uploading new csvfile, change to /export?format=csv
        name_formatted = ", ".join(self._name.split(" ")[::-1])                                                                                   #reformats name into last, first
        rowAccessed = df.loc[name_formatted]                                                                                                      #locates the row cooresponding to the name
        rowAccessed.dropna(how = "all", inplace=True)                                                                                             #removes all NaN columns
        rowAccessed.drop(rowAccessed[rowAccessed == "A"].index, inplace = True)                                                                   #removes all A columns
        return list(rowAccessed[:-2].index)


me = UTA("Umar Faruque", 23432423)
print(me.getSchedule())


'''
me.checkIn()
time.sleep(6)
me.checkIn()
time.sleep(9)
me.checkOut() #worked for 15 seconds
time.sleep(9)
me.checkIn()
time.sleep(4)
me.checkIn()
time.sleep(6)
me.checkOut()#worked for 10 seconds
'''


#print(f"Wow i worked so hard for {me.getTotalTimeWorked()} seconds")

#print(notme)


#shifts
#11:30 - 01:00
#01:00 - 02:30
#02:30 - 04:00
#04:00 - 05:30