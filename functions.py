import math
# import matplotlib.pyplot as plt
import simplekml
from selenium import webdriver
import time
from datetime import datetime
import socket
import os
import serial 
import re


#----------------------------------------------- Functions -------------------------------------------------#


#------------------------------------ User or GPS Input ---------------------------------------#

def userOrGPS():

    global x
    resetPrompt = str(input("Press U For User Coordinates Input \nPress G for GPS Input : "))
    while True:
        if resetPrompt != "U" and resetPrompt != "G":       # User input incorrect --> stay in While loop
            resetPrompt = str(input("Nope ! Press U or G : "))
        if resetPrompt == "U" :        # User input correct --> exit While loop and return M or A  
            x = 10
            break
        if resetPrompt == "G":
            x = 1
            break
    return x


#------------------------------- User Lon Lat Input is a Number Validation (decimal degrees) ------------------------------------#

def lonLatInput(stringLonOrLat,i):                              # My circleCoord() function creates a circle using the metric system, 
                                                                # I must therefore convert my nautical miles to meters,
                                                                # 1 nautical mile = 1852 meters
    while True:
        lonOrLat = input("Boat%d %s: " %(i,stringLonOrLat))
        try:
            val = int(lonOrLat)
            # print("%s is an Integer Number = " %stringLonOrLat, val )        # Nautical miles as an integer is accepted 
            break
        except ValueError:
            try:
                val = float(lonOrLat)
                # print("%s is a Float Number = " %stringLonOrLat, val )      # Nautical miles as a float is accepted 
                break
            except ValueError:
                print("This is not a number. Please enter a valid number") # Nautical miles as any other class/type is not accepted 
    return val



#-------------------------------- Create Circle from Centre Coordinates ----------------------------------------#

def circleCoord(radius,N,lat,lon):

    RADIUS = radius       # Meters
    CENTER_LAT = lat      # Latitude of circle center, decimal degrees
    CENTER_LONG = lon     # Longitude of circle center, decimal degrees


    M_2_DEG = 0.0000089831117499

    LatPoints = []
    LongPoints = []
    circlePoints = []
    coordinates = []                                           # Generate a list with the coordinates Lat and Lon

    for k in range(N):
        angle = math.pi*2*k/N                                  # Divide the circle in N points and thus N angles         
        dx = RADIUS*math.cos(angle)
        dy = RADIUS*math.sin(angle)
        point = {}                                             # Creates an empty dictionary to store points
        point['lat'] = CENTER_LAT + (180/math.pi)*(dy/6378137)
        point['lon'] = CENTER_LONG + (180/math.pi)*(dx/6378137)/math.cos(CENTER_LAT*math.pi/180)
        # add to list
        LatPoints.append(point['lat'])
        LongPoints.append(point['lon'])
        circlePoints.append(point)
        coordinates.append((point['lon'],point['lat']))        # Fill in list of coordinates that will be used to create the kml file  
                                                               # [(Lon1,Lat1),(Lon2,Lat2),....]
    # print(coordinates)

    return coordinates


#------------------------------------ Create Line kml file ---------------------------------------#

def kmlGenerator(coordinates): # Function not used 
    kml = simplekml.Kml()                                               
    lin = kml.newlinestring(name="GPSCircle", description="CoordCircle",coords=coordinates)
    lin.style.linestyle.color = simplekml.Color.rgb(255, 0, 0)
    # print(kml.kml())
    kml.save("My.kml")

#------------------------------------ Create Polygon kml file ---------------------------------------#

def kmlPolygonGenerator(circleColor,coordinates,smallCoord):
    kml = simplekml.Kml()
    pol = kml.newpolygon(name="GPSCircle", description="LatLonCircle",outerboundaryis=coordinates, innerboundaryis=smallCoord)
    pol.style.polystyle.outline = 1
    pol.style.polystyle.fill = 0
    pol.style.linestyle.color = circleColor     # Enter Hexagonal color code for circle Outline
    pol.style.polystyle.color = '007f7f7f'      # Enter Hexagonal color code for circle colour (Gray Looks Transparent)
    
    kml.save("MyPolygon.kml")                       # Save kml file 


