# Automatic Image Base

## Download Images Script
The script is developed to automatically download images from Helioviewer, using [drms](https://docs.sunpy.org/projects/drms/en/latest/intro.html) package. 

The solar flares informations *must be* on a csv file.

Once the infos are on the correct pattern, the script will be able to download images on HMI Continuum, AIA 1600 and AIA 1700.

## CSV Manipulation Script 
This script converts the informations about the flares to the correct format. It is also included a verification of date. 

It is *essential* to provide *Type,Year,Spot,Start,Max,End* off all flares. 

### Syntax 
> python csv_manipulation.py <file_with_flares_informations> <file_to_record_relevant_flares>
