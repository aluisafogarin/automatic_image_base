# Automatic Image Base

## Download Images Script
The script is developed to automatically download images from Helioviewer, using [drms](https://docs.sunpy.org/projects/drms/en/latest/intro.html) package. 

The solar flares informations **must be** on a csv file.

Once the infos are on the correct pattern, the script will be able to download images on HMI Continuum, AIA 1600 and AIA 1700.

### Syntax
> python download_images.py <flares_infos.csv>

## CSV Manipulation Script 
This script converts the informations about the flares to the correct format. It is also included a verification of date. 

It is **essential** to provide: 
1. Type,
2. Year,
3. Spot,
4. Start, 
5. Max,
6. End.  

### Syntax 
> python csv_manipulation.py <input_flares_infos.csv> <output_flares_infos.csv> 

* __Input Flares Infos:__ This file must contain all informations about the solar flares;
* __Output Flares Infos:__ Doesn't need to be a file, it can be just the name wanted on the output file.
