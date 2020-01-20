"""
@author: Ana Luís Fogarin de S. Lima

"""

import sys 
import drms 
import os 
import csv

c = drms.Client(email='automatic.download.ic@gmail.com', verbose=True)   #Creating an instance of drms.Client class 

listDate = []
listTime = []

def downloadImages(): 
    
    global continuumImages
    global aiaSixImages
    global aiaSevenImages
    global alreadyExists

    with open(validDataFile, 'r') as inputFile:
        row = csv.DictReader(inputFile)
        for row in row:
            print(alreadyExists)
            listDate = row['Year']
            listTime = row['Max']

            listTime = listTime[:-3]
            
            yearFlare = row['Year']
            timeFlare = row['Max']
            
            #Relevant informations about current flare, to compare and avoid replication
            currentFlare = yearFlare + "_" + timeFlare
            currentFlare = currentFlare.replace(" ", "")
            
            with open(controlFile, 'r') as controlFileR:
                images = controlFileR.read()
                images = images.split('|')
                   
                #HMI Continuum  
                continuumFlare = currentFlare + "C"
                if continuumFlare in images:
                    #print("JUMP!")
                    alreadyExists += 1
                    
                elif continuumFlare not in images:
                    
                    dc = 'hmi.Ic_45s['+listDate +'_'+listTime+'_TAI/30m@30m]'
                    dc = dc.replace(" ", "") #Removes blank spaces
                    r = c.export(dc, method='url', protocol='fits')  #Using url/fits 
                    r.wait()
                    r.status
                    r.request_url
                    r.download(continuum)
                    
                    continuumImages += 1 
                    
                    with open(controlFile, 'a+') as controlFileW:
                        controlFileW.write(continuumFlare)
                        controlFileW.write('|')
                    
                #Downloading images on AIA 1600 and 1700 
                sixteenHundredFlare = currentFlare + "A16"
                if sixteenHundredFlare in images:
                    #print("JUMP!")
                    alreadyExists += 1
                    
                elif sixteenHundredFlare not in images:
                    da = 'aia.lev1_uv_24s['+listDate+'_'+listTime+'/30m@30m][1600]'
                    da = da.replace(" ", "") #Removes blank spaces
                    r = c.export(da, method='url', protocol='fits')
                    r.wait()
                    r.status
                    r.request_url
                    r.download(aia1600)
                    
                    aiaSixImages += 1
                    
                    with open(controlFile, 'a+') as controlFileW:
                        controlFileW.write(sixteenHundredFlare)
                        controlFileW.write('|')
                  
                seventeenHundredFlare = currentFlare + "A17"
                if seventeenHundredFlare in images:
                    #print("JUMP!")
                    alreadyExists += 1
                    
                elif seventeenHundredFlare not in images:    
                    daia = 'aia.lev1_uv_24s['+listDate+'_'+listTime+'/30m@30m][1700]'
                    daia = daia.replace(" ", "")    #Removes blank spaces
                    r = c.export(daia, method='url', protocol='fits')
                    r.wait()
                    r.status
                    r.request_url
                    r.download(aia1700)
                    
                    aiaSevenImages += 1
                    
                    with open(controlFile, 'a+') as controlFileW:
                        controlFileW.write(seventeenHundredFlare)
                        controlFileW.write('|')
                        
    totalImages = aiaSevenImages + aiaSixImages + continuumImages
    print(" Total of images downloaded: " + totalImages)
    print("HMI Continuum images: " + continuumImages)
    print("AIA 1600 images: " + aiaSixImages)
    print("AIA 1700 images: " + aiaSevenImages)
    print(alreadyExists + "weren't downloaded to avoid duplication.")
        
try:
    validDataFile = sys.argv[1]
    
    controlFile = "controlDownloads.txt" 
    continuum = 'continuum'
    aia1600 = 'aia1600'
    aia1700 = 'aia1700'

    continuumImages = 0
    aiaSixImages = 0
    aiaSevenImages = 0
    alreadyExists = 0

    directory = (os.path.dirname(os.path.realpath(__file__)))   #Get currently directory 
    
    #Creates controlFile when necessary 
    createFileControl = directory + os.sep + controlFile 
    if not os.path.exists(createFileControl):  
        file = open(controlFile, 'w+')
    
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









