"""
@author: Ana Luís Fogarin de S. Lima

    This script will read a file (.csv), classify the data in 'valid' or 'invalid' (based on the datetime)
    Data valid will be recorded in another file, that will eventually be used to download the image
    Invalid data will just be desconsidered.     
    
"""
import sys
import csv
import os

def verifyOutputFile(): 
    global validDataFile 
    
    directory = (os.path.dirname(os.path.realpath(__file__)))  #Get currently directory 
    createFile = directory + os.sep + validDataFile   #Adress of the file 

    if not os.path.exists(createFile):  #Creates the file if necessary 
        outputFile = directory + os.sep + validDataFile
        
        with open(outputFile, 'w') as csvfile:  #Write the header of the file, this way prevent replication 
            
            fieldnames = ['Type','Year','Spot','Start','Max','End'] #Using fieldnames makes it easier to put each data on the right position 
            w = csv.DictWriter(csvfile, fieldnames)       #Path to write on the file
            w.writeheader()
        
        print("Output file (" + validDataFile + ") created!")

def verifyDate():
    global addLines 
    global existLines
    global validDataFile
    global invalidLines
    
    controlE = 0 
    controlN = 0
    
    with open(solarFlareFile) as inputFile:
    #inputFile = open(solarFlareFile)
        row = csv.DictReader(inputFile) #DictReader allow do get only some specify part of the file, based on the header 
        for row in row:    
            completeRow = row #Receives the row
            dateList = row["Year"].split("-")  #Separate the column "Year" using "-" as the separation point
            year = dateList[0]                  #All the years (position 0) goes to "year"
    
            if (int(year) > 2011):                      
                #Before recording, it should verify if the row is already on the outputFile 
                readFile = open(validDataFile, 'r')
                reader = csv.DictReader(readFile)        
                for reader in reader:
                    if completeRow == reader :
                        controlE = 1
                        existLines += 1
                        
                    elif completeRow != reader:
                        controlN = 1 
                readFile.close
 
                #Recording on outputFile
                if (controlE == 0 and controlN == 1) or (controlE == 0 and controlN == 0): 
                    outputFile = open(validDataFile, 'a', newline='')     
                                
                    fieldnames = ['Type','Year','Spot','Start','Max', 'End'] #Using fieldnames makes it easier to put each data on the right position 
                    write = csv.DictWriter(outputFile, fieldnames)       #Path to write on the file
                    write.writerow({'Type': row['Type'], 'Year': row['Year'], 'Spot': row['Spot'], 'Start': row['Start'], 'Max': row['Max'], 'End': row['End']})
                    addLines += 1 
                                
                    outputFile.close         
            else:
                invalidLines += 1
                   
    print("Success on the verification!")
    messageAdd = str(addLines) + " lines were add to the file " + validDataFile + ".\n"
    messageExist =  str(existLines) + " lines already exists on the file, and weren't duplicated.\n"
    messageInvalid = str(invalidLines) + " lines were invalid and weren't add to the file."
    print(messageExist + messageAdd+ messageInvalid)  
    
try:
    solarFlareFile = sys.argv[1]
    validDataFile = sys.argv[2]
    
    invalidLines = 0
    addLines = 0
    existLines = 0
    
    if (addLines == 0): #Verify if the output file already exists. If it don't, than create it. 
        verifyOutputFile()

    verifyDate()
    
except IndexError:
    print("Incorrect parameters")
    print("Try: >$ python csv_manipulation.py <file_with_flares_informations> <file_to_record_relevant_flares>")
    