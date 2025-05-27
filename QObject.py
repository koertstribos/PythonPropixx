from copy import deepcopy
import psychopy.tools.colorspacetools as ct
import psychopy.visual
import psychopy
import numpy as np
import Oscillation
import time
import random

class QuadrifiableStimulus():
    def __init__(self, window, type_, oscillation = None, **kwargs):
        self.win = window
        self.baseType = type_
        self.baseKwargs = kwargs

        #do position precalculations
        if 'pos' not in self.baseKwargs:
            self.baseKwargs['pos'] = (0,0)
        self._pos = self.baseKwargs['pos']

        self.fullDispsize = self.win.size

        dx, dy = self.fullDispsize[0]/2, self.fullDispsize[1]/2
        if 'anchor' not in self.baseKwargs or self.baseKwargs['anchor'] == 'center':
            self.dPoss = [[-dx/2, dy/2],[dx/2, dy/2],
                            [-dx/2,-dy/2],[dx/2,-dy/2]]
            self.poss = [self.QuadrifyPosition(self.baseKwargs['pos'], i) for i in range(4)]
        else:
            raise Exception(f"anchor {self.baseKwargs['anchor']} not supported")

        #get color arguments from dict
        if 'tagColor' in kwargs:
            self.maxColor = kwargs['tagColor']
            del kwargs['tagColor']
            #get mincolor by using HSV operation
            #get hsv from rgb
            hsv = ct.rgb2hsv(self.maxColor)
            #check if if color is not too dark
            if hsv[2] < 0.25:
                raise Exception("colour too dark for tagging")
            #lower 'value' value
            hsv[2] = 0.1
            #convert back to rgb and save as minColor
            self.minColor = ct.hsv2rgb(hsv)
        elif 'tagColors' in kwargs:
            self.maxColor = kwargs['tagColors'][0]
            self.minColor = kwargs['tagColors'][1]
            del kwargs['tagColors']
        elif 'color' in kwargs:
            self.maxColor = kwargs['color']
            self.minColor = [-1,-1,-1]
        else:
            self.maxColor = [1,1,1]
            self.minColor = [-1,-1,-1]    
        self.dColor = [fg - bg for fg, bg in zip(self.maxColor, self.minColor)]
            
        self.SetOscillation(oscillation)

    def SetOscillation(self, oscillationIn):
        #make tag
        #check if tag is an int and zero
        if (type(oscillationIn) == int and oscillationIn == 0) or oscillationIn == None:
            oscillation = Oscillation.NoOscillation()       
        #check if tag is an int
        elif type(oscillationIn) == int:
            oscillation = Oscillation.Oscillation((oscillationIn, 1), screenFlipFrequency = 120)
        #check if tag is iterable
        else:
            try: 
                iter(oscillationIn)
                oscillation = Oscillation.Oscillation(oscillationIn, screenFlipFrequency = 120)
            except Exception as e:
                print(f"type of argument oscillation ({type(oscillationIn)} with value {oscillationIn})")
                raise e
            
        self._oscillation = oscillation
        self.ResetOscillationFrames()


    def ResetOscillationFrames(self):
        self.lumVals = []
        self.lumObjs = [[],[],[],[]]
        self._oscillation.InitialiseLookupTables(self)

    #position property
    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self.SetPos(value)

    def SetPos(self, newPos):
        self.poss = [self.QuadrifyPosition(newPos, i) for i in range(4)]
        for q in range(4):
            row = self.lumObjs[q]
            for obj in row:
                obj.pos = self.poss[q]

    def QuadrifyPosition(self, pos, quadrant):
        #test for len()2
        if len(pos) != 2:
            raise Exception(f"argument {pos} not in 2D")
        res = [a + q for a,q in zip(pos, self.dPoss[quadrant])]
        #res[1] += (quadrant-2)*100
        return res
        
    def AddLumValue(self, value):
        for i in range(4):
            obj = self.baseType(self.win, **self.baseKwargs)

            if self._oscillation.framesInCycle > 1:
                self.SetColor(value, obj)
            obj.pos = self.poss[i]
            
            self.lumObjs[i].append(obj)

    def FitLumValue(self, value):
        value = np.round(value, 5) #round value to 2 decimals
        for j, repValue in enumerate(self.lumVals):
            if value == repValue:
                for i in range(4):
                    obj = self.lumObjs[i][j]
                    self.lumObjs[i].append(obj)
                return 

        #if value did not exist before, create it
        self.lumVals.append(value)
        self.AddLumValue(value)

    def SetColor(self, luminanceValue, object_):
        #calculate color by using the luminance value
        color = [minCol + (dCol * luminanceValue) for minCol, dCol in zip(self.minColor, self.dColor)]

        #gratings need to have their texture set indirectly
        if type(object_) == psychopy.visual.GratingStim:
            #set the color of the grating texture
            tex = object_.tex
            tex[:, :, 0] = color[0]
            tex[:, :, 1] = color[1]
            tex[:, :, 2] = color[2]
            object_.tex = tex
            return
        
        #set the color of the object directly
        object_.color = color

    def SetTagColor(self, color):
        self.maxColor = color
        hsv = ct.rgb2hsv(self.maxColor)
        hsv[2] = 0.25
        self.minColor = ct.hsv2rgb(hsv)
        self.dColor = [fg - bg for fg, bg in zip(self.maxColor, self.minColor)]

        self.ResetOscillationFrames()

    def SetTagColors(self, colors):
        self.maxColor = colors[0]
        self.minColor = colors[1]
        self.dColor = [fg - bg for fg, bg in zip(self.maxColor, self.minColor)]

        self.ResetOscillationFrames()

    def Draw(self, frameNo):
        l = self._oscillation.length
        startIndex = (frameNo * 4) % l

        for i in range(4):
            subI = (startIndex+i)%l
            self.lumObjs[i][subI].draw()

            # # uncomment for DebugDraw (only for GratingStim)
            # pos = self.lumObjs[i][subI].pos
            # pos = (pos[0], pos[1]-120)
            # self.DebugDraw(pos, subI)

    #DrawAll draws all objects
    #I use this because I noticed that the first time drawing an object takes a bit more time
    #this way, all objects have been drawn once, allowing for quick 
    def DrawAll(self):
        for i in range(4):
            for lumObj in self.lumObjs[i]:
                lumObj.draw()

    def DebugDraw(self, pos, text):
        pass