#------------------------------------ Create Multiple Radius (for Routeur) ---------------------------------------#

def radiusMulticircles(radiusUserInput):
    listRadius = []
    listMultiplicateur = [1,2,4]
    for i in range(len(listMultiplicateur)):
        listRadius.append(radiusUserInput*listMultiplicateur[i]) # Multiply the input radius by 1,2 and 4
    listRadius.insert(0,300)                                     # The first radius in this list corresponds to the smallest circle used to locate the boat     
    # print(listRadius)                                          # The output is expressed in meters not in nautical miles 
    return listRadius 

#------------------------------------ Create Multiple Circle (for Routeur) ---------------------------------------#

def kmlMultiCircles(listRadius,N,lat,lon,circleColor):  

    from simplekml import Kml
    kml = Kml(open=1)
    kml = simplekml.Kml(open=1)

    # Create Multiple Polygons and put them in a list 
    circle1 = kml.newmultigeometry(name="Circle1") 
    circle2 = kml.newmultigeometry(name="Circle2") 
    circle3 = kml.newmultigeometry(name="Circle3") 
    circle4 = kml.newmultigeometry(name="Circle4") 
    # point1 =  kml.newmultigeometry(name="Point1") 

    listCircles = [circle1,circle2,circle3,circle4] 

    listCoord = [] # We will generate a list of lists 

    for i in range(len(listRadius)):
        listCoord.append(circleCoord(listRadius[i],N,lat,lon))
        listCircles[i].newpolygon(outerboundaryis=listCoord[i],innerboundaryis=listCoord[i]) # Putting the inner and outer boundaries the same removes the inside coloring
        # listCircles[i].style.polystyle.color = '007f7f7f'
        listCircles[i].style.polystyle.fill = 0
        listCircles[i].style.linestyle.color = circleColor
    # point1.newpoint(coords=[(lon, lat)])
    # print(listRadius)
    # print(listCoord)
    # print(listCircles)
    kml.save("MyPolygon.kml")
    return 


#------------------------------------ Create Multiple Circles for Multiple Boats (for Routeur) ---------------------------------------#

def kmlMultiBoats(N,nbBoats):  

    kml = simplekml.Kml()

    # Creating MultiGeometry
    multiBoat = kml.newmultigeometry(name="MultiPoint") 
    radius = radiusInput()                      # Outer radius of the donut (user input)
    listRadius = radiusMulticircles(radius)     # List of radius all the plotted circles  
    circleColor = colorInput(colorDict())      # Dictionary of colors in the user selection function
    for i in range(0,nbBoats,1):
        lonBoat = lonLatInput('lon',i)
        latBoat = lonLatInput('lat',i)

        boatCircles = []
        for i in range(len(listRadius)):
            x = circleCoord(listRadius[i],N,latBoat,lonBoat)
            boatCircles.append(x)
            multiBoat.newpolygon(outerboundaryis=x,innerboundaryis=x)
            multiBoat.style.polystyle.fill = 0
            multiBoat.style.linestyle.color = circleColor

    kml.save("MyPolygon.kml")
    return 


#------------------------------------ Selenium Windy ---------------------------------------#

