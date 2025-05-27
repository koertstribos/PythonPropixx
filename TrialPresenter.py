import QObject, Screen, DualStim
import numpy as np
from psychopy import visual, filters
from psychopy import event, clock
import constants
import psychopy.tools.colorspacetools as ct
import matplotlib.pyplot as plt
import PinkNoise as PN
trialCount = 0
trialsMax = None
dx = 540 #pixels between two stimuli, adjust based on stereoscope x setup

def MakeMaskTex(bgCol, kwargs):
    for key, defaultValue in [['radius', 128],
                                ['sf', 0.3],
                                ['phase', 0],
                                ['ori', -45]]:
        if key not in kwargs:
            kwargs[key] = defaultValue

    scaledRadius = kwargs['radius']

    pow_ = 0
    while 2**pow_ < scaledRadius * 1.5:
        pow_ += 1

    size = 2 ** pow_

    grating = filters.makeGrating(res=size*2,
                                    cycles = 1/kwargs['sf'] * (size/scaledRadius),
                                    phase = kwargs['phase'],
                                    ori = kwargs['ori'])

    grating=np.array(grating)
    #turn grating into square grating
    #grating = np.sign(grating)


    #mask will be size (y,x,7) where last dim corresponds to (rMax,bMax,gMax,rMin,bMin,gMin,alpha)
    mask = np.ones((2 * size, 2 * size,7))

    x_start = 0
    y_start = 0

    x_end = 2 * size
    y_end = 2 * size
    
    #convert bgCol from 0:255 to -1:+1
    #bgCol = [(c - 127.5)/127.5 for c in bgCol]

    #select bg colour value nearest to -1 or +1
    index_furthest = 2
    for i in range(2):
        if abs(bgCol[i] > abs(bgCol[index_furthest])):
            index_furthest = i 

    if bgCol[index_furthest] >= 0:
        d = 1-bgCol[index_furthest]
        bgMax = [c+d for c in bgCol]
        bgMin = [c-d for c in bgCol]
    else:
        d = -1 - bgCol[index_furthest]
        bgMax = [c-d for c in bgCol]
        bgMin = [c+d for c in bgCol]

    maxCol, minCol = kwargs['tagColors']

    centrePoint = ((x_end + x_start)/2,(y_end + y_start)/2)


    random_range_alpha = 0.1
    random_range_grating = 0

    for x in range(x_start, x_end):
        for y in range(y_start, y_end):
            try:
                #calculate alpha
                #####################################
                #get distance from centre point
                dist = np.sqrt((x - centrePoint[0])**2 + (y - centrePoint[1])**2)
                #normalise distance from 0 to 1 radius ratio
                dist = dist / scaledRadius

                #random variation, nice to counteract circular patterns
                #dist = dist + ((np.random.rand()-0.5)*random_range_alpha)

                #calculate alpha value using normal distribution
                sigma = 0.4
                d_sig_sq = 2* sigma **2
                div = np.sqrt(np.pi*d_sig_sq)
                exp = -((dist**2)/d_sig_sq)
                norm = np.exp(exp)/div
                norm = np.sqrt(norm)
                #clip to 0:1 range
                if norm > 1:
                    norm = 1
                elif norm < 0:
                    norm = 0

                mask[y,x,6] = norm

                #calculate min and max Colors
                ###################################
                #use normalised (0-1) grating
                gratingValue = grating[y,x]/2+0.5

                #use gratingValue to yield 2 values: max tag-value and min tag-value. The oscillation will interpolate and oscillate between these
                tagMax = np.array([cF * gratingValue + cB * (1-gratingValue) for cF, cB in zip(maxCol, bgMax)])
                tagMin = np.array([cF * gratingValue + cB * (1-gratingValue) for cF, cB in zip(minCol, bgMin)])

                #final values are distance alpha from bgCol
                mask[y,x,:3] = tagMax * norm + bgCol * (1-norm)
                mask[y,x,3:6] = tagMin * norm + bgCol * (1-norm)
                
            except Exception as e:
                raise(Exception(f"error at {x}, {y}: {e}"))
            
    return mask

