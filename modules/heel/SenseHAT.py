from sense_hat import SenseHat
from time import sleep
try:
    import thread
except ImportError:
    import _thread as thread

gyro_error = 0 # poprawka do przechyłu

gyro = SenseHat()
gyro.set_imu_config(True, True, True)
orientation = None

def orientation_thread():
    global orientation
    global gyro
    while(True):
        orientation = gyro.get_orientation()

thread.start_new_thread(orientation_thread, ())

def getHeel():
    heel = int(round(orientation["pitch"], 0))
    if heel >= 180:
        heel = -1 * (360 - heel) 
    heel = heel + gyro_error
    return(heel)
