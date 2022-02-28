# unfolding_of_sheet_metal
The script draws a flat pattern drawing of a sheet metal part.  
To apply, you need to edit the script by changing the values of the part dimensions, eccentricity and offset coefficient of the central layer of the sheet to the desired ones.  

### input block
a = 378           # internal length  
b = 278           # inner width  
d = 300           # inner diameter  
h = 250           # height  
s = 3             # metal sheet thickness  
n = 5             # number of bends per 1 angle (per 90 degree sector)  
eccentricity = 0  # eccentricity on the 'a' side  (x coordinate)  
k = 0.4           # coefficient of displacement of the central layer  
