import serial 

class USB():
    def __init__(self, win):
        self.port = serial.Serial('COM3',115200)
        self.win = win

    #call before trial starts
    def WriteTrialno(self, trialNo):
        self.win.callOnFlip(self.port.write, str.encode(f"{trialNo}"))

    def WriteFrame(self):
        self.win.callOnFlip(self.port.write, str.encode(f"{255}"))

    def Close(self):
        self.port.close()

class dummyUSB(USB):
    def __init__(self, win):
        self.win = win

    def WriteTrialno(self, trialNo):
        print(f"USB would now write to EEG: {trialNo}")

    def Close(self):
        print("USB would now close")


