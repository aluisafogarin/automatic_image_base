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

    #Create the destiny folders when necessary 
    continuum = 'continuum'
    if not os.path.exists(continuum):
        os.mkdir(continuum)
    
    aia1600 = 'aia1600'
    if not os.path.exists(aia1600):
        os.mkdir(aia1600)
    
    aia1700 = 'aia1700'
    if not os.path.exists(aia1700):
        os.mkdir(aia1700)

    #Create control file to avoid downloading twice the same image 
    directory = (os.path.dirname(os.path.realpath(__file__)))   #Get currently directory 
    createFile = directory + os.sep + 'downloadImages.csv'      #Adress of the file 

    if not os.path.exists(createFile):  #Creates the file if necessary 
        outputFile = directory + os.sep + 'downloadImages.csv'  
        
        with open(outputFile, 'w') as csvfile:  #Write the header of the file, this way prevent replication 
            
            fieldnames = ['Type','Year','Spot','Start','Max','End'] #Using fieldnames makes it easier to put each data on the right position 
            w = csv.DictWriter(csvfile, fieldnames)
            w.writeheader()


    with open(validDataFile, 'r') as inputFile:
        row = csv.DictReader(inputFile)
        for row in row:
            listDate = row['Year']
            listTime = row['Max']
            #listTime = str(listTime)
            listTime = listTime[:-3]
                   
            dc = 'hmi.Ic_45s['+listDate +'_'+listTime+'_TAI/30m@30m]'
            dc = dc.replace(" ", "") #Removes blank spaces
            r = c.export(dc, method='url', protocol='fits')  #Using url/fits 
            r.wait()
            r.status
            r.request_url
            r.download(continuum)
            
#            Downloading images on AIA 1600 and 1700 
            da = 'aia.lev1_uv_24s['+listDate+'_'+listTime+'/30m@30m][1600]'
            da = da.replace(" ", "") #Removes blank spaces
            r = c.export(da, method='url', protocol='fits')
            r.wait()
            r.status
            r.request_url
            r.download(aia1600)
            
            daia = 'aia.lev1_uv_24s['+listDate+'_'+listTime+'/30m@30m][1700]'
            daia = daia.replace(" ", "")    #Removes blank spaces
            r = c.export(daia, method='url', protocol='fits')
            r.wait()
            r.status
            r.request_url
            r.download(aia1700)
        
try:
    validDataFile = sys.argv[1]
    
    downloadImages()
    
except IndexError:
    print("Incorrect parameters")
    print("Try: >$ python download_images.py <file_with_correct_flares.csv>")









