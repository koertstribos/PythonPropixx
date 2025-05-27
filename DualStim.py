from psychopy.visual import filters
from psychopy import visual
import numpy as np
import constants
#a class to define dual stimuli for binocular rivalry
#define stimulus properties, and difference between the two stimuli
#class returns kwargs used in the initialisation of those stimuli

class DualStim():
    def __init__(self, **kwargs):
        self.baseKwargs = [{}, {}]

        #get position arguments from dict
        self.pos = (0,0)
        if 'pos' not in kwargs:
            print("position not provided to DualStim")
        else:
            self.centrePos = kwargs['pos']
            del kwargs['pos']
        if 'dPos' in kwargs:
            self.dPos = kwargs['dPos']
            del kwargs['dPos']
        elif 'dX' in kwargs and 'dY' in kwargs:
            self.dPos = (kwargs['dX'], kwargs['dY'])
            del kwargs['dX']
            del kwargs['dY']
        elif 'dX' in kwargs:
            self.dPos = (kwargs['dX'], 0)
            del kwargs['dX']
        elif 'dY' in kwargs:
            self.dPos = (0, kwargs['dY'])
            del kwargs['dY']
        else:
            self.dPos = (0,0)
        self.AppendBKwargs('pos', 
                           [int(p - d/2) for p,d in zip(self.pos, self.dPos)], 
                           [int(p + d/2) for p,d in zip(self.pos, self.dPos)])
        
        #get frequency arguments from dict
        if 'sfs' in kwargs:
            self.sfs = kwargs['sfs']
            del kwargs['sfs']
        else:
            self.sfs = [0.1, 0.1]
        self.AppendBKwargs('sf', self.sfs[0], self.sfs[1])
        
        #get rotation args from dict
        if 'oris' in kwargs:
            self.oris = kwargs['oris']
            del kwargs['oris']
        else:
            self.oris = [-45, 45]
        self.AppendBKwargs('ori', self.oris[0], self.oris[1])
        
        #do somethin    g with 'colors' arg if it exists
        if 'colors' in kwargs:
            colors = kwargs['colors']
            del kwargs['colors']
            self.AppendBKwargs('color', colors[0], colors[1])
        if 'minmaxcolors' in kwargs:
            colors = kwargs['minmaxcolors']
            del kwargs['minmaxcolors']
            self.AppendBKwargs('tagColors', colors[0], colors[1])

        #pass the rest of kwargs to the baseKwargs
        self.baseKwargs[0].update(kwargs)
        self.baseKwargs[1].update(kwargs)

    def AppendBKwargs(self, kw, aValue, bValue):
        self.baseKwargs[0].update({kw: aValue})
        self.baseKwargs[1].update({kw: bValue})
        
    def Kwargs(self, stimType):
        res = []
        if stimType == 'Circle':
            for kwargs in self.kwargs:
                kwCopy = {}
                #get circle constructor arguments from dicts if they exists
                for key in ['edges', 'radius ', 'units', 'color','tagColors', 'pos']:
                    if key in kwargs:
                        kwCopy[key] = kwargs[key]

                res.append(kwCopy)

        elif stimType == "Rect":
            for kwargs in self.kwargs:
                kwCopy = {}
                #get circle constructor arguments from dicts if they exists
                for key in ['width', 'height', 'units', 'color','tagColors', 'pos']:
                    if key in kwargs:
                        kwCopy[key] = kwargs[key]

                res.append(kwCopy)
            
        elif stimType == 'Grating': #don't check if stimType is a psychopy grating, as I don't use these
            for kwargs in self.kwargs:
                kwCopy = {}
                #get circle constructor arguments from dicts if they exists
                for key in ['radius', 'sf', 'phase', 'ori','tagColors', 'pos']:
                    if key in kwargs:
                        kwCopy[key] = kwargs[key]
                res.append(kwCopy)


        elif stimType == 'Fixation':
            raise Exception("unimplemented")
            for kwargs in self.kwargs:
                kwCopy = {}
                #get fixation constructor arguments from dicts if they exists
                for key in ['radius', 'units', 'color', 'pos']:
                    if key in kwargs:
                        kwCopy[key] = kwargs[key]

            
                res.append(kwCopy)


        else:
            raise Exception(f"stimType {stimType} not implemented")
        
        return res
        
    @property
    def kwargs(self):
        return self.baseKwargs
    