"""
@author: Ana Luís Fogarin de S. Lima

"""

import sys 
import drms 
import os 
import csv

listDate = []
listTime = []

#CONFIGURE VARIABLES HERE 
EMAIL = 'automatic.download.ic@gmail.com' #Insert registered email here 

#Fieldnames are up to the user, but it's essential to provide DATE (yyyy/mm/dd) and TIME (hh:mm:ss)
fieldnames = ['Type','Year','Spot','Start','Max','End'] #Insert fieldnames from CSV File 
dateField = 'Year' #Insert fieldname that corresponds to DATE (yyy/mm/dd) 
yearField = 'Max'  #Insert fieldname that corresponds to TIME (hh:mm:ss)

#DO NOT CHANGE 
controlFile = 'controlDownloads.bin'  #Control file
continuum = 'continuum'
aia1600 = 'aia1600'
aia1700 = 'aia1700'

c = drms.Client(email=EMAIL, verbose=True)   #Creating an instance of drms.Client class 

def downloadImages(): 
    
    global continuumImages
    global aiaSixImages
    global aiaSevenImages
    global alreadyExists

    with open(validDataFile, 'r') as inputFile:
        row = csv.DictReader(inputFile)
        for row in row:
            print(alreadyExists)
            dateFlare = row[dateField]  
            timeFlare = row[yearField]   

            listTime = timeFlare[:-3]
            
            #Relevant informations about current flare, to compare and avoid replication
            currentFlare = dateFlare + "_" + timeFlare
            currentFlare = currentFlare.replace(" ", "")
            
            with open(controlFile, 'rb') as controlFileR:
                data = controlFileR.read()
                data = data.decode('utf-8')
                data = str(data)
                data = data.split('|')
                   
                #HMI Continuum  
                continuumFlare = currentFlare + "C" #Control flare 
                if continuumFlare in data:
                    #print("JUMP!")
                    alreadyExists += 1
                    
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
                    alreadyExists += 1
                    
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
                    alreadyExists += 1
                    
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
    print("\n\nTotal of images downloaded: ", totalImages)
    print("HMI Continuum images: ", continuumImages)
    print("AIA 1600 images: ", aiaSixImages)
    print("AIA 1700 images: ", aiaSevenImages)
    print(alreadyExists, "weren't downloaded because they already exists.")
        
try:
    validDataFile = sys.argv[1]
    
    continuumImages = 0
    aiaSixImages = 0
    aiaSevenImages = 0
    alreadyExists = 0

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









