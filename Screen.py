#Screen class for drawing of stimuli 
import numpy as np
from psychopy import event
import math
import matplotlib.pyplot as plt

try:
    #from pypixxlib.datapixx3 import DATAPixx3
    from pypixxlib.propixx import PROPixx # type: ignore
    from pypixxlib import _libdpx as dp # type: ignore
    dummy_pypixx = False
except:
    print("pypixx import unresolved")
    dummy_pypixx = True

import Oscillation 
from psychopy import visual, core
import constants

#class for linking Screen to PyPixx
class ScreenLink():
    def __init__(self):
        
        self.InitPyPixx()

    def InitPyPixx(self):
        if dummy_pypixx:
            print("pypixx dummy mode")
        else:
            self._ppx = PROPixx()
            self.StartQ4X()

        
    #time between .flip() calls (in seconds)
    #is equal to 1/120th of a second (0.008333333 seconds)        
    @property
    def flipTime(self):
        return 0.00833

    #time that actual fliptime can be off before triggering flip correction
    @property
    def flipOvertime(self):
        #return 0.0041666666666666
        return 0.01249999999999
    
    @property
    def flipTimeMs(self):
        return 8.333333333333

    def StartQ4X(self):
        self._ppx.setDlpSequencerProgram('RGB Quad 480Hz')
        self._ppx.updateRegisterCache()

    def Close(self):
        if not dummy_pypixx:
            self._ppx.setDlpSequencerProgram('RGB')
            self._ppx.updateRegisterCache()


#class for top-level screen control
class Screen(ScreenLink):
    def __init__(self, window = None):
        super().__init__()
        if window == None:
            self.win =  visual.Window(constants.DISPSIZE)
        else:
            self.win = window
            
        #get resolution
        self.winsize = self.win.size
            
        self.ClearObjects()
        
        self.ClearEndKeys()

        self._loop = False

        self.CommandKeyDebug = 'f12'
        self.debugging = False

    def AddQObject(self, qObj):
        self.qObjects.append(qObj)

    def AddObject(self, obj):
        self.objects.append(obj)

            
    def ClearEndKeys(self):
        self.endKeys = []
        event.clearEvents()

    def ClearObjects(self):
        self.qObjects = []
        self.objects = []
        
    def DrawObjects(self):
        #draw all objects with their respective tag
        for qObj in self.qObjects:
            qObj.Draw(self.frameNo)

        for obj in self.objects:
            obj.draw()

    def DrawAllSubObjs(self):
        for qObj in self.qObjects:
            qObj.DrawAll()

    def Plot(self):
        diffs = np.diff(np.array(self.frameTimeStamps))

        # Compute moving average with a window size of 10
        window_size = 10
        moving_avg = np.convolve(diffs, np.ones(window_size)/window_size, mode='valid')

        # Plot raw diffs
        plt.plot(diffs, label='Frame Duration Diffs')

        # Plot moving average (note: shorter due to convolution)
        plt.plot(range(window_size - 1, len(diffs)), moving_avg, label='Moving Avg (10)', color='orange')

        # Set y-limits and show plot
        plt.ylim(0.006, 0.01)
        plt.show()

    def AddEndCondition(self, keys):
        self.endKeys.extend(keys)

    def Show(self, duration = 9999, altFrameStart = 0):
        
        self._loop = True
        self.framesTotal = duration * 120
        self._duration = duration

        #start counting frames
        self.frameTimeStamps = []

        #draw all objects one time (first times are slowest)
        self.DrawAllSubObjs()

        self.frameNo = altFrameStart
        self.prevFlipTime = self.win.flip()

        while self._loop:
            #check if the loop should continue
            if self.BreakLoop():
                self._loop = False

            #update objects across quadrants
            self.frameNo += 1
            self.DrawObjects()
            
            #flip the screen
            self.frameTimeStamps.append(self.win.flip())

    def BreakLoop(self):
        if self.frameNo > self.framesTotal:
            return True
            
        if len(self.endKeys) > 0:
            keys = event.getKeys(keyList = self.endKeys)
            if len(keys) > 0:
                print(f"keypress {keys} detected, ending loop")
                return True

        if self.debugging:
            while True:
                core.wait(0.05)

                keys = event.getKeys(keyList = [self.CommandKeyDebug, 'left', 'right', 'c'])
                if len(keys) > 0:
                    if keys[0] == 'left':
                        self.frameNo -= 1
                        self.DrawObjects()
                        self.win.flip()
                    if keys[0] == 'right':
                        self.frameNo += 1
                        self.DrawObjects()
                        self.win.flip() 
                    if keys[0] == 'c':
                        print(f"capturing movie frame")
                        self.win.getMovieFrame()
                        self.win.saveMovieFrames(f'frame{self.frameNo}.bmp')
                    if keys[0] == self.CommandKeyDebug:
                        self.debugging = False
                        self.prevFlipTime = self.win.flip
                        self.frameNo = 0
                        self.StartQ4X()
                        break
                    
        elif len(event.getKeys(keyList = [self.CommandKeyDebug])) > 0:
            self.debugging = True
            self.frameNo = 0
            self.Close()

        return False

class EquiluminanceScreen(Screen):
    def __init__(self, window = None, flickerFreq = 30):
        super().__init__(window)

        self.flickerFreqSamples = int(math.floor((1/flickerFreq) / self.flipTime))
        self.nextFlickerFlip = self.flickerFreqSamples

        print(f"flipping every {self.flickerFreqSamples} frames")

        self._flickerFunc = None

        self._buttonFuncMapping = {}

    def DrawObjects(self): 
        super().DrawObjects()

        if self.frameNo >= self.nextFlickerFlip:
            self.nextFlickerFlip += self.flickerFreqSamples
            if hasattr(self, '_flickerFunc'):
                self._flickerFunc()

        self.DoColorFuncs()

    def DoColorFuncs(self):
        keys = event.getKeys(keyList = self.buttons)
        for key in keys:
            self._buttonFuncMapping[key]()

    def SetFlickerFunc(self, func):
        self._flickerFunc = func

    def SetColorFunc(self, button, func):
        self._buttonFuncMapping[button] = func

    @property
    def buttons(self):
        return self._buttonFuncMapping.keys()

        
        



    
        
        
    
