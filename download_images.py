"""
@author: Ana Luís Fogarin de S. Lima

"""

import sys 
import drms 
import os 
import csv

#from tqdm import tqdm
#from time import sleep

listDate = []
listTime = []

#CONFIGURE VARIABLES HERE 
EMAIL = 'automatic.download.ic@gmail.com' #Insert registered email here 

#Fieldnames are up to the user, but it's essential to provide DATE (yyyy/mm/dd) and TIME (hh:mm:ss)
fieldnames = ['Type','Year','Spot','Start','Max','End'] #Insert fieldnames from CSV File 
dateField = 'Year' #Insert fieldname that corresponds to DATE (yyy/mm/dd) 
timeField = 'Max'  #Insert fieldname that corresponds to TIME (hh:mm:ss)

#DO NOT CHANGE 
controlFile = 'controlDownloads.bin'  #Control file
continuum = 'continuum'
aia1600 = 'aia1600'
aia1700 = 'aia1700'

c = drms.Client(email=EMAIL, verbose=True)   #Creating an instance of drms.Client class 

def verifyOutputFile(): 
    global validDataFile 
    
    directory = (os.path.dirname(os.path.realpath(__file__)))  #Get currently directory 
    createFile = directory + os.sep + validDataFile   #Adress of the file 

    if not os.path.exists(createFile):  #Creates the file if necessary 
        outputFile = directory + os.sep + validDataFile
        
        with open(outputFile, 'w') as csvfile:  #Write the header of the file, this way prevent replication 
            
            #fieldnames = ['Type','Year','Spot','Start','Max','End'] #Using fieldnames makes it easier to put each data on the right position 
            w = csv.DictWriter(csvfile, fieldnames)       #Path to write on the file
            w.writeheader()
        
        print("Output file (" + validDataFile + ") created!")

def verifyDate():
    global newLines 
    global oldLines
    global validDataFile
    global invalidLines

    #fieldnames = ['Type','Year','Spot','Start','Max','End'] #Insert fieldnames from CSV File  
    
    controlE = 0 
    controlN = 0
    
    with open(flareFile) as inputFile:
        rowReader = csv.DictReader(inputFile) #DictReader allow do get only some specify part of the file, based on the header 
        
        for row in rowReader:
            completeRow = row #Receives the row
            dateList = row[dateField].split("-")  #Separate the column "Year" using "-" as the separation point
            year = dateList[0]                  #All the years (position 0) goes to "year"
    
            if (int(year) > 2011):                      
                #Before recording, it should verify if the row is already on the validDataFile 
                readFile = open(validDataFile, 'r')
                reader = csv.DictReader(readFile)     
                for existingRow in reader:
                    if completeRow == existingRow:
                        controlE = 1
                        oldLines += 1
                        
                    elif completeRow != existingRow:
#                        print("Nova linha\n",reader)
#                        print("Linha antiga\n",completeRow)
                        controlN = 1 
                readFile.close
 
                #Recording on validDataFile
                #ControlE = 0 and ControlN = 1: current line wasn't recorded
                #ControlE = 0 and ControlN = 0: current line is the first 
                if (controlE == 0 and controlN == 1) or (controlE == 0 and controlN == 0): 
                    outputFile = open(validDataFile, 'a', newline='')     
                    
                    #fieldnames = ['Type','Year','Spot','Start','Max', 'End'] #Using fieldnames makes it easier to put each data on the right position 
                    write = csv.DictWriter(outputFile, fieldnames)       #Path to write on the file
                    write.writerow({'Type': row['Type'], 'Year': row['Year'], 'Spot': row['Spot'], 'Start': row['Start'], 'Max': row['Max'], 'End': row['End']})
                    newLines += 1 
                                
                    outputFile.close         
            else:
                invalidLines += 1
                   
    print("Success on the verification!")
    print(newLines, " lines were add to the file", validDataFile)
    print(oldLines, " lines already exists on the file, and weren't duplicated")
    print(invalidLines, " lines were invalid and weren't add to the file")

def downloadImages(): 
    
    global validDataFile
    global continuumImages
    global aiaSixImages
    global aiaSevenImages
    global existingImages

    
#    print("\n\n-----------------------------------------------------")
    print("Starting downloading process")
    
