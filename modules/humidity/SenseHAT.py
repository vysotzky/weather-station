from sense_hat import SenseHat

sense = SenseHat()

def getHumidity():
    humidity = int(sense.get_humidity())
    return(humidity)


