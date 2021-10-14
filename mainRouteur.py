
#----------- Making a .exe file -------------#
# Open cmd in the Python file directory
# pyinstaller.exe --onefile --incon=WindyLogoV1.ico main.py

from selenium import webdriver
# import time
import functions as fn
import socket 
# import simplekml
# import math
# import matplotlib.pyplot as plt
# import os
# import selenium


browser = fn.browserInit()

#----------------------------------------------- Additional Variables -------------------------------------------------#

N = 36     # Number of points that define the circle
reset = 0   # Variable used in the while loop
x = 0       # Variable used in the while loop 

#----------------------------------------------- Initiate the While Loop -------------------------------------------------#

try:
    while True:

        if x == 0:
            x = fn.userOrGPS()

        if x == 1:
            x = 2
            
            # Setting up the user input variables
            radius,listRadius,innerRadius,circleColor,autoOrManual,sleepTime = fn.initGlobal()
            # Local IP and Port for UDP communication
            hostname,ip,port = fn.socketInit() 
        
        if x == 2:
            x = 3                                         # Allows to transition to the next if statement             

            stringGPRMC = fn.receiveUDP(ip,port)          # Retrieving the GPS NMEA0183 sentence (GPRMC) via UDP

            dictGPRMC = fn.decodeGPRMC(stringGPRMC)       # Seperating the GPRMC sentence by elements in a dictionary 

            decodedData = fn.decodeLonLat(dictGPRMC["Lon"],dictGPRMC["Lat"],dictGPRMC["lonDir"],dictGPRMC["latDir"]) # Converting the Longitude and 
                                                                                                                     # Latitude from DDMM.mm to dd
            decodedData["Date"] = fn.date2utc(dictGPRMC["dateStamp"])                                                # Decoding the date
            decodedData["Time"] = fn.time2utc(dictGPRMC["timeStamp"])                                                # Decoding the time

            fn.printDecodedData(decodedData)
                            
            fn.kmlMultiCircles(listRadius,N,float(decodedData["Latitude"]),float(decodedData["Longitude"]),circleColor)    # Generate the 4 Circle kml file
               
        
        try:    

            if x == 3:
                x = 2                                         # Allows to transition to the next if statement      
                
                x = fn.seleniumWindy(browser,reset,autoOrManual,sleepTime)                                                     # Importing the kml file to Windy using Selenium 
                fn.clear()  

            if x == 10:
                x = 0
                nbBoats = fn.numberOfBoats()
                fn.kmlMultiBoats(36,nbBoats)
                x = fn.seleniumWindy(browser,reset,'M',0)
                fn.clear()  

        except KeyboardInterrupt:
            x = 0  
            browser = fn.browserInit()
            pass
            
except KeyboardInterrupt:
    print("Press Ctrl-C to terminate while statement")   
    pass
            