class QuadrifiableGrating(QuadrifiableStimulus):
    def __init__(self, window, oscillation = None, **kwargs):
        if 'tex' in kwargs and len(kwargs['tex'].shape) == 3:
            self._tex = kwargs['tex'].copy()
            del(kwargs['tex'])

        else:
            raise Exception('tex not provided')

        super().__init__(window=window, type_=psychopy.visual.GratingStim, oscillation=oscillation, **kwargs)

    def DebugDraw(self, pos, text):
        text = psychopy.visual.TextStim(self.win, text=text, pos=(pos[0], pos[1]))
        text.draw()

    def AddLumValue(self, value):

        #create tex to pass to basetype initialisation
        tex = self.CreateTex(value)

        for i in range(4):
            obj = psychopy.visual.GratingStim(self.win, tex=tex, **self.baseKwargs)
            obj.pos = self.poss[i]
            self.lumObjs[i].append(obj)


    def CreateTex(self, value): 
        x_ = self._tex.shape[1]
        y_ = self._tex.shape[0]

        tex_ = np.ones((y_, x_, 3))
        tex_[:,:,:3] = (self._tex[:,:,:3] * value) + (self._tex[:,:,3:6] * (1-value))

        return tex_

    def SetColor(self, luminanceValue, object_):
        raise Exception('unimplemented')

class QuadrifiableImage(QuadrifiableStimulus):
    def __init__(self, window, oscillation = None, **kwargs):
        if 'tex' in kwargs and len(kwargs['tex'].shape) == 3:
            self._tex = kwargs['tex'].copy()
            del(kwargs['tex'])

        else:
            raise Exception('tex not provided')

        super().__init__(window=window, type_=psychopy.visual.ImageStim, oscillation=oscillation, **kwargs)

    def AddLumValue(self, value):
        tex = self.CreateTex(value)/ 2 + 0.5

        for i in range(4):
            obj = psychopy.visual.ImageStim(self.win, image=tex, **self.baseKwargs, colorSpace='rgb1')
            obj.pos = self.poss[i]
            self.lumObjs[i].append(obj)

    def CreateTex(self, value): 
        x_ = self._tex.shape[1]
        y_ = self._tex.shape[0]

        tex = np.ones((y_, x_, 3))
        tex[:,:,:3] = (self._tex[:,:,:3] * value) + (self._tex[:,:,3:6] * (1-value))

        return tex

    def SetColor(self, luminanceValue, object_):
        raise Exception('unimplemented')
