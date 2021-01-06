"""
@author: Ana Luís Fogarin de S. Lima

"""
import sys 
import drms 
import os 
import csv
import urllib
import time
import shutil
from tqdm import tqdm
from time import sleep
import glob


from astropy.io import fits
from PIL import Image
import numpy as np
from os import listdir

# CONFIGURE VARIABLES HERE 
EMAIL = 'automatic.download.ic@gmail.com' #Insert registered email here 

# Fieldnames are up to the user, but it's essential to provide DATE (yyyy/mm/dd) and TIME (hh:mm:ss)
fieldnames = ['Type','Year','Spot','Start','Max','End'] #Insert fieldnames from CSV File 
dateField = 'Year' # Insert fieldname that corresponds to DATE (yyy/mm/dd) 
timeField = 'Max'  # Insert fieldname that corresponds to TIME (hh:mm:ss)
typeField = 'Type' # Insert fieldname that corresponds to the TYPE of the flare 

#DO NOT CHANGE 
controlFile = 'controlDownloads.bin'  # Control file
continuum = 'continuum'
aia1600 = 'aia1600'
aia1700 = 'aia1700'
separation = 's'
listDate = []
listTime = []
c = drms.Client(email=EMAIL, verbose=True)   # Creates an instance of drms.Client class 

fitsFiles = 0
pngFiles = 0
fitsConverted = 0

# This function is responsible to make sure that the file with valid data exists and has the right header
def verifyOutputFile(): 
    global validDataFile 
    global flareFile
    
    directory = (os.path.dirname(os.path.realpath(__file__)))  # Get currently directory 
    createFile = directory + os.sep + validDataFile   # Adress of the file 

    if not os.path.exists(createFile):  # Creates the file if necessary 
        outputFile = directory + os.sep + validDataFile
        
        with open(outputFile, 'w') as csvfile:  # Write the header of the file, this way prevent replication 
            w = csv.DictWriter(csvfile, fieldnames)       # Path to write on the file
            w.writeheader()
    
# This function is responsible to record only the data older than 2011 on the validDataFile that will be used to download images 
def verifyDate():
    global newLines 
    global oldLines
    global validDataFile
    global invalidLines
    
    controlE = 0 
    controlN = 0
    
    with open(flareFile) as inputFile:
        rowReader = csv.DictReader(inputFile) # DictReader allow do get only some specify part of the file, based on the header 
        
        for row in rowReader:
            completeRow = row # Receives the row
            dateList = row[dateField].split("-")  # Separate the column "Year" using "-" as the separation point
            year = dateList[0]                    # All the years (position 0) goes to "year"
    
            if (int(year) > 2011):                      
                # Before recording, it should verify if the row is already on the validDataFile 
                readFile = open(validDataFile, 'r')
                reader = csv.DictReader(readFile)     
                for existingRow in reader:
                    if completeRow == existingRow:
                        controlE = 1
                        oldLines += 1
                        
                    elif completeRow != existingRow:
                        controlN = 1 
                readFile.close
 
                # Recording on validDataFile
                # ControlE = 0 and ControlN = 1: current line wasn't recorded
                # ControlE = 0 and ControlN = 0: current line is the first 
                if (controlE == 0 and controlN == 1) or (controlE == 0 and controlN == 0): 
                    
                    outputFile = open(validDataFile, 'a', newline='')     
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

