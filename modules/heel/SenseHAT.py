from sense_hat import SenseHat
from time import sleep
try:
    import thread
except ImportError:
    import _thread as thread

error = 0

ap = SenseHat()
ap.set_imu_config(True, True, True)
orientation = None

def orientation_thread():
    global orientation
    global ap
    while(True):
        orientation = ap.get_orientation()

thread.start_new_thread(orientation_thread, ())

def getHeel():
    heel = int(round(orientation["pitch"], 0))
    if heel >= 180:
        heel = -1 * (360 - heel) 
    heel = heel + error
    return(heel)