def seleniumWindy(browser,reset,autoOrManual,sleepTime):

    #------------------------------------ SUPER IMPORTANT ---------------------------------------#
    x = 2

    kmlDirectory = os.getcwd()                                                     # Automatically find the path of the file in whiwh the Python Script is run 
    kmlDirectory = kmlDirectory[:2] + "\\" + kmlDirectory[2:] + "\\MyPolygon.kml"  # Create the appropriate path that Selenium can read

    if reset == 0: # Open the Upload webpage and paste the .kml file
        browser.find_element_by_id('upload-file').send_keys(kmlDirectory)
        time.sleep(0.2)
        reset = 1
    
    if reset == 1: # Click on the X to show the map in full screen
        elem = browser.find_element_by_xpath('//*[@id="plugin-uploader"]/div[2]')
        elem.click()
        time.sleep(0.2)
        reset = 2

    if reset == 2 and autoOrManual == 'A': # Automatic 
        # elem = browser.find_element_by_xpath('//*[@id="rhpane"]/div[2]') # Zooming out button
        # elem.click()
        # time.sleep(0.2)
        print("Press Ctrl + C to escape")
        time.sleep(sleepTime)
        browser.get('https://www.windy.com/uploader')
        reset = 0

    elif reset == 2 and autoOrManual == 'M': # Manual
        print('-------------------------------------------')

        resetPrompt = str(input("Press : \ny to Refresh \nCtrl + C to Terminate \ninit to change Config : "))

        while True: 
            if resetPrompt != "y" and resetPrompt != "init":
                resetPrompt = str(input("Type y or Ctrl + C or init:"))
            if resetPrompt == "y":                    # Refresh
                x = 2
                break
            if resetPrompt == "init":                 # ReConfig Radius, Colour and Automation Mode
                x = 0
                break
        browser.get('https://www.windy.com/uploader') # Open page to Upload new kml file 
        reset = 0  
    return x


#------------------------------------ Decode GPRMC Sentence ---------------------------------------#


decodedData = {} #Create an empty Dict that will be filled in by the functions below 


def decodeGPRMC(stringGPRMC):
    dictGPRMC  = {}                                  # Initialise an empty dictionary where,
                                                     # Key = GPRMC Component Attribute
                                                     # Value = GPRMC Component Value                     
    componentValues = []
    componentKeys = ["codeNMEA","timeStamp","navStat","Lat","latDir","Lon","lonDir","boatSpeed","trueCourse","dateStamp","magVar","magVarDir","checkSum"]
    NMEAComponents = stringGPRMC.split(",")          # Splits the string into a list of strings wherever you have a ","
    for i in range(len(NMEAComponents)):
        componentValues.append(NMEAComponents[i])    # Creates a list with the component values 
        # print(componentValues)

    zipGPRMC = zip(componentKeys,componentValues)    # Zip the 2 lists together
    dictGPRMC = dict(zipGPRMC)                       # Make the zip a Dict
    #print(dictGPRMC)
    
    return dictGPRMC
    


#------------------------- Decode Longitude and Latitude from GPRMC Sentence (DDMM.mm to dd) -------------------------------#


# def decodeLonLatUserInput(LonOrLat):                 # Decode lon and lat from User Input

#     LonOrLat = str()

#     for x in Lon:                                    # DDDMM.mm to dd
#         degree = float(Lon[:3])                        
#         minute = float(Lon[3:])
#         ddLon = LonDir*(degree + (minute/60))
#         ddLon = "{:.5f}".format(ddLon)               # Decimal places 
#         decodedData["Longitude"] = ddLon
#     # print(ddLon)


#     for x in Lat:                                    # DDMM.mm to dd
#         degree = float(Lat[:2])
#         minute = float(Lat[2:])
#         ddLat = LatDir*(degree + (minute/60))
#         ddLat = "{:.5f}".format(ddLat)               # Decimal places 
#         decodedData["Latitude"] = ddLat
#     # print(ddLat)
#     return decodedData


#------------------------------------ Convert NMEA Date to UTC datetime ---------------------------------------#

def date2utc(dates):           
    
    # input: NMEA date ddmmyy --> output : UTC date yy:mm:dd
    # output type: datetime.date
    
    utc = datetime.strptime(dates, "%d%m%y")
    return utc.date()


#------------------------------------ Convert NMEA Time to UTC datetime ---------------------------------------#

def time2utc(times):  

    # input: NMEA time hhmmss.ss --> output: UTC time hh:mm:ss.ss
    # output type: datetime.time

    utc = datetime.strptime(times, "%H%M%S.%f")
    return utc.time()


#------------------------------------ UDP Receiver ---------------------------------------#

def receiveUDP(ip,port):                            # The following function allows us to retrieve the message sent over UDP 

    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind((ip, port))

    try:
    
        data, addr = sock.recvfrom(1024)            # buffer
        messageReceived = data.decode("utf-8")      # converts the bytes data to strings !!!

        
        print("The GPRMC Sentence Received: \n")
        print("%s \n " % messageReceived) 
        return messageReceived

    except KeyboardInterrupt:
        print("Press Ctrl-C to terminate while statement")
        pass  


