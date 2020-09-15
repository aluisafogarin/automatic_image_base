"""
@author: Ana Luís Fogarin de S. Lima

"""
import sys 
import drms 
import os 
import csv

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
                # continuumFlare = currentFlare + "C" # Control flare continuum
                # if continuumFlare in data: # Verify if the image has already been downloaded
                #     existingImages += 1
                
                # elif continuumFlare not in data:  
                #     try:
                #         print("------ CONTINUUM IMAGE DOWNLOAD --------")
                #         dc = 'hmi.Ic_45s['+dateFlare +'_'+listTime+'_TAI/30m@30m]'
                #         dc = dc.replace(" ", "") # Removes blank spaces
                #         r = c.export(dc, method='url', protocol='fits')  # Using url/fits 
                #         r.wait()
                #         r.status
                #         r.request_url
                #         if 'X' in row[typeField]: 
                #             r.download(continuum + '/x')
                #             # print('Achei o tipo X')
                        
                #         elif 'M' in row[typeField]:
                #             r.download(continuum + '/m')
                #             # print('Achei o tipo M')
                        
                #         elif 'C' in row[typeField]:
                #             r.download(continuum + '/c')
                #             # print('Achei o tipo C')
                            
                #         elif 'B' in row[typeField]:
                #             r.download(continuum + '/b')
                #             # print('Achei o tipo B')
                            
                #         continuumImages += 1 
                        
                #     except drms.DrmsExportError:
                #         print("Current image doesn't have records online. It can't be downloaded.")
                #         with open('notFound.csv', 'r') as notFoundFile:
                #             reader = csv.reader(notFoundFile)
                #             for rowFile in reader:
                #                 if row not in rowFile:
                #                     notFound = open('notFound.csv', 'a', newline='')     
                #                     write = csv.DictWriter(notFound, fieldnames) # Path to write on the file
                #                     write.writerow({'Type': row['Type'], 'Year': row['Year'], 'Spot': row['Spot'], 'Start': row['Start'], 'Max': row['Max'], 'End': row['End']})
                #                     notFound.close    
                #         # Records on notFound.csv the infos of flare that couldn't be downloaded
                #         # with open('notFound.csv', 'r') as notFoundFile:
                #         #     row = csv.DictReader(notFoundFile)
                #         #     if 
                    
                #         # notFound = open('notFound.csv', 'a', newline='')     
                #         # write = csv.DictWriter(notFound, fieldnames) # Path to write on the file
                #         # write.writerow({'Type': row['Type'], 'Year': row['Year'], 'Spot': row['Spot'], 'Start': row['Start'], 'Max': row['Max'], 'End': row['End']})
                #         # notFound.close    
                        
                    # with open(controlFile, 'ab+') as controlFileW:
                    #     controlFileW.write(continuumFlare.encode('utf-8'))
                    #     controlFileW.write('|'.encode('utf-8'))
                    
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
                        # r.download(aia1600)
                        if 'X' in row[typeField]: 
                            r.download(aia1600 + '/x')
                            # print('Achei o tipo X')
                            
                        elif 'M' in row[typeField]:
                            r.download(aia1600 + '/m')
                            # print('Achei o tipo M')
                        
                        elif 'C' in row[typeField]:
                            r.download(aia1600 + '/c')
                            # print('Achei o tipo C')
                            
                        elif 'B' in row[typeField]:
                            r.download(aia1600 + '/b')
                            # print('Achei o tipo B')
                        
                        aiaSixImages += 1
                        
                        with open(controlFile, 'ab+') as controlFileW:
                            controlFileW.write(sixteenHundredFlare.encode('utf-8'))
                            controlFileW.write('|'.encode('utf-8'))
                            
                    except drms.DrmsExportError:
                         print("Current image doesn't have records online. It can't be downloaded.")
                         with open('notFound.csv', 'r') as notFoundFile:
                            reader = csv.reader(notFoundFile)
                            for rowFile in reader:
                                if row not in rowFile:
                                    notFound = open('notFound.csv', 'a', newline='')     
                                    write = csv.DictWriter(notFound, fieldnames) # Path to write on the file
                                    write.writerow({'Type': row['Type'], 'Year': row['Year'], 'Spot': row['Spot'], 'Start': row['Start'], 'Max': row['Max'], 'End': row['End']})
                                    notFound.close  
                        
                # # Downloading images on AIA 1700 -------------------------------------------- 
                # seventeenHundredFlare = currentFlare + "A17"
                # if seventeenHundredFlare in data:
                #     #print("JUMP!")
                #     existingImages += 1
                    
                # elif seventeenHundredFlare not in data:  
                #     try:
                #         print("------ AIA1700 IMAGE DOWNLOAD --------")
                #         daia = 'aia.lev1_uv_24s['+dateFlare+'_'+listTime+'/30m@30m][1700]'
                #         daia = daia.replace(" ", "")    #Removes blank spaces
                #         r = c.export(daia, method='url', protocol='fits')
                #         r.wait()
                #         r.status
                #         r.request_url
                #         # r.download(aia1700)
                #         if 'X' in row[typeField]: 
                #             r.download(aia1700 + '/x')
                #             # print('Achei o tipo X')
                            
                #         elif 'M' in row[typeField]:
                #             r.download(aia1700 + '/m')
                #             # print('Achei o tipo M')
                        
                #         elif 'C' in row[typeField]:
                #             r.download(aia1700 + '/c')
                #             # print('Achei o tipo C')
                            
                #         elif 'B' in row[typeField]:
                #             r.download(aia1700 + '/b')
                #             # print('Achei o tipo B')
                        
                #         aiaSevenImages += 1
                        
                #         with open(controlFile, 'ab+') as controlFileW:
                #             controlFileW.write(seventeenHundredFlare.encode('utf-8'))
                #             controlFileW.write('|'.encode('utf-8'))
                            
                #     except drms.DrmsExportError:
                #           print("Current image doesn't have records online. It can't be downloaded.")
                #           with open('notFound.csv', 'r') as notFoundFile:
                #             reader = csv.reader(notFoundFile)
                #             for rowFile in reader:
                #                 if row not in rowFile:
                #                     notFound = open('notFound.csv', 'a', newline='')     
                #                     write = csv.DictWriter(notFound, fieldnames) # Path to write on the file
                #                     write.writerow({'Type': row['Type'], 'Year': row['Year'], 'Spot': row['Spot'], 'Start': row['Start'], 'Max': row['Max'], 'End': row['End']})
                #                     notFound.close  
                        
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
    # flareFile = 'completesolarflares.csv'
    # validDataFile = 'completesolarflaresValid.csv'
    validDataFile = flareFile[:-4] + 'valid.csv'
    operation = sys.argv[2]
    print(operation)
    #print(validDataFile)
    
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
    
        # Creates controlFile (controlDownloads.bin) when necessary 
        createFileControl = directory + os.sep + controlFile 
        if not os.path.exists(createFileControl):  
            file = open(controlFile, 'wb+')
            file.close
        
        # Creates destiny folders for the files
        if not os.path.exists(continuum):
            os.mkdir(continuum)
            os.mkdir('continuum/x')
            os.mkdir('continuum/m')
            os.mkdir('continuum/c')
            os.mkdir('continuum/b')
        
        if not os.path.exists(aia1600):
            os.mkdir(aia1600)
            os.mkdir('aia1600/x')
            os.mkdir('aia1600/m')
            os.mkdir('aia1600/c')
            os.mkdir('aia1600/b')
        
        if not os.path.exists(aia1700):
            os.mkdir(aia1700)
            os.mkdir('aia1700/x')
            os.mkdir('aia1700/m')
            os.mkdir('aia1700/c')
            os.mkdir('aia1700/b')
    
        # After all the process done correctly, everything is read to start the download
        downloadImages()
    
    if operation == '2':
        print("CONVERTER PNG")
        #fits_image_filename = fits.util.get_testdata_filepath()
        # print (os.listdir)
        
        # Converting CONTINUUM images
        # print(directory)
        # print(glob.glob('/continuum/x/*.txt'))

        # Converting CONTINUUM images
        path = directory + os.sep + continuum + os.sep + 'x/' 
    
        controlWave = 1
        # 1 = continuum
        # 2 = aia1600
        # 3 = aia1700
        
        controlType = 'x'
        
        
        while controlWave != 4:
            # print("Entrei no while")
            if controlWave == 1:
                # print("Estou no if controlWave 1")
                files = listdir(path)
                wave = continuum
                vmin, vmax = float(40000), float(100000)
                controlType == 'x'
                i = 0
            
            if controlWave == 2:
                print("Estou no if controlWave 2")
                wave = aia1600
                files = listdir(path)
                comp = aia1600
                vmin, vmax = float(0), float(1113)
                controlType == 'x'
                i = 0
                
            if controlWave == 3:
                print("Estou no if controlWave 3")
                wave = aia1700
                files = listdir(path)
                comp = aia1700
                vmin, vmax = float(0), float(1113)
                controlType == 'x'
                i = 0
            
            if controlType == 'x':
                path = directory + os.sep + wave + os.sep + controlType
                    
            if controlType == 'm':
                path = directory + os.sep + wave + os.sep + controlType
        
            if controlType == 'c':
                path = directory + os.sep + wave + os.sep + controlType
                
            if controlType == 'b':
                path = directory + os.sep + wave + os.sep + controlType
            
            # print(path)
            files = listdir(path)
            # print(files)
            # print("Estou antes do for")
            print(len(files))
            print('Valor de i', i)
            print('Controltype ', controlType)
            
            if len(files) != 0:
                for file in files:  
                    print("ENTREI NO FOR")
                    imagePath = directory + os.sep + wave + os.sep + controlType + os.sep + file
                    hdulist = fits.open(imagePath)
                    hdulist.verify('fix')
                    imagem = hdulist[1].data
                    print(imagePath)
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
                    destino = imagePath[:-5] + '.png'
                    # destino = path + os.sep + 'png'
                    print(destino)
                    image.save(destino)
                    # print(destino)
                   
                    print('Control wave value:', controlWave)
                    print('Control type value:', controlType)
                    
                    i += 1
                    # print(i)
                    
                    if i == len(files):
                        if controlType == 'b':
                            controlType = 'x'
                            controlWave += 1
                            i = 0
                            
                        elif controlType == 'x':
                            controlType = 'm'
                            i = 0
                        
                        elif controlType == 'm':
                            controlType = 'c'
                            i = 0
                            
                        elif controlType == 'c':
                            controlType = 'b'
                            i = 0
                            
            elif len(files) == 0:
                if controlType == 'b':
                    controlType = 'x'
                    controlWave += 1
                    i = 0
                        
                elif controlType == 'x':
                    print("ENTREI NO IF")
                    controlType = 'm'
                    i = 0
                
                elif controlType == 'm':
                    controlType = 'c'
                    i = 0
                    
                elif controlType == 'c':
                    controlType = 'b'
                    i = 0
    
except IndexError:
    print("Incorrect parameters")
    print("Try: >$ python download_images.py <flare_infos.csv> <number_operation>")
    print("Number 1: Download images basead on the csv file")
    print("Number 2: Convert FITS images to PNG images")

    