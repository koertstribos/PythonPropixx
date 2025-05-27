import random as r


class TrialHandler():
    #constructor
    #args:
    #   conditions: list of Condition objects
    #   nTrials: int, number of trials within each block
    #   nBlocks: int, number of blocks
    def __init__(self, conditions, nTrials, nBlocks):
        self.conditions = conditions
        self.nTrials = nTrials
        self.nBlocks = nBlocks

        self.trials = []
        combi = 1
        for condition in conditions:
            combi *= condition._nCombinations

        print(f"total combinations: {combi}")
        print("------------------")
        if (nTrials * nBlocks) % combi != 0:
            print(f"warning, {nTrials * nBlocks} trials is not a multiple of {combi} combinations")
        
        #a list that will keep track of which combinations have been drawn
        self._combinations = [0] * combi

    #GetTrials method
    #generates nBlocks blocks of nTrials trials
    def GetBlocks(self):
        res = []
        for _ in range(self.nBlocks):
            res.append(self.GenerateBlock())
        return res

    #GenerateBlock method
    #generates a block by calling GenerateTrial nTrials times
    def GenerateBlock(self):
        res = []
        for _ in range(self.nTrials):
            res.append(self.GenerateRandomTrial())
        return res
    
    #GenerateTrial method
    #generates a trial by drawing from each condition
    #returns: dict
    #         where each key is a condition, and value is/are the value(s) drawn from the condition
    def GenerateRandomTrial(self):

        #get indeces that contain lowest values in self._combinations
        indeces = []
        lowestval = self._combinations[0]
        for i in range(len(self._combinations)):
            if self._combinations[i] == lowestval:
                indeces.append(i)
            elif self._combinations[i] < lowestval:
                indeces = [i]
                lowestval = self._combinations[i]

        #get random index from indeces
        index = r.choice(indeces)

        #increment value at index
        self._combinations[index] += 1

        return self.GenerateTrial(index)
    
    def GenerateTrial(self, index):
        trial = {}

        conditionIndeces = []

        divisor = len(self._combinations)

        for condition in self.conditions:
            divisor //= condition._nCombinations
            subIndex = (index // divisor) % condition._nCombinations
            conditionIndeces.append(subIndex)

        for i, condition in zip(conditionIndeces, self.conditions):
            trial[condition._name] = condition.GenerateTrialVals(i)


        self.trials.append(trial)

        return trial

    def LogFrameTimeStamps(self, trial, frameTimeStamps):
        try:
            indexOf = self.trials.index(trial)
            #if index is not found, log to first trial
            if indexOf == -1:
                raise Exception("trial not found")
        except:
            indexOf = 0

        trialFileName = f"{indexOf}_frameStamps"
        with open(trialFileName, 'w') as f:
            for frameI, value in enumerate(frameTimeStamps):
                f.write(f"{frameI}:{value}")
                f.write("\n")

    #LogValue method
    #args:
    #   name: string, name of value
    #   value: string-castable, value to log
    def LogValue(self, trial, name, value):
        try:
            indexOf = self.trials.index(trial)
            #if index is not found, log to first trial
            if indexOf == -1:
                raise Exception("trial not found")
        except:
            indexOf = 0
        
        loggingTrial = self.trials[indexOf]

        #check if name is not used by any condition
        while name in loggingTrial:
            name += "_" #append underscore to name until it is unique
        
        loggingTrial[name] = value

    def SaveCSV(self, filename):
        with open(filename, 'w') as f:
            for trial in self.trials:
                [f.write(f"{key},{value} ") for key, value in trial.items()]
                f.write("\n")

            

class Condition():
    #constructor
    #args:
    #   name: string, name of condition
    #   values: list, values to draw from
    #   drawsize: int, number of (unique) values to draw from values
    def __init__(self, name, values, drawsize = None):
        if drawsize == None:
            drawsize = len(values)
        if drawsize > len(values):
            raise ValueError("drawsize must be less than the number of values")

        self._name = name
        self._values = values
        self._drawsize = drawsize

        n_combinations = 1
        n = len(values)
        while n > len(values)-drawsize: 
            n_combinations *= (n)
            n -= 1

        self._nCombinations = n_combinations
        self._combinations = [0 for _ in range(n_combinations)]
    
    #GenerateTrialVals method
    #args:
    #   index: int, index of combination to generate (used as nonrandom seed)
    #returns a list of values that are drawn from the values list
    def GenerateTrialVals(self, index):
        res = []
        #copy values list
        values = [v for v in self._values]
        combinations = len(self._combinations)
        for i in range(self._drawsize):
            #pop from values using index as superseed
            #say we sort all combinations by first value, then second, then third etc.
            #   with c combinations total
            #   index will go up to incl. c-1
            #as we are selecting from n values,
            #   we will get c/n combinations that start the same first value
            #   to get the first value, we do long division of index by c/n
            draw_in_subsort = index // (combinations // len(values))
            #take the modulo of this draw because this seems to work?
            draw_in_subsort = draw_in_subsort % len(values)
            res.append(values.pop(draw_in_subsort))
            #for the next value, the process is the same, only with c/n combinations left, and with n-1 values left
            #   to prepare for this, do c/n and n-1
            #   n-1 is taken care of by removing the value from the list (values.pop(draw_in_subsort))
            #   c/n is taken care of by the next line
            combinations = combinations // (len(values)+1)

        return res
    

if __name__ == "__main__":
    #test
    c5 = Condition("test5", ['a', 'b', 'c', 'd', 'e'], 1)
    c6 = Condition("test6", ['a', 'b', 'c'], 2)
    c4 = Condition("test4", ['a', 'b', 'c', 'd'], 1)

    th = TrialHandler([c5, c6, c4], 120, 1)

    trials = [th.GenerateTrial(i) for i in range(120)]
    for t in trials:
        print(t)

    #we expect 120 combinations, lets check them all
    #test if any combination matches
    for i in range(120):
        for j in range(120):
            if i == j:
                continue
            if trials[i] == trials[j]:
                print(f"combination {i} matches {j}")
                print(trials[i])
                print(trials[j])
                raise Exception("duplicate combination found")

    print("coding genius")