#------------------------------------ Color Dictionary ---------------------------------------#

def colorDict():

    colors = ['Red (R)','Orange (O)','Yellow (Y)','Green (G)','Light Blue (LB)', 'Dark Blue (DB)','Purple (P)','Pink (PK)'] # A list of colors for the user to choose from
    print(colors)

    dictColor = {}                                                                                      # Initialize a disctionary where,
                                                                                                        # Key = Hex Code
                                                                                                        # Color = Colour 1st letter in capital
    colorsShort = ['R','O','Y','G','LB', 'DB','P','PK']                                                 # Colors user will use as input 
    hexCode = ['990000ff','990080ff','6600fff5','6600ff00','99ffff00','99ff0000','66dd00ff','998000ff'] # https://htmlcolorcodes.com/ to choose colour
    zipColor = zip(colorsShort,hexCode)                                                                 # Zip the 2 lists together
    dictColor= dict(zipColor)                                                                           # Create Dictionary of zipped list

    # for i in dictColor:                                                                               # Used to print Hex Code and associated color letter     
    #     print (dictColor[i],i)
    
    return dictColor



#------------------------------------ User Color Input converted to HEX Code ---------------------------------------#

def colorInput(colorDictionary):

    colorChosen = str(input("Choose Your Colour:"))

    while True:
        if colorChosen in colorDictionary.keys():               # Check if user has chosen R,G,LB etc...
            colorChosenHex = colorDictionary[colorChosen]
            # print("Hex Code of %s is %s" % (colorChosen,colorChosenHex))
            break
        if colorChosen not in colorDictionary.keys():           # Incorrect user input then stay in the While loop
            colorChosen = str(input("Choose Your Colour Again:"))
            
    
    return colorChosenHex


#------------------------------------ User Radius Input is a Number Validation ---------------------------------------#

def radiusInput():                                              # My circleCoord() function creates a circle using the metric system, 
                                                                # I must therefore convert my nautical miles to meters,
                                                                # 1 nautical mile = 1852 meters
    while True:
        num = input("Enter Radius in Nautical Miles: \n")
        try:
            val = int(num)
            print("Radius is an Integer Number = ", val)        # Nautical miles as an integer is accepted 
            val = val*1852
            break
        except ValueError:
            try:
                val = float(num)
                print("Radius is an Float Number = ", val)      # Nautical miles as a float is accepted 
                val = val*1852
                break
            except ValueError:
                print("This is not a number. Please enter a valid number") # Nautical miles as any other class/type is not accepted 
    return val


#------------------------------------ User Auto or Manual Input Validation ---------------------------------------#

def autoOrManualFunc():

    resetPrompt = str(input("Press A For Automatic Refresh \nPress M for Manual Refresh : "))
    while True:
        if resetPrompt != "A" and resetPrompt != "M":       # User input incorrect --> stay in While loop
            resetPrompt = str(input("Nope ! \nPress A For Automatic Refresh \nPress M for Manual Refresh : "))
        if resetPrompt == "A" or resetPrompt == "M":        # User input correct --> exit While loop and return M or A  
            break
    return resetPrompt


    
#------------------------------------ Choose Refresh Rate of Selenium (in seconds)---------------------------------------#

def sleepInputSec(autoOrManual):

    if autoOrManual == "A":
        while True:
            num = input("I want to Refresh every ... seconds ")
            try:
                val = int(num)
                print("Refresh Rate in seconds : ", val)   # User input can only be an integer 
                val = val
                break
            except ValueError:
                print("Please select an Integer : ")
        return val
    elif autoOrManual == "M":
        return


#------------------------------------ Choose Refresh Rate of Selenium (in seconds)---------------------------------------#

def sleepInputMin(autoOrManual):

    if autoOrManual == "A":
        while True:
            num = input("I want to Refresh every ... minutes ")
            try:
                val = int(num)*60
                print("Refresh Rate in minutes : ", num)   # User input can only be an integer 
                val = val
                break
            except ValueError:
                print("Please select an Integer : ")
        return val
    elif autoOrManual == "M":
        return