# Function responsible to download the images based on the validDataFile
def downloadImages(): 
    
    global validDataFile
    global continuumImages
    global aiaSixImages
    global aiaSevenImages
    global existingImages

    print("Starting downloading process")
    with open(validDataFile, 'r') as inputFile:
        row = csv.DictReader(inputFile)
        for row in row: 
            dateFlare = row[dateField]  
            timeFlare = row[timeField]   
            listTime = timeFlare[:-3]
            
            # Relevant informations about current flare, to compare and avoid replication
            currentFlare = dateFlare + "_" + timeFlare
            currentFlare = currentFlare.replace(" ", "")
            
            # Read control file and decode it into "data"
            with open(controlFile, 'rb') as controlFileR:
                data = controlFileR.read()
                data = data.decode('utf-8')
                data = str(data)
                data = data.split('|')
                   
                # Downloading images on HMI Continuum -------------------------------------------- 
                continuumFlare = currentFlare + "C" # Control flare continuum
                if continuumFlare in data: # Verify if the image has already been downloaded
                    existingImages += 1
                
                elif continuumFlare not in data:  
                    try:
                        print("------ CONTINUUM IMAGE DOWNLOAD --------")
                        dc = 'hmi.Ic_45s['+dateFlare +'_'+listTime+'_TAI/30m@30m]'
                        dc = dc.replace(" ", "") # Removes blank spaces
                        r = c.export(dc, method='url', protocol='fits')  # Using url/fits 
                        r.wait()
                        r.status
                        r.request_url
                        if 'X' in row[typeField]: 
                            r.download(continuum + '/x')
                        
                        elif 'M' in row[typeField]:
                            r.download(continuum + '/m')
                        
                        elif 'C' in row[typeField]:
                            r.download(continuum + '/c')
                            
                        elif 'B' in row[typeField]:
                            r.download(continuum + '/b')
                            
                        continuumImages += 1 
                        
                    except drms.DrmsExportError:
                        print("Current image doesn't have records online. It can't be downloaded.")
                        with open('notFound.bin', 'rb+') as notFoundFile:
                            notFoundData = notFoundFile.read()
                            notFoundData = notFoundData.decode('utf-8')
                            notFoundData = str(notFoundData)
                            
                        newRow = row[typeField] + "," + row['Year'] + "," + row['Spot'] + "," + row['Start'] + "," + row[timeField] + "," + row['End']
                        if newRow not in notFoundData:
                            with open('notFound.bin', 'ab+') as notFoundFile:                            
                                notFoundFile.write(newRow.encode('utf-8'))
                                notFoundFile.write('|'.encode('utf-8'))
                    
                    except urllib.error.HTTPError:
                        print("The website appers to be offline.")
                        if controlWebSite < 5:
                            print("Trying to reconnet. Attempt ", controlWebSite, " of 5.")
                            time.sleep(60)
                            downloadImages()
                        
                        else:
                            print("The website is offline. Try to run the script again in a few minutes.")

                        
                    with open(controlFile, 'ab+') as controlFileW:
                        controlFileW.write(continuumFlare.encode('utf-8'))
                        controlFileW.write('|'.encode('utf-8'))
                    
                # Downloading images on AIA 1600 -------------------------------------------- 
                sixteenHundredFlare = currentFlare + "A16"
                if sixteenHundredFlare in data:
                    existingImages += 1
                    
                elif sixteenHundredFlare not in data:
                    try: 
                        print("------ AIA1600 IMAGE DOWNLOAD --------")
                        da = 'aia.lev1_uv_24s['+dateFlare+'_'+listTime+'/30m@30m][1600]'
                        da = da.replace(" ", "") # Removes blank spaces
                        r = c.export(da, method='url', protocol='fits')
                        r.wait()
                        r.status
                        r.request_url

                        if 'X' in row[typeField]: 
                            r.download(aia1600 + '/x')
                            
                        elif 'M' in row[typeField]:
                            r.download(aia1600 + '/m')
                        
                        elif 'C' in row[typeField]:
                            r.download(aia1600 + '/c')
                            
                        elif 'B' in row[typeField]:
                            r.download(aia1600 + '/b')
                        
                        aiaSixImages += 1
                        
                        with open(controlFile, 'ab+') as controlFileW:
                            controlFileW.write(sixteenHundredFlare.encode('utf-8'))
                            controlFileW.write('|'.encode('utf-8'))
                            
                    except drms.DrmsExportError:
                         print("Current image doesn't have records online. It can't be downloaded.")
                         with open('notFound.bin', 'rb+') as notFoundFile:                     
                            notFoundData = notFoundFile.read()
                            notFoundData = notFoundData.decode('utf-8')
                            notFoundData = str(notFoundData)
                            
                         newRow = row[typeField] + "," + row['Year'] + "," + row['Spot'] + "," + row['Start'] + "," + row[timeField] + "," + row['End']
                         if newRow not in notFoundData:
                            with open('notFound.bin', 'ab+') as notFoundFile:                            
                                notFoundFile.write(newRow.encode('utf-8'))
                                notFoundFile.write('|'.encode('utf-8'))
                            # notFoundRow = csv.DictReader(notFoundFile)
                            # for notFoundRow in notFoundRow:
                            #     if row not in notFoundRow:
                            #         notFound = open('notFound.csv', 'a', newline='')     
                            #         write = csv.DictWriter(notFound, fieldnames) # Path to write on the file
                            #         write.writerow({'Type': row['Type'], 'Year': row['Year'], 'Spot': row['Spot'], 'Start': row['Start'], 'Max': row['Max'], 'End': row['End']})
                            #         notFound.close 
                            
                    except urllib.error.HTTPError:
                        print("The website appers to be offline.")
                        if controlWebSite < 5:
                            print("Trying to reconnet. Attempt ", controlWebSite, " of 5.")
                            time.sleep(60)
                            downloadImages()
                        
                        else:
                            print("The website is offline. Try to run the script again in a few minutes.")
                            
                # Downloading images on AIA 1700 -------------------------------------------- 
                seventeenHundredFlare = currentFlare + "A17"
                if seventeenHundredFlare in data:
                    existingImages += 1
                    
                elif seventeenHundredFlare not in data:  
                    try:
                        print("------ AIA1700 IMAGE DOWNLOAD --------")
                        daia = 'aia.lev1_uv_24s['+dateFlare+'_'+listTime+'/30m@30m][1700]'
                        daia = daia.replace(" ", "")    #Removes blank spaces
                        r = c.export(daia, method='url', protocol='fits')
                        
                        r.wait()
                        r.status
                        r.request_url
        
                        if 'X' in row[typeField]: 
                            r.download(aia1700 + '/x')
                            
                        elif 'M' in row[typeField]:
                            r.download(aia1700 + '/m')
                        
                        elif 'C' in row[typeField]:
                            r.download(aia1700 + '/c')
                            
                        elif 'B' in row[typeField]:
                            r.download(aia1700 + '/b')
                        
                        aiaSevenImages += 1
                        
                        with open(controlFile, 'ab+') as controlFileW:
                            controlFileW.write(seventeenHundredFlare.encode('utf-8'))
                            controlFileW.write('|'.encode('utf-8'))
                            
                    except drms.DrmsExportError:
                          print("Current image doesn't have records online. It can't be downloaded.")
                          with open('notFound.bin', 'rb+') as notFoundFile:                     
                            notFoundData = notFoundFile.read()
                            notFoundData = notFoundData.decode('utf-8')
                            notFoundData = str(notFoundData)
                            
                          newRow = row[typeField] + "," + row['Year'] + "," + row['Spot'] + "," + row['Start'] + "," + row[timeField] + "," + row['End']
                          if newRow not in notFoundData:
                              with open('notFound.bin', 'ab+') as notFoundFile:                            
                                  notFoundFile.write(newRow.encode('utf-8'))
                                  notFoundFile.write('|'.encode('utf-8'))
                                  
                    except urllib.error.HTTPError:
                        print("The website appers to be offline.")
                        if controlWebSite < 5:
                            print("Trying to reconnet. Attempt ", controlWebSite, " of 5.")
                            time.sleep(60)
                            downloadImages()
                        
                        else:
                            print("The website is offline. Try to run the script again in a few minutes.")
                            
                          # with open('notFound.csv', 'r') as notFoundFile:
                          #   notFoundRow = csv.DictReader(notFoundFile)
                          #   for notFoundRow in notFoundRow:
                          #       if row not in notFoundRow:
                          #           notFound = open('notFound.csv', 'a', newline='')     
                          #           write = csv.DictWriter(notFound, fieldnames) # Path to write on the file
                          #           write.writerow({'Type': row['Type'], 'Year': row['Year'], 'Spot': row['Spot'], 'Start': row['Start'], 'Max': row['Max'], 'End': row['End']})
                          #           notFound.close   
                        
    totalImages = aiaSevenImages + aiaSixImages + continuumImages
    print("Download complete!")
    print("\n\n ----------------------------------------------------- ")
    print("Total of images downloaded: ", totalImages)
    print("HMI Continuum images: ", continuumImages)
    print("AIA 1600 images: ", aiaSixImages)
    print("AIA 1700 images: ", aiaSevenImages)
    print(existingImages, "weren't downloaded to avoid duplication.")
    
