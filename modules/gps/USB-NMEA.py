import time
import pynmea2
import sys, os
try:
    import thread
except ImportError:
    import _thread as thread
import time

data = {}
if os.name != 'nt':
    serial = '/dev/ttyACM0'
else:
    serial = 'C:/inzynierka/nmea.txt'

def array(msg):
    return {k: getattr(msg, k) for k in msg.name_to_idx}

def read_nmea_thread():
    global data, serial
    try:
        f = open(serial)
        reader = pynmea2.NMEAStreamReader(f)
    except:
        sys.exit()

    while True:
        try:
            for msg in reader.next():
                if msg != "":
                    pass
                nmea = pynmea2.parse(str(msg))

                fields = array(nmea)
                if nmea.sentence_type == "GGA":
                    data['time'] = nmea.timestamp.strftime('%H:%I:%S')
                    data['latitude'] = nmea.latitude
                    data['longitude'] = nmea.longitude
                    data['latitude_f'] = ('%02d°%07.4f′' % (abs(nmea.latitude), nmea.latitude_minutes)) + " " + msg.lat_dir
                    data['longitude_f'] = ('%03d°%07.4f′' % (abs(nmea.longitude), nmea.longitude_minutes))  + " " + msg.lon_dir
                    
                if nmea.sentence_type == "GSV":
                    if nmea.msg_num == "1":
                        data['visible_satelites'] = {}
                    for x in map(str, range(1, 4)):
                        if fields['sv_prn_num_'+x] != "":
                            data['visible_satelites'][fields['sv_prn_num_'+x]] = {"elevation":fields['elevation_deg_'+x] , "azimuth":fields['azimuth_'+x]}
                if nmea.sentence_type == "GSA":
                    data['used_satelites'] = []
                    data['dop'] = {}
                    for key, value in fields.items():
                        if key.startswith('sv_id') and value != "":
                            data['used_satelites'].append(value)
                        if key.endswith('dop') and value != "":
                            data['dop'][key] = value
                if nmea.sentence_type == "VTG":
                    data['sog'] = str(nmea.spd_over_grnd_kts)
        except:
            pass


thread.start_new_thread(read_nmea_thread, ())

def getGPSData():
    return data