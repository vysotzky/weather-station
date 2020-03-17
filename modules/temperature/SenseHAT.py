from sense_hat import SenseHat
import os, time

sense = SenseHat()

def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))
                                                                                                                        
def getTemperature():
    cpuTemp=int(float(getCPUtemperature()))                                                                                    
    ambient = sense.get_temperature()     
    
    ## KALIBRACJA TEMPERATURY
    #  T aktualna = (T odczytana - C * T cpu) / (1 - C)    gdzie C - obliczony wspolczynnik
    C = 0.235                                                                                                           
    calctemp = (ambient - C * cpuTemp ) / (1 - C)
    calctemp = ambient - ((cpuTemp - ambient))/1.08122

    return round(calctemp)

if __name__ == "__main__":
    while 1:
        time.sleep(1)
        print(getTemperature())
        print(str(sense.get_temperature_from_pressure()) + " " + str(sense.get_temperature_from_humidity()) + " " + str(sense.get_temperature()) + " "+ str(getCPUtemperature()))