def convertImages():
    print("------- Converting FITS to PNG ------- ")
    path = directory + os.sep + continuum + os.sep + 'x/' 
    controlWave = 1 # 1 - continuum, 2 - aia1600, 3 - aia1700
    controlType = 'x'
    global fitsFiles
    global pngFiles
    global fitsConverted
    control = 0
        
    while controlWave != 4:
        if controlWave == 1:
            files = listdir(path)
            wave = continuum
            vmin, vmax = float(40000), float(80000)
            controlType == 'x'
            fitsConverted = 0
            fitsFiles = 0
            pngFiles = 0
            print("Converting ", wave, " images.")
            
        if controlWave == 2:
            wave = aia1600
            files = listdir(path)
            vmin, vmax = float(0), float(1113)
            controlType == 'x'
            fitsConverted = 0
            fitsFiles = 0
            pngFiles = 0
            print("Converting ", wave, " images.")
            
        if controlWave == 3:
            wave = aia1700
            files = listdir(path)
            vmin, vmax = float(0), float(1113)
            controlType == 'x'
            fitsConverted = 0
            fitsFiles = 0
            pngFiles = 0
            print("Converting ", wave, " images.")
            
        if controlType == 'x':
            path = directory + os.sep + wave + os.sep + controlType
            
        if controlType == 'm':
            path = directory + os.sep + wave + os.sep + controlType
    
        if controlType == 'c':
            path = directory + os.sep + wave + os.sep + controlType
            
        if controlType == 'b':
            path = directory + os.sep + wave + os.sep + controlType
        
        # files = listdir(path)
        newPath = path + os.sep + "*.fits"
        # print("NEW", newPath)
        # print(glob.glob(newPath))
        for file in glob.glob(newPath):
            # if "fits" in file: 
            fitsFiles += 1
                
        
        if fitsFiles != 0:
            print("Fits to convert:" ,fitsFiles)
            print("Converting images " + wave + " type ", controlType, "to PNG.")
            print("This can take some time. Please, wait.")
            
            # convertToPNG(path, wave, controlType, vmax, vmin, True)
            newPath = path + os.sep + "*.fits"
            for file in glob.glob(newPath):
                # if controlValue == False:
                #     for i in [i for i, x in enumerate(files) if x == 1]:
                #         if i == fitsConverted:
                #             imagePath = directory + os.sep + wave + os.sep + controlType + os.sep + file
                #     # if "fits" in file.index(fitsConverted):
                #     #     imagePath = directory + os.sep + wave + os.sep + controlType + os.sep + file 
                # else: 
                # if "fits" in file:
                # imagePath = directory + os.sep + wave + os.sep + controlType + os.sep + file 
                hdulist = fits.open(file, ignore_missing_end=True)
                hdulist.verify('fix')
                imagem = hdulist[1].data
                np.warnings.filterwarnings('ignore')
            
                # Clip data to brightness limits
                imagem[imagem > vmax] = vmax
                imagem[imagem < vmin] = vmin
                # Scale data to range [0, 1] 
                imagem = (imagem - vmin)/(vmax - vmin)
                # Convert to 8-bit integer  
                imagem = (255*imagem).astype(np.uint8)
                # Invert y axis
                imagem = imagem[::-1, :]
                
                # Create image from data array and save as png
                image = Image.fromarray(imagem)
                destino = file[:-5] + '.png'
                image.save(destino)
                fitsConverted += 1
                control += 1
                print(fitsConverted,"/",fitsFiles)
                
            # Move image to png folders
            
            newPath = path + os.sep + "*.png"
            for file in glob.glob(newPath):
                file = file.replace(path, "")
                file = file.replace(os.sep, "")
                imagePath = directory + os.sep + wave + os.sep + controlType + os.sep + file

                pngFolder = directory + os.sep + wave + os.sep + 'png' + os.sep + controlType + os.sep + file
                shutil.move(imagePath, pngFolder)
                pngFiles += 1
                control += 1
        
        if fitsConverted + pngFiles == control:
            
            if controlType == 'x':     
                controlType = 'm'
                fitsConverted = 0
                fitsFiles = 0
                pngFiles = 0
                control = 0
                
            elif controlType == 'm':
                controlType = 'c'
                fitsConverted = 0
                fitsFiles = 0
                pngFiles = 0
                control = 0
            
            elif controlType == 'c':
                controlType = 'b'
                fitsConverted = 0
                fitsFiles = 0
                pngFiles = 0
                control = 0
                
            elif controlType == 'b':
                controlType = 'x'
                controlWave += 1
                fitsConverted = 0
                fitsFiles = 0
                pngFiles = 0
                control = 0
        
        elif fitsFiles == 0:
            if controlType == 'b':
                controlType = 'x'
                controlWave += 1
                fitsConverted = 0
                fitsFiles = 0
                pngFiles = 0
                control = 0
                        
            elif controlType == 'x':
                controlType = 'm'
                fitsConverted = 0
                fitsFiles = 0
                pngFiles = 0
                control = 0
                
            elif controlType == 'm':
                controlType = 'c'
                fitsConverted = 0
                fitsFiles = 0
                pngFiles = 0
                control = 0
                
            elif controlType == 'c':
                controlType = 'b'
                fitsConverted = 0
                fitsFiles = 0
                pngFiles = 0
                control = 0

  
