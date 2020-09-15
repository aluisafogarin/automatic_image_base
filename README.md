# Automatic Image Base

## Download Images Script

The script is developed to automatically download images from JSOC, using [drms](https://docs.sunpy.org/projects/drms/en/latest/intro.html) package. This download provides images on FITS format, so there is also the possibility to convert FITS images to PNG images.

The solar flares informations **must be** on a csv file.

The script will put the information on the correct pattern, and then start downloading the flares that are avaiable on HMI Continuum, AIA 1600 and AIA 1700. The images are downloaded on separated folders, according to the wavelength and classification of the solar falre. It is also prepared to avoid duplication of data, making a verification before start the requisition of every image.

### Syntax

> python download_images.py <flares_infos_file.csv> <operation_number>

### Operation Number

The operation number corresponds to what operation the script should do. Number 1 is used to **download images** and number 2 to **convert images to PNG.** It is important to make it clear that to the convertion process, the folder management is based on the folders created during the downloading process, and even though these operations are done separately, some errors can occur if the second one is done without the first one.

### Important

It is **essential** to provide the **date** (yyyy/mm/dd), **time** (hh:mm:ss) and **classification** (X, M, C or B) of the flare.

This following informations must be replaced on the code:

1. EMAIL - The download need a registered e-mail on JSOC Export (on [this](http://jsoc.stanford.edu/ajax/register_email.html) page).
2. fieldnames = ['Info1', '...', 'InfoN']
3. dateField = 'dateField'
4. timeField = 'timeField'
5. typeField = 'classField'

### Usefull links

Guide to SDO Data Analysis - Click [here](https://www.lmsal.com/sdodocs/doc/dcur/SDOD0060.zip/zip/entry/)

Tutorial DRMS Package - Click [here](https://docs.sunpy.org/projects/drms/en/latest/tutorial.html)  

Joint Science Operations Center (JSOC) - Click [here](http://jsoc.stanford.edu)
