import sys

# Function that extracts range from supplied string
def getRangefromStr(channRangeStr):

    ind = channRangeStr.find('-')
    # Extract start and end
    try:
        startChann = int(channRangeStr[0:ind])
        endChann = int(channRangeStr[ind+1:])
        errorCode = 0
    except:
        startChann = 0
        endChann = 0
        errorCode = 1

    # Check if end is larger than start
    if endChann-startChann < 1:
        errorCode = 1
        
    return(startChann,endChann,errorCode)