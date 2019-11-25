# -*- coding: utf-8 -*-
"""
Created on Sat Nov  17 02:07:15 2019

@author: analu

    This script will read a file (.csv), classify the data in 'valid' or 'invalid' (based on the datetime)
    Data valid will be recorded in another file, that will eventually be used to download the image
    Invalid data will just be desconsidered. 

"""
import csv
import os 

dateList = []
validData = []

if not os.path.exists('validData'):
    os.mkdir(validData)

def verifyDate():
    data = csv.DictReader(file) #DictReader allow do get only some specify part of the file, based on the header 
    for data in data: 
        completeRow = data
        dateList = data["Year"].split("-")  #Separate the column "Year" using "-" as the separation point
        year = dateList[0]                  #All the years (position 0) goes to "year"
        yearInt = int(year)                 #Convert string to int to allow comparing
        if (yearInt > 2011):
            #with open('validDate.csv', 'w', newline='') as validFile:
            recordingFile = open('validDate.csv', 'a') 
            
            fieldnames = ['Type','Year','Spot','Start','Max','End']
            writer = csv.DictWriter(recordingFile, fieldnames=fieldnames)
            #print(completeRow)
            writer.writeheader() #VERIFICAR KEYERROR END 
            writer.writerow({'Type': completeRow['Type'], 'Year': completeRow['Year'], 'Spot': completeRow['Spot'], 'Start': completeRow['Start'], 'Max': completeRow['Max']})
        
            recordingFile.close 
            
with open('solarflares.csv') as file:
   verifyDate()
    
    
    
    
    
    
    
    