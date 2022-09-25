'''
This program will take the location information from a Philippine Transfer Certificate of Title
and generate a csv file that can be imported onto google map.

USER INPUT IN THE VARIABLE BELOW,
To be taken from the land title certificate

'''
land_data = {
    'title':'TCT_XXXXXX',
    'Lot':'XXXX',
    'distances':{
        # the data below are the bearing and distance information taken from the land title
        # the format is as follow
        # from_pt1-to_pt2:(bearing,distance)
        # bearing and distance are to be taken from the land title
        'BLLM-1':('S45-08W',3624.25),
        '1-2':('S80-25W',32.26),
        '2-3':('S48-40E',1.77),
        '3-4':('N83-44E',20.15),
        '4-1':('Nxx-xxW',xx.x)
        # Note that the end_point-first_point data must be included to check if there is any
        # closure error
    },
    'coordinates':{
        # BLLM refers to the land monument with known latitude and longitude from which the
        # first lot corner was located
        # This must be in degrees, i.e. 'dd.dddd', 'dd.dddd', as per example below
        # You have to obtain this (try searching google or facebook)
        # Longitude is written first, followed by latitude
        # 
        'BLLM':(121.xxxx, 15.xxx)
    }
}


# Earth's mean radius, assuming earth is a perfect sphere
# It recommend adjusting it by trial and error until the calculated area of the lot match what is shown
# in the land title
# I am not a geodetic engineer so there could be a better way of doing this. I am open to comments
# and suggestions for improvement
# R = 6371 # km, from google search
R = 6450 # km (this seem to fit my trial lot that is at an elevation of around 30m above sea level)

# USER INPUT ENDS HERE.

# Python code that below will generate a csv file that can be imported onto google map

# Import python libraries
import re
import math
import csv

deg_per_m = 360/(math.pi * 2 * R * 1000) # deg/m
# this is the number of degrees corresponding to a meter in earth's surface, assuming earth
# is a perfect sphere. I am not a geodetic engineer so there could be a more accurate approach to 
# calculating this. Comments/suggestions are welcome

# distances is the array of survey data made to measure and record the land boundary onto the land title
distances = land_data['distances']

def dms2deg(degMinSec):
    # The parameter degMinSec is assumed to not contain the bearing information NSEW.
    # Basically, the parameter would be a string format as follow:
    # 'ddd-mm-ss' or 'ddd mm ss'
    # Remove the bearing info from the start and end of string before passing it to this function
    dms = re.split('[\s-]',degMinSec)
    index = len(dms)
    angle = float(dms[0]) # assume all will have a degree term
    if index >= 2:
        angle += float(dms[1])/60
    if index == 3:
        angle += float(dms[2])/60/60
    return angle        

def Lat_Long(f_coord, brng_dist):
    '''
    Google Map's import function of csv data requires that Latitude and Longitude coordinates are in 
    decimal degrees. I tried other format but this is the only format that works on csv file import.
    
    This function will return the Longitude and Latitude coordinates of the next point in the land
    boundary. It is calculated based on the 'from' coordinates adding the boundary bearing and distance
    to the next point.
    
    The function will return a floating point Latitude & Longitude data for the next point.
    
    'from' refers to the current point, 'to' refers to the next point
    
    The first step is to get the from point Latitude & Longitude passed to the f_coord parameter
    '''
    
    Long, Lat = f_coord # f_coord is in degrees
    # Longitude appears first followed by the Latitude, both in degrees, following google map csv
    
    # Next, we calculate the changes in Latitude & Longitude angles based on the bearing & distance
    # to the next point
    bearing, distance = brng_dist
    # bearing is in the format 'Ndd-mm.mmE', S or W can also be used. This data was input from the
    # land title.
    # distance is in meters
    
    # Note that I have not yet checked the possibility of the Latitude being negative (south of the
    # equator) and the Longitude being less than zero or greater than 360 degrees. This is something
    # to check in the future.
    NSbearing = bearing[0] # N or S
    EWbearing = bearing[(len(bearing)-1)] # E or W
    
    brng_angle = dms2deg(bearing[1:len(bearing)-1]) # remove the start and end character
    
    # Calculate the change in Longitude and Latitude to the next point.
    # Note that this is affected by the Mean Radius of the hypothetical spherical earth at the location
    # where the lot is located. This may have to be adjusted based on the elevation of the lot location
    delta_Lat = math.cos(math.radians(brng_angle))*distance * deg_per_m
    delta_Long = math.sin(math.radians(brng_angle))*distance * deg_per_m
    
    if NSbearing == 'N':
        nextLat = Lat + delta_Lat
    elif NSbearing == 'S':
        nextLat = Lat - delta_Lat
    else:
        print('Data Error!')
        
    if EWbearing == 'E':
        nextLong = Long + delta_Long
    elif EWbearing == 'W':
        nextLong = Long - delta_Long
    else:
        print('Data Error!')
        
    return (nextLong, nextLat)

