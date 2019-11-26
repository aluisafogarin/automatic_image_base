"""
@author: Ana Luís Fogarin de S. Lima

    https://www.lmsal.com/sdodocs/doc/dcur/SDOD0060.zip/zip/entry/ 
    https://docs.sunpy.org/projects/drms/en/latest/tutorial.html
"""

import drms 
import os 
import csv
#https://pypi.org/project/PyDrive/ upload the database to gdrive 

c = drms.Client(email='a193948@dac.unicamp.br', verbose=True)   #Creating an instance of drms.Client class 

listDate = []
listTime = []
#Client.series(): method that allow the access to all data available 
#c.series(r'hmi\.m_') #First parameter is optional (regular expression to filter the result)

"""
X4.9, 2014-02-25, 1990, 00:39:00, 00:49:00, 01:03:00
X3.3, 2013-11-05, 1890, 22:07:00, 22:12:00, 22:15:00

aia.lev1_uv_24s (1600 and 1700)
hmi.Ic_* (continuum)

#aia.lev1_uv_24s[2014-02-25_00:49][1700]
r = c.export('hmi.Ic_*[2014-02-25_00:49_TAI]')
'hmi.Ic_45s[2014-02-25_00:49_TAI/30m@3m]'
r.urls.url[0]
r.download(out_dir, 0)
"""
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
    
file = csv.DictReader(open("validDate.csv","r"))
for file in file :
    listDate = file['Year']
    listTime = file['Max']
    listTime = listTime[:-3]
    
#Downloading images on HMI Continuum 
    
#c.series(r'hmi.Ic_*') To know coontinuum types of images available 
dc = 'hmi.Ic_45s['+listDate +'_'+listTime+'_TAI/30m@3m]'
dc = dc.replace(" ", "") #Removes blank spaces
#print(ds)

#Using url/fits 
r = c.export(dc, method='url', protocol='fits')    
r.wait()
r.status
r.request_url
r.download(continuum)

#Downloading images on AIA 1600 and 1700 

#/30m - pelos próximos 30 minutos @3m - uma vez a cada 3 minutos 
#ds = 'aia.lev1_uv_24s[2014-02-25_00:49/30m@3m][1600,1700]' Encontra 20 arquivos 

da = 'aia.lev1_uv_24s['+listDate+'_'+listTime+'/30m@3m][1600]'
r = c.export(da, method='url', protocol='fits')
r.wait()
r.status
r.request_url
r.download(aia1600)

daia = 'aia.lev1_uv_24s['+listDate+'_'+listTime+'/30m@3m][1700]'
r = c.export(daia, method='url', protocol='fits')
r.wait()
r.status
r.request_url
r.download(aia1700)