#dict for all types that are usuable in DualQuadrifiableStimuli()
dict_types = {'Circle': visual.Circle,
              'Rect': visual.Rect}


#return two QuadrifiableStimulus objects
def DualQuadrifiableStimuli(window, dualStim, tags):
    res = []
    type_ = visual.Circle

    #create two of the following
    for i in range(2):
        stim_args = dualStim.Kwargs('Grating')[i]
        tex = MakeMaskTex(window.color, stim_args)

        stim_args['size'] = tex.shape[0]
        del(stim_args['radius'])
        del(stim_args['ori'])
        del(stim_args['sf'])
        del(stim_args['phase'])

        res.append(QObject.QuadrifiableGrating(window, tex=tex, oscillation=tags[i], **stim_args))
        
    return res

dva = 2
sf = 0.3 #used to be 0.3

#fixation dimensions
armLength = 5
l = armLength
armWidth = 1
w = armWidth
#points on a fixation cross
vertices_fix =  [(-l, w), (-w, w),(-w, l),
                (w, l),  (w, -w),(l, -w),
                (l, w),  (w, w), (w, -l),
                (-w, -l),(-w,-w),(-l,-w)
                ]


def QFixations(win):
    #fixation stimuli
    fixationL = QObject.QuadrifiableStimulus(win, visual.shape.ShapeStim, vertices = vertices_fix, pos=(-dx/2,0), lineWidth = 0.05,
                                             fillColor = 'black', lineColor='black')
    fixationR = QObject.QuadrifiableStimulus(win, visual.shape.ShapeStim, vertices = vertices_fix, pos=(dx/2,0), lineWidth = 0.05, 
                                            fillColor = 'black', lineColor='black')

    return fixationL, fixationR

#rectangle dimensions
rectLineWidth = 10
lw = rectLineWidth
rectHeight = 100
h = rectHeight
rectWidth = 100
w = rectWidth

rectPoints = ((-w , h),(w,h),(w, -h),(-w, -h))

def QRects(win):
    res = []
    for pos in ((-dx/2,0), (dx/2,0)):
        for start, end, corrLW in zip(rectPoints, rectPoints[1:] + rectPoints[:1], [1, 0, -1, 0]):
            
            start = [a+b for a,b, in zip(start, pos)]
            end = [a+b for a,b, in zip(end, pos)]

            if corrLW != 0:
                start[0] -= corrLW * lw / 2
                end[0] += corrLW * lw / 2

            res.append(QObject.QuadrifiableStimulus(win, visual.line.Line, start = start, end = end, lineWidth = rectLineWidth, color = [-1,-1,-1]))

    return res

def QBack_PNoise(win):


    extraW = 40
    pinkW = w*2 + lw * 2 + extraW
    pinkH = 540

    pinkSize = [pinkH, pinkW]
    
    grating = PN.PinknoiseSG(pinkSize, -1)
    grating = np.stack((grating,) *3, axis=-1)

    print(f"grating shape: {grating.shape}")

    grating_rgba = np.ones([pinkH, pinkW, 4]) * 1
    grating_rgba[:,:,:3] = grating

    #set alpha to -1 for everything outside rectangles
    alphaVStart = int((pinkW / 2) - h - lw/2)
    alphaVEnd = int((pinkW / 2) + h + lw/2)

    alphaHStart = int(pinkH/2 - h - lw/2)
    alphaHEnd = int(pinkH/2 + h + lw/2)

    for x in range(alphaVStart, alphaVEnd):
        for y in range(alphaHStart, alphaHEnd):
            grating_rgba[y,x,3] = -1

    res = []
    for diPos in ((-dx/2,0), (dx/2,0)):
        res.append(QObject.QuadrifiableStimulus(win, type_ = visual.GratingStim,tex=grating_rgba, size=(pinkW, pinkH), pos = diPos, oscillation = None))

    return res