#    for i in tqdm(range(1000)):
#        sleep(0.01)
    
    with open(validDataFile, 'r') as inputFile:
        row = csv.DictReader(inputFile)
        for row in row:
            #print(existingImages)
            dateFlare = row[dateField]  
            timeFlare = row[timeField]   

            listTime = timeFlare[:-3]
            
            #Relevant informations about current flare, to compare and avoid replication
            currentFlare = dateFlare + "_" + timeFlare
            currentFlare = currentFlare.replace(" ", "")
            
            #Read control file and decode it into "data"
            with open(controlFile, 'rb') as controlFileR:
                data = controlFileR.read()
                data = data.decode('utf-8')
                data = str(data)
                data = data.split('|')
                   
                #HMI Continuum  
                continuumFlare = currentFlare + "C" #Control flare continuum
                if continuumFlare in data: #Verify if the continuum flare has already been downloaded
                    #print("JUMP!")
                    existingImages += 1
                    
                elif continuumFlare not in data:   
                    dc = 'hmi.Ic_45s['+dateFlare +'_'+listTime+'_TAI/30m@30m]'
                    dc = dc.replace(" ", "") #Removes blank spaces
                    r = c.export(dc, method='url', protocol='fits')  #Using url/fits 
                    r.wait()
                    r.status
                    r.request_url
                    r.download(continuum)
                    
                    continuumImages += 1 
                    
                    with open(controlFile, 'ab+') as controlFileW:
                        controlFileW.write(continuumFlare.encode('utf-8'))
                        controlFileW.write('|'.encode('utf-8'))
                    
                #Downloading images on AIA 1600 and 1700 
                sixteenHundredFlare = currentFlare + "A16"
                if sixteenHundredFlare in data:
                    #print("JUMP!")
                    existingImages += 1
                    
                elif sixteenHundredFlare not in data:
                    da = 'aia.lev1_uv_24s['+dateFlare+'_'+listTime+'/30m@30m][1600]'
                    da = da.replace(" ", "") #Removes blank spaces
                    r = c.export(da, method='url', protocol='fits')
                    r.wait()
                    r.status
                    r.request_url
                    r.download(aia1600)
                    
                    aiaSixImages += 1
                    
                    with open(controlFile, 'ab+') as controlFileW:
                        controlFileW.write(sixteenHundredFlare.encode('utf-8'))
                        controlFileW.write('|'.encode('utf-8'))
                  
                seventeenHundredFlare = currentFlare + "A17"
                if seventeenHundredFlare in data:
                    #print("JUMP!")
                    existingImages += 1
                    
                elif seventeenHundredFlare not in data:    
                    daia = 'aia.lev1_uv_24s['+dateFlare+'_'+listTime+'/30m@30m][1700]'
                    daia = daia.replace(" ", "")    #Removes blank spaces
                    r = c.export(daia, method='url', protocol='fits')
                    r.wait()
                    r.status
                    r.request_url
                    r.download(aia1700)
                    
                    aiaSevenImages += 1
                    
                    with open(controlFile, 'ab+') as controlFileW:
                        controlFileW.write(seventeenHundredFlare.encode('utf-8'))
                        controlFileW.write('|'.encode('utf-8'))
                        
    totalImages = aiaSevenImages + aiaSixImages + continuumImages
    print("Download complete!")
    print("\n\n ----------------------------------------------------- ")
    print("Total of images downloaded: ", totalImages)
    print("HMI Continuum images: ", continuumImages)
    print("AIA 1600 images: ", aiaSixImages)
    print("AIA 1700 images: ", aiaSevenImages)
    print(existingImages, "weren't downloaded to avoid duplication.")
        
try:
    
    flareFile = sys.argv[1]
    validDataFile = flareFile[:-3] + 'correct.csv'
    #print(validDataFile)
    
    continuumImages = 0
    aiaSixImages = 0
    aiaSevenImages = 0
    existingImages = 0
    
    invalidLines = 0
    newLines = 0
    oldLines = 0
    
    if (newLines == 0): #Verify if the output file already exists. If it don't, than create it. 
        verifyOutputFile()

    verifyDate()

    directory = (os.path.dirname(os.path.realpath(__file__)))   #Get currently directory 
    
    #Creates controlFile when necessary 
    createFileControl = directory + os.sep + controlFile 
    if not os.path.exists(createFileControl):  
        file = open(controlFile, 'wb+')
        file.close
    
    #Creates destiny folders when necessary 
    if not os.path.exists(continuum):
        os.mkdir(continuum)
    
    if not os.path.exists(aia1600):
        os.mkdir(aia1600)
    
    if not os.path.exists(aia1700):
        os.mkdir(aia1700)

    downloadImages()
    
except IndexError:
    print("Incorrect parameters")
    print("Try: >$ python download_images.py <file_with_correct_flares.csv>")