# This is the MAIN program that generates the csv file to be imported to google map

# Open the csv file in write mode
filename = land_data['title']+' Lot '+land_data['Lot']+'.csv'
with open(filename, 'w') as fcsv:
    # write the header
    fcsv.write('WKT,name,description\n')
    
    # First, we need to know the coordinates of the Bureau of Land Location Monument referenced in the 
    # survey information
    # I used google to search for the BLLM coordinates referenced in the land title
    BLLM_coord = land_data['coordinates']['BLLM']
    # write the BLLM coordinates to the csv file
    fcsv.write('"POINT ('+str(BLLM_coord[0])+' '+str(BLLM_coord[1])+')",BLLM,\n')
    
    # Calculate the coordinates to the first point
    # 'BLLM-1' means BLLM to point 1 of the lot
    point1 = Lat_Long(BLLM_coord,distances['BLLM-1'])
    # write the first point
    fcsv.write('"POINT ('+str(point1[0])+' '+str(point1[1])+')",1,\n')
    
    '''
    We now have to locate point 1 of the lot boundary that is tied to the BLLM. This information is
    written as a linestring.
    '''
    fcsv.write('"LINESTRING ('+str(BLLM_coord[0])+' '+str(BLLM_coord[1])+', ')
    fcsv.write(str(point1[0])+' '+str(point1[1])+')",BLLM-1,\n')
    
    '''
    Next would be the lot boundary from point 1 to the last point and back to point 1 to close the 
    boundary. A final check would be made regarding a possible error to the survey based on the starting
    point 1 coordinate to the closing point 1 coordinate.
    
    Lot boundary is written as a polygon.
    '''
    fcsv.write('"POLYGON ((')
    
    for edge in distances:
        # distances info is taken from the dictionary of from-to nodes in the data input.
        # distance is in the format from-to string
        # parse f = from; t = to
        f,t = re.split('-',edge)

        # get the from coordinates from the land data
        f_coord = land_data['coordinates'][f]

        # get the bearing and distance to the next point
        # this is a list containing bearing and distance information
        brng_dist = distances[edge]

        # calculate the coordinate of the next point
        t_coord = Lat_Long(f_coord, brng_dist)

        # record the t_coord to the land data
        land_data['coordinates'][t] = t_coord

        if f=='BLLM':
            # This is the first point of the polygon
            # We could have used t=='1' but this would be errorneous because the last t will also be '1' 
            row = str(t_coord[0]) + ' '+str(t_coord[1])
        else:
            # This applies to all points after the first point
            row = ', '+str(t_coord[0]) + ' '+str(t_coord[1])
        # write the row to the csv file
        fcsv.write(row)
        
    # At this point, we are back to point '1'
    # the last point has been written which should be point 1 + survey error
    # Let's calculate the closure error
    errorLong = t_coord[0]-point1[0]
    errorLat = t_coord[1] - point1[1]
    distLong = abs(errorLong)/deg_per_m # meters
    distLat = abs(errorLat)/deg_per_m # meters
    errorDist = round(math.sqrt(distLong**2 + distLat**2),2)
    print('Survey closure error = ' + str(errorDist) +'m.')
    # to close the polygon and compensate for the error, write the first point 1 coordinate
    row=', '+str(point1[0])+' '+str(point1[1])+'))",Lot 1, Closure Error = '+str(errorDist)+'m!\n'
    fcsv.write(row)

# NOTE:
# At the end of the calculation, a closure error will be calculated to check the quality of the data
# I tested this program in two lots where I found that there was an error in closure
# I simply ignore the error and use the coordinate of corner #1 that was measured from the BLLM
#
# Possible sources of error could be:
# 1. Typo in preparing the TCT
# 2. Round off error in bearing data
# 3. Error in the survey measurement - not likely because the surveyor will surely check the closure
# Anyway, this is why this is for general info only - not to be taken as accurate enough
# to be a basis for boundary dispute (grin)
# Don't blame me for any erroneous use of this software - you have been warned!
