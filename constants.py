## This file is part of PyGaze - the open-source toolbox for eye tracking
##
##    PyGaze is a Python module for easily creating gaze contingent experiments
##    or other software (as well as non-gaze contingent experiments/software)
##    Copyright (C) 2012-2013  Edwin S. Dalmaijer
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# version: 0.4 (25-03-2013)
import math 

# MAIN
DUMMYMODE = True # False for gaze contingent display, True for dummy mode (using mouse or joystick)
LOGFILENAME = 'default' # logfilename, without path
LOGFILE = LOGFILENAME[:] # .txt; adding path before logfilename is optional; logs responses (NOT eye movements, these are stored in an EDF file!)

# DISPLAY
# used in libscreen, for the *_display functions. The values may be adjusted,
# but not the constant's names
SCREENNR = 0 # number of the screen used for displaying experiment
DISPTYPE = 'psychopy' # either 'psychopy' or 'pygame'
DISPSIZE = (960*2,540*2) # canvas sizes, multiplied by 2x2 for quad4x mode
SCREENMIDPOINT = (DISPSIZE[0]/2, DISPSIZE[1]/2)
SCREENSIZE = (48.0, 27.2) # physical display size in cm
SCREENDIST = 90 
MOUSEVISIBLE = False # mouse visibility

BGC = (0,0,0,255) # backgroundcolour
FGC = (255,255,255,255) # foregroundcolour

#CIRCLECOLOUR
CIRCLECOLOUR = (30,30,30)

INTERTIME_CHECKGAZEPOS = 1
SCREENREFRESHRATE = 480
SCREENFRAMETIME = int(1000/SCREENREFRESHRATE)

dispsize_quad = [d/2 for d in DISPSIZE]
pixPerCm = (dispsize_quad[0] / (2*SCREENSIZE[0])) + (dispsize_quad[1] / (2*SCREENSIZE[1])) 

def DegToPix(deg):
    global SCREENDIST, pixPerCm
    rad = deg / 360 * math.tau
    cm = math.tan(rad) * SCREENDIST
    return pixPerCm * cm


def PixToDeg(pix):
    global SCREENDIST, pixPerCm
    cm = pix/pixPerCm
    rad = math.atan(cm/SCREENDIST)
    deg = rad / math.tau * 360
    
    if __name__ == "__main__":
        print(f"cm: {cm}")
        print(f"rad: {rad}")
        print(f"deg: {deg}")

    return deg


#EXPERIMENT INFO
TARGETSIZE = DegToPix(10) #size of targets in pixels

FIXATIONTIME = 1000 * 60 * 2 # 2 minutes in ms
TRIALS = 1
BLOCKS = 3 #starts at 0 ...
CIRCLEPOLYGONCOUNT = 256


# INPUT
# used in libinput. The values may be adjusted, but not the constant names.
MOUSEBUTTONLIST = None # None for all mouse buttons; list of numbers for buttons of choice (e.g. [1,3] for buttons 1 and 3)
MOUSETIMEOUT = None # None for no timeout, or a value in milliseconds
KEYLIST = None # None for all keys; list of keynames for keys of choice (e.g. ['space','9',':'] for space, 9 and ; keys)
KEYTIMEOUT = 1 # None for no timeout, or a value in milliseconds
JOYBUTTONLIST = None # None for all joystick buttons; list of button numbers (start counting at 0) for buttons of choice (e.g. [0,3] for buttons 0 and 3 - may be reffered to as 1 and 4 in other programs)
JOYTIMEOUT = None # None for no timeout, or a value in milliseconds

if __name__ == "__main__":
    deg1 = DegToPix(1)
    deg10 = DegToPix(10)
    print(f"1 degree = {deg1} pixels")
    print(f"10 degrees = {deg10} pixels")
    
    print(f"1 degree = {PixToDeg(deg1)} degrees")
    print(f"10 degrees = {PixToDeg(deg10)} degrees")
   