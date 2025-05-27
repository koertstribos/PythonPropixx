import numpy as np
import matplotlib.pyplot as plt

class NoOscillation():
    def __init__(self, **kwargs):
        self._frequency = 0
        self.framesInCycle = 1
       
    def InitialiseLookupTables(self, QObject):
        QObject.AddLumValue(1)

    @property
    def length(self):
        return 1

class Oscillation():
    def __init__(self, cycles, screenFlipFrequency = 120):
        
        self.framesInCycle = cycles[0]
        self.repsInCycle = cycles[1]

        self._frequency = 480 / self.framesInCycle * self.repsInCycle #in Hz

    def InitialiseLookupTables(self, QObject):
        #sine wave with set number of samples
        self._lookup = np.cos(self.lsp) * 0.5 + 0.5

        if QObject != None:
            for lumValue in self._lookup:
                QObject.FitLumValue(lumValue)
            
    @property
    def lsp(self):
        return np.linspace(0, self.repsInCycle * 2 * np.pi, self.framesInCycle, endpoint=False)

    def Plot(self, ax):
        ax.scatter(self.lsp/2/np.pi, self._lookup)
        
    @property
    def length(self):
        return self.framesInCycle

    def __eq__(self, other):
        try:
            return (self.framesInCycle == other.framesInCycle and self.repsInCycle == other.repsInCycle)
        except:
            return False
    
#run this to test the Oscillation class
if __name__ == "__main__":

    fig, axs = plt.subplots(3)

    osc60 = Oscillation((8,1))
    osc64 = Oscillation((15,2))
    osc68 = Oscillation((7,1))
    osc60.InitialiseLookupTables(QObject=None)
    osc64.InitialiseLookupTables(QObject=None)
    osc68.InitialiseLookupTables(QObject=None)

    osc60.Plot(axs[0])
    osc64.Plot(axs[1])
    osc68.Plot(axs[2])

    print(f"freqs: {osc60._frequency}, {osc64._frequency}, {osc68._frequency}")

    plt.show()






    