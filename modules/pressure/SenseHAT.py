from sense_hat import SenseHat

sense = SenseHat()

def getPressure():
    pressure = int(sense.get_pressure())
    return(pressure)
