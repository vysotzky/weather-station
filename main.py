from flask import Flask, render_template, request, jsonify
from collections import defaultdict 
import importlib
import threading
import os
import sys

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  
	

app = Flask(__name__, static_url_path='',   
            static_folder='gui/static',
            template_folder='gui/templates')


config_path = 'ustawienia.ini'

config = ConfigParser(allow_no_value=True)
config.read(config_path)

module = {}
errors = {}
		
for k, v in config.items("modules"):
    try:
        module[k] =  importlib.import_module("modules."+k+"."+v)
    except:
        print("error: loading module "+v+" for "+k+" failed")
        print(sys.exc_info())
        errors[k] = v

def multi_dict(K, type): 
    if K == 1: 
        return defaultdict(type) 
    else: 
        return defaultdict(lambda: multi_dict(K-1, type)) 

def getModules(name):
    i=0
    modules = {}
    for module in os.listdir('modules/'+name):
        if module.endswith(".py"):
            modules[i] = module.replace(".py", "")
            i+=1
    return modules

@app.route("/get-forecast/<lat>/<long>")
def UIGetForecast(lat, long):
    try:
        forecast = module['forecast'].getForecast(lat, long)
        var = str(forecast[0]["temperature"])
    except:
        var = "error"
    return var

@app.route("/get-temperature")
def UIGetTemperature():
    try:
        temperature = module['temperature'].getTemperature()
    except:
        temperature = "error"
    return str(temperature)

@app.route("/get-pressure")
def UIGetPressure():
    try:
        pressure = module['pressure'].getPressure()
    except:
        pressure = "error"
    return str(pressure)

@app.route("/get-humidity")
def UIGetHumidity():
    try:
        humidity = module['humidity'].getHumidity()
    except:
        humidity = "error"
    return str(humidity)

    
@app.route("/get-heel")
def UIGetHeel():
    try:
        heel = module['heel'].getHeel()
    except:
        heel = "error"
    return str(heel)

@app.route("/set-brightness/<brightness>")
def UISettingsSetBrightness(brightness):
    try:
        brt = int(brightness)
    except:
        brt = 150
    
    if brt >= 15 & brt <=255:
        try:
            if os.name != 'nt':
                os.system('sudo bash -c "echo '+str(brt)+'  > /sys/class/backlight/rpi_backlight/brightness"') 
            config.set("general", "brightness", str(brt))
            saveConfig()
        except:
            pass
    return str(brt)

@app.route("/set-logbook-frequency/<frequency>")
def UISettingsSetLogbookFrequency(frequency):
    try:
        freq = int(frequency)
    except:
        freq = 10
    
    if freq >= 1 & freq<=60:
        try:
            config.set("general", "logbookFrequency", str(freq))
            saveConfig()
        except:
            pass
    return str(freq)

@app.route('/save-modules', methods=['POST']) 
def UISettingsSaveModules():
    modules = request.get_json(force=True)
    try:
        config['modules'] = modules
        saveConfig()
        return "success"
    except:
        return "error"

@app.route('/index')
@app.route('/')
def index():
    return render_template('main.html', errorList = errors)
	
@app.route('/sensors')
def sensors():
    return render_template('sensors.html')

@app.route('/logbook')
def logbook():
    return render_template('logbook.html')

@app.route('/shutdown')
def shutdown():
    os.system("shutdown now -h") 
    return ""

@app.route('/reboot')
def reboot():
    os.system("reboot") 
    return ""
	
@app.route('/close')
def close():
    os.system("pkill chromium") 
    return ""

@app.route('/settings')
def settings():
    modulesList = {}
    for k, v in config.items("modules"):
        modulesList[k] =  getModules(k)
    return render_template('settings.html', moduleList = modulesList)


def startChromium():
    os.system('chromium-browser  --kiosk --no-sandbox --test-type http://localhost/# –overscroll-history-navigation=0')
    return

def saveConfig():
    with open(config_path, 'w') as configfile:
        config.write(configfile)
    return


@app.context_processor
def utility_processor():
    def get_config(section, option):
        try:
            value = config.get(section, option)
        except:
            value = ""
        return value
    return dict(get_config=get_config)

@app.errorhandler(Exception)
def exception_handler(error):
    print(error)
    return render_template('error.html', error=error), 500

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    debugMode = True
    if os.name != 'nt':
        thread = threading.Thread(target = startChromium, args=[])
        thread.start()
        debugMode = False
    app.run(host= '0.0.0.0', port=int("80"), debug=debugMode)