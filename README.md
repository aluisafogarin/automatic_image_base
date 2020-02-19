# Automatic Image Base

## Download Images Script
The script is developed to automatically download images from JSOC, using [drms](https://docs.sunpy.org/projects/drms/en/latest/intro.html) package. 

The solar flares informations **must be** on a csv file.

The script will put the information on the correct pattern, and then start downloading the flares that are avaiable on HMI Continuum, AIA 1600 and AIA 1700. It is also prepared to avoid duplication of data, making a verification before start the requisition of every image. 

### Syntax
> python download_images.py <flares_infos_file.csv> 

It is **essential** to provide the **date** (yyyy/mm/dd) and **time** (hh:mm:ss) of the wanted image. 

This following informations must be replaced on the code: 
1. EMAIL - The download need a registered e-mail on JSOC Export (on [this](http://jsoc.stanford.edu/ajax/register_email.html) page).
2. fieldnames = ['Info1', '...', 'InfoN']
3. dateField = 'dateField'
4. timeField = 'timeField'

### Usefull links 

Guide to SDO Data Analysis - Click [here](https://www.lmsal.com/sdodocs/doc/dcur/SDOD0060.zip/zip/entry/)

Tutorial DRMS Package - Click [here](https://docs.sunpy.org/projects/drms/en/latest/tutorial.html)  

Joint Science Operations Center (JSOC) - Click [here](http://jsoc.stanford.edu)

