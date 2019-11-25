# -*- coding: utf-8 -*-
"""
Created on Sat Nov  17 02:07:15 2019

@author: analu

    This script will read a file (.csv), classify the data in 'valid' or 'invalid' (based on the datetime)
    Data valid will be recorded in another file, that will eventually be used to download the image
    Invalid data will just be desconsidered. 

"""
import sys
import csv


def verifyDate():
    data = csv.DictReader(file) #DictReader allow do get only some specify part of the file, based on the header 
    for data in data: 
        completeRow = data
        dateList = data["Year"].split("-")  #Separate the column "Year" using "-" as the separation point
        year = dateList[0]                  #All the years (position 0) goes to "year"
        yearInt = int(year)                 #Convert string to int to allow comparing
        if (yearInt > 2011):
            recordingFile = open(validDate, 'a', newline='') 
            
            fieldnames = ['Type','Year','Spot','Start','Max','End']
            writer = csv.DictWriter(recordingFile, fieldnames)
            writer.writerow({'Type': completeRow['Type'], 'Year': completeRow['Year'], 'Spot': completeRow['Spot'], 'Start': completeRow['Start'], 'Max': completeRow['Max']})
        
            recordingFile.close 
    print("Success on the verification!") 
    
try:
    solarFlaresInfos = sys.argv[1]
    validDate = sys.argv[2]
    
    with open(solarFlaresInfos) as file:
        verifyDate()
    
except IndexError:
    print("Incorrect parameters")
    print("Try: >$ python csv_manipulation.py <file_with_flares_informations> <file_to_record_relevant_flares>")
    
    
    
    
    
    