def QRects_SPattern(win):
    res = []
    for diPos in ((-dx/2,0), (dx/2,0)):
        gratingV = filters.makeGrating(res=h*2, cycles = 10, phase = 90, ori = 90)
        gratingH = filters.makeGrating(res=w*2, cycles = 10, phase = 90, ori = 0)

        maskV = np.ones((h*2, lw, 4))
        maskH = np.ones((lw, w*2, 4))

        for i, (mask, grating) in enumerate(zip([maskV, maskH],[gratingV, gratingH])):

            w_mask = mask.shape[1]
            h_mask = mask.shape[0]

            grating_sub = grating[:h_mask, :w_mask]

            if i == 2:
                grating_sub = np.flip(grating_sub, axis=0)
            elif i == 3:
                grating_sub = np.flip(grating_sub, axis=1)
            else:
                pass

            mask[...,0] = grating_sub
            mask[...,1] = grating_sub
            mask[...,2] = grating_sub

        gratings = []
        for mask, pos, size in zip([maskH, maskV, maskH, maskV], [(0-lw/2, h), (w, 0+lw/2), (0+lw/2, -h), (-w, 0-lw/2)], [(w*2, lw), (lw, h*2), (w*2, lw), (lw, h*2)]):
            #modulate pos by diPos
            pos = [a+b for a,b in zip(pos, diPos)]
            gratings.append(QObject.QuadrifiableStimulus(win, visual.GratingStim, tex=mask, size=size, pos=pos))

        res.extend(gratings)
    return res

redG, redB = -1, -1
blueR, blueG = -0.75, -0.75

redColorMax = [1,redG,redB]
redColorMin = [-1, -1, -1]
blueColorMax = [blueR,blueG,1]
blueColorMin = [-1,-1,-1]

currentColorStr = 'r'

luminanceValue = 0
luminanceMax = 20