try:
    
    flareFile = sys.argv[1] 
    validDataFile = flareFile[:-4] + 'valid.csv'
    operation = sys.argv[2]
    print(operation)
    
    directory = (os.path.dirname(os.path.realpath(__file__)))   #Get currently directory 
    
    while operation != '1' and operation != '2':
        operation = input("Please, insert 1 to download images or 2 to convert FITS to PNG and press ENTER: ")
    
    if operation == '1':
        print("DOWNLOAD IMAGES")
        
        # Control variables
        continuumImages = 0
        aiaSixImages = 0
        aiaSevenImages = 0
        existingImages = 0
        invalidLines = 0
        newLines = 0
        oldLines = 0
        controlWebSite = 0
        
        
        if (newLines == 0): #Verify if the output file already exists. If it don't, than create it. 
            verifyOutputFile()
    
        # Function to record only the flare infos older than 2011
        verifyDate()
    
        # Creates notFound.csv when necessary
        notFoundFlares = directory + os.sep + 'notFound.csv'
        if not os.path.exists(notFoundFlares):
            with open(notFoundFlares, 'w') as csvNotFound:
                w = csv.DictWriter(csvNotFound, fieldnames)
                w.writeheader()
                
        notFoundFlaresBin = directory + os.sep + 'notFound.bin'
        if not os.path.exists(notFoundFlaresBin):
           file = open(notFoundFlaresBin, 'wb+')
           file.close
    
        # Creates controlFile (controlDownloads.bin) when necessary 
        createFileControl = directory + os.sep + controlFile 
        if not os.path.exists(createFileControl):  
            file = open(controlFile, 'wb+')
            file.close
        
        # Creates destiny folders for the files
        if not os.path.exists(continuum):
            os.mkdir(continuum)
            os.mkdir('continuum/x')
            os.mkdir('continuum/png/x')
            os.mkdir('continuum/m')
            os.mkdir('continuum/png/m')
            os.mkdir('continuum/c')
            os.mkdir('continuum/png/c')
            os.mkdir('continuum/b')
            os.mkdir('continuum/png/b')
        
        if not os.path.exists(aia1600):
            os.mkdir(aia1600)
            os.mkdir('aia1600/x')
            os.mkdir('aia1600/png/x')
            os.mkdir('aia1600/m')
            os.mkdir('aia1600/png/m')
            os.mkdir('aia1600/c')
            os.mkdir('aia1600/png/c')
            os.mkdir('aia1600/b')
            os.mkdir('aia1600/png/b')
        
        if not os.path.exists(aia1700):
            os.mkdir(aia1700)
            os.mkdir('aia1700/x')
            os.mkdir('aia1700/png/x')
            os.mkdir('aia1700/m')
            os.mkdir('aia1700/png/m')
            os.mkdir('aia1700/c')
            os.mkdir('aia1700/png/c')
            os.mkdir('aia1700/b')
            os.mkdir('aia1700/png/b')
    
        # After all the process done correctly, everything is read to start the download
        downloadImages()
    
    if operation == '2':
        convertImages()
        
    
except IndexError:
    print("Incorrect parameters")
    print("Try: >$ python download_images.py <flare_infos.csv> <number_operation>")
    print("Number 1: Download images basead on the csv file")
    print("Number 2: Convert FITS images to PNG images")

    