#------------------------------------ Choose NB of Boats---------------------------------------#

def numberOfBoats():
    
    while True:
        num = input("I want to plot ... boats: ")
        try:
            val = int(num)
            print("Number of boats plotted : ", val)   # User input can only be an integer 
            val = val
            break
        except ValueError:
            print("Please select an Integer : ")
    return val


#------------------------------------ Print the GPRMC Decoded Data ---------------------------------------#

def printDecodedData(decodedData): # Function to print the decoded GPRMC Data in the dictionary
    
    print("The Decoded GPRMC Sentence: \n")
    print("Longitude: %s" % decodedData["Longitude"])
    print("Latitude: %s" % decodedData["Latitude"])
    print("Time: %s %s" % (decodedData["Date"],decodedData["Time"]))
    


#------------------------------------ Clear Kernel ---------------------------------------#    

# This Function was created to remove the error message that comes up
# upon the initialization of the Chrome Drive.
# The error in itself does not cause the script to fail,
# it is merely a warning that Chrome struggles with the compatibility of Selenium

from os import system, name

def clear():
    if name == 'nt':
        _ = system('cls')  # If the program is run on a Windows PC 

    else: 
        __=system('clear') # If the program is run on a Mac 


#------------------------------------ Initialize browser ---------------------------------------#  

def browserInit():
    print("Initialization :")
    browser = webdriver.Chrome('C:\\Windows\chromedriver.exe')  # Directory of the Chrome Driver (Chrome Version 94)
                                                                # Go to Chrome, Top right 3 dots, Help, About Google Chrome
    browser.maximize_window()                                   # Open Window in Full Screen
    browser.get('https://www.windy.com/uploader')               # Open Windy
    time.sleep(6)
    clear()                                                     # Removing the error message generated by the Chrome Driver 
    return browser

#------------------------------------ Initialize UDP Socket ---------------------------------------#  

def socketInit():

    global hostname 
    global ip
    global port

    hostname = socket.gethostname()                         # Utilizing the Python Socket package 
    ip = socket.gethostbyname(hostname)                     # Automatically retrieve the IP address of the computer
    port = 504                                              # Can be any port 
    print(f'Listening to IP:{ip} UDP Port:{port} \n')

    return hostname,ip,port


#------------------------------------ Initialize Global Variables ---------------------------------------#  

def initGlobal():

    global radius 
    global listRadius 
    global innerRadius
    global circleColor
    global autoOrManual
    global sleepTime

    radius = radiusInput()                      # Outer radius of the donut (user input)
    listRadius = radiusMulticircles(radius)     # List of radius all the plotted circles
    innerRadius = 300                           # Inner Radius of the donut (not a user input)                                        
    circleColor = colorInput(colorDict())      # Dictionary of colors in the user selection function
    autoOrManual = autoOrManualFunc()           # User Manual or Auto selection function 
    sleepTime = sleepInputSec(autoOrManual)     # User Sleep time selection function 

    return radius,listRadius,innerRadius,circleColor,autoOrManual,sleepTime


#------------------------------------ Read COM Port ---------------------------------------#  
# COM Port = ...
# Baudrate = 4800 



def readCOM():
    serialPort = serial.Serial(port="COM4",baudrate=4800)
    stringOfData = ""
    stringOfData = serialPort.readline()
    stringOfData.decode("Ascii")
    print(stringOfData)
    # Wait until there is data waiting in the serial buffer
    # if serialPort.in_waiting > 0:
    #     # Read data out of the buffer until a carraige return / new line is found
    #     stringOfData = serialPort.readline()
    #     stringOfData.decode("Ascii")
    #     print(stringOfData)
        # if "hello" in stringOfData:
        #     stringOfData.decode("Ascii")
        #     print(stringOfData)
    return stringOfData


def writeCOM():
    serialPort = serial.Serial(port="COM4",baudrate=4800)
    # my_str = "hello world"
    # my_str_as_bytes = str.encode(my_str)
    # serialPort.write(my_str_as_bytes)
    serialPort.write(b"yoyoyo")
    return