#todo: implement
#show two alternating stimuli, one red and one blue
#ask participant to adjust the luminance of the red stimulus to match the blue stimulus
#return the luminance of the red stimulus
def EquiluminanceCalibration(win):
    LumScreen = Screen.EquiluminanceScreen(win, flickerFreq = 30)

    #stimuli
    squareW = 100
    squareH = 100

    squareLPos = [-dx/2,0]

    #todo: 2 squares (red and blue)
    squareR = QObject.QuadrifiableStimulus(window = LumScreen.win, type_ = visual.Rect, oscillation=(8,1),
                                               width = squareW, height = squareH, 
                                               tagColors = [redColorMin, redColorMax], 
                                               pos=squareLPos)

    squareB = QObject.QuadrifiableStimulus(window = LumScreen.win, type_ = visual.Rect, oscillation=(8,1),
                                               width = squareW, height = squareH, 
                                               tagColors = [blueColorMin, blueColorMax], 
                                               pos=squareLPos)

    lineExtraHRoom = 20
    lineStart = (squareLPos[0] - squareW/2, squareLPos[1] - squareH - lineExtraHRoom)
    lineEnd = (squareLPos[0] + squareW/2, squareLPos[1] - squareH - lineExtraHRoom)

    lineL = QObject.QuadrifiableStimulus(window = LumScreen.win, type_ = visual.line.Line,
                                            start = lineStart, end = lineEnd)

    sliderPos = [c for c in squareLPos]
    sliderPos[1] -= (squareH + lineExtraHRoom)

    slider = QObject.QuadrifiableStimulus(window = LumScreen.win, type_ = visual.Circle,
                                            size = 10, pos = [p for p in sliderPos])

    def FlickerFunc():
        global redColorMin, redColorMax, blueColorMin, blueColorMax, currentColorStr
        LumScreen.ClearObjects()

        LumScreen.AddQObject(slider)
        LumScreen.AddQObject(lineL)

        if currentColorStr == 'r':
            LumScreen.AddQObject(squareB)
            currentColorStr = 'b'
        else:
            LumScreen.AddQObject(squareR)
            currentColorStr = 'r'

    def LuminanceFunc(sign):
        global redColorMin, redColorMax, blueColorMin, blueColorMax, luminanceValue, luminanceMax, redG, redB, blueR, blueG
        
        
        luminanceValue += sign
        if luminanceValue > luminanceMax:
            luminanceValue = luminanceMax
            return
        elif luminanceValue < -luminanceMax:
            luminanceValue = -luminanceMax
            return
        
        lumScale = abs(luminanceValue / luminanceMax) * 2 #number between 0 and 2

        blueVmax = 1
        blueVmin = -1
        redVmax = 1
        redVmin = -1

        #luminanceV above 0 -> decrease blueMax, increase redMin
        if luminanceValue > 0:
            blueVmax = 1 - lumScale
            redVmin = -1 + lumScale

        #luminanceV below 0 -> decrease redMax, increase blueMin
        elif luminanceValue < 0:
            redVmax = 1 - lumScale
            blueVmin = -1 + lumScale

        blueColorMax, blueColorMin = [blueR, blueG, blueVmax], [-1, -1, blueVmin]
        redColorMax, redColorMin = [redVmax, redG, redB], [redVmin, -1, -1]

        squareR.SetTagColors([redColorMax, redColorMin])
        squareB.SetTagColors([blueColorMax, blueColorMin])

        sliderPos[0] = int(squareLPos[0] + (luminanceValue / luminanceMax * squareW)/2)
        slider.pos = [v for v in sliderPos]

    LumScreen.AddEndCondition(['escape'])
    LumScreen.SetColorFunc(button = 'left', func = lambda:LuminanceFunc(-1))
    LumScreen.SetColorFunc(button = 'right', func = lambda:LuminanceFunc(1))
    LumScreen.SetFlickerFunc(FlickerFunc)

    #add objects to screen
    LumScreen.AddQObject(squareR)
    LumScreen.AddQObject(slider)
    LumScreen.AddQObject(lineL)

    LumScreen.Show()

    print(f"colours set. red: {redColorMin[0]}<->{redColorMax[0]}. blue: {blueColorMin[2]}<->{blueColorMax[2]}")

    return luminanceValue

def Cols(char):
    global redColorMin, redColorMax, blueColorMin, blueColorMax
    if char == 'r':
        return [redColorMax, redColorMin]
    elif char == 'b':
        return [blueColorMax, blueColorMin]
    else:
        return [[0,0,0],[0,0,0]]

#Training method: show only left or right eye image, and request keypress
def Training(trialDict, screen, eeg, flipDuration = 3, flipCount = 4):
    print(f"starting training session")
    global trialCount, dx
    win = screen.win

    screen.ClearObjects()
    screen.ClearEndKeys()
    pixRadius = int(constants.DegToPix(dva))
    rectSize = int(pixRadius * 2)

    colors = [Cols(char) for char in trialDict['color']]

    #rivalrous stimuli
    dualStim = DualStim.DualStim(dX = dx, 
                                 sfs = [sf / dva for sf in [sf, sf]], #modulate sf by dva
                                 radius = pixRadius,
                                 oris = trialDict['ori'],
                                 minmaxcolors = colors, width = rectSize, height = rectSize)
    
    rivStims = DualQuadrifiableStimuli(win, dualStim, tags = trialDict['tag'])    

    #add a None object for now
    screen.AddQObject(None)

    permStims = []

    #fixation stimuli
    permStims.extend(QFixations(win))
    #rect stimuli 
    permStims.extend(QRects_SPattern(win))
    #PinkNoise
    permStims.extend(QBack_PNoise(win))

    #add objects to screen
    for obj in permStims:
        screen.AddQObject(obj)

    event.clearEvents()

    if np.sign(trialDict['ori'][0]) == -1:
        endKeys = ['lctrl', 'rctrl']
    else:
        endKeys = ['rctrl', 'lctrl']
    
    screen.win.callOnFlip(eeg.WriteTrialno, trialCount)

    for i in range(flipCount):
        #depending on rivalrous stimuli that is active at that moment, set end condition

        screen.AddEndCondition(['escape'])
        screen.AddEndCondition([endKeys[i%2]])
        screen.qObjects[0] = rivStims[i%2]

        screen.win.callOnFlip(eeg.WriteTrialno, trialCount)
        screen.Show()
        
        #end key has been pressed, show for some time
        screen.ClearEndKeys()
        screen.AddEndCondition(['escape'])
        screen.Show(duration = flipDuration, altFrameStart = screen.frameNo)

