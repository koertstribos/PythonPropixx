
import constants
from psychopy import visual, event, core, data, gui
import TrialHandler as th
import TrialPresenter as tp
from Screen import Screen
from USB import USB, dummyUSB

#only critical logging
from psychopy import logging
logging.console.setLevel(logging.CRITICAL)

EEG = True


def Main():
    #initialise window
    win = visual.Window(constants.DISPSIZE, fullscr=True, units='pix', color=[0,0,0], checkTiming=False)

    screen = Screen(win)

    #eeg
    if EEG:
        eeg = USB(win)
    else:
        eeg = dummyUSB(win)

    #initialise condition objects
    conditions = [
        th.Condition("color", ['r', 'b']),
        th.Condition("ori", [-45, 45]),
        th.Condition("tag", [(7,1), (8,1)])
    ]

    #trial stuff
    trialDuration = 120 # seconds
    nTrials = 24 # a multiple of 8, as TrialHandler has 8 different combinations ()    

    #initialise trial handler
    trialHandler = th.TrialHandler(conditions, nTrials = nTrials, nBlocks = 1)

    #generate trials
    blocks = trialHandler.GetBlocks()

    #show fixation 
    tp.ShowFixation(screen, ITI = 0)

    #do equiluminance calibration, and log the values 
    trialHandler.LogValue(trial=None, name='equiLuminanceValue', value=tp.EquiluminanceCalibration(win = win))

    #do 30 seconds of 'practice' trials where we show one stimulus at a time
    pracTrial = blocks[0][0]
    tp.ShowFixation(screen)
    tp.Training(pracTrial, screen, eeg, flipDuration=3, flipCount=5)

    #set maxTrials, which will also start counting down for the participant
    tp.trialsMax = nTrials

    for block in blocks: 
        for trial in block:
            tp.ShowFixation(screen)
            log, frameTimeStamps = tp.Present(trial, screen, eeg, duration=trialDuration)
            for key, value in log.items():
                trialHandler.LogValue(trial, key, value)
            trialHandler.LogFrameTimeStamps(trial, frameTimeStamps)

    screen.Close()
    screen.win.close()
    trialHandler.SaveCSV('trialInfo') 
    screen.Plot()

if __name__ == "__main__":
    print(f"running experiment")
    try:
        Main()
    except Exception as e:
        import resetProjectorMode
        raise e