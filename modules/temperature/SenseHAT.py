from sense_hat import SenseHat

sense = SenseHat()

def getTemperature():
    temperature = int(sense.get_temperature())
    return(temperature)