def Present(trialDict, screen, eeg, duration = 2):
    global trialCount, dx

    trialCount += 1
    print(f"starting trial where {trialDict}")
    win = screen.win

    screen.ClearObjects()
    screen.ClearEndKeys()

    pixRadius = int(constants.DegToPix(dva))
    rectSize = int(pixRadius * 2)

    
    colors = [Cols(char) for char in trialDict['color']]

    #rivalrous stimuli
    dualStim = DualStim.DualStim(dX = dx, 
                                 sfs = [sf / dva for sf in [sf, sf]], #modulate sf by dva
                                 radius = pixRadius,
                                 oris = trialDict['ori'],
                                 minmaxcolors = colors, width = rectSize, height = rectSize)
    
    stims = DualQuadrifiableStimuli(win, dualStim, tags = trialDict['tag'])    

    #fixation stimuli
    stims.extend(QFixations(win))
    #rect stimuli 
    stims.extend(QRects_SPattern(win))
    #PinkNoise
    stims.extend(QBack_PNoise(win))

    #add objects to screen
    for obj in stims:
        screen.AddQObject(obj)

    event.clearEvents()

    screen.AddEndCondition(['escape'])

    trialClock = clock.Clock()
    
    screen.win.callOnFlip(eeg.WriteTrialno, trialCount)
    screen.Show(duration = duration)
    duration = trialClock.getTime()
    keypresses = event.getKeys(keyList=['lctrl', 'rctrl'], timeStamped=trialClock)
    
    logDict = {'trialNo': trialCount, 'duration':duration, 'keypresses': keypresses}
    frameTimeStamps = screen.frameTimeStamps

    return logDict, frameTimeStamps

def ShowFixation(screen, duration = 999999, ITI = 0):
    screen.ClearEndKeys()
    screen.ClearObjects()
    win = screen.win
    
    fixationL, fixationR = QFixations(win)  

    #get position of one fixation subObject
    pos_l = fixationL.lumObjs[0][0].pos
    pos_r = fixationR.lumObjs[0][0].pos

    dy = 50

    try:
        global trialsMax 
        if trialsMax != None:
            trialsRemaining = trialsMax - trialCount

            text_l = visual.TextStim(win, text=trialsRemaining, pos=(pos_l[0], pos_l[1]+dy), color = 'black')
            text_r = visual.TextStim(win, text=trialsRemaining, pos=(pos_r[0], pos_r[1]+dy), color = 'black')

            screen.AddObject(text_l)
            screen.AddObject(text_r)
    except:
        pass

    PNl, PNr = QBack_PNoise(win)

    rects = QRects_SPattern(win)

    for obj in [*rects, fixationL, fixationR,PNl, PNr]:
        screen.AddQObject(obj)


    screen.AddEndCondition(['space'])

    screen.Show(duration = duration)

    #delay
    screen.ClearEndKeys()
    screen.Show(duration = ITI)
    screen.ClearObjects()


    
