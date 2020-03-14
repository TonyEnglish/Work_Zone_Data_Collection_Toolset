#!/usr/bin/env python3
###
#   This function writes JavaScript variables and array into the jsfile in the format required by the
#   JavaScript for animating vehicle driven and map data collected on Google satellite view map
#
#   By J. Parikh / June, 2017
#   Initial Ver 1.0
###

###
#   Write js variables already constructed in discStr... 
###

def build_jsvars (jsfile,discStr):
    jsfile.write (discStr)
    return


###
#   Write jsarray...
###


def build_jsarray(jsfile,array,discStr):

###
#   Loop through through pathPt array, appMapPt and wzMapPt and build variables and arrays and for .js file
#   file for JavaScript
###
#   set EOL and EOA (end of Array) string for array...
###

    endStr = ""
    eolStr = ",\n"
    eoaStr = "];\n\n"

    ##print ("tot Pt: ",totDataPt)
 
###
#   Loop through the array...
###
    Kt = 0
    totDataPt = len(list(array))
    endStr = eolStr
    jsfile.write (discStr)

    while Kt <= totDataPt-1:
        if Kt == totDataPt-1:
            endStr = eoaStr

        jsfile.write (str(array[Kt])+endStr)
        Kt = Kt + 1
    return
