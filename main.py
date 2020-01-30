from flask import Flask, render_template, request, jsonify
from collections import defaultdict 
import importlib
import threading
import os

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  
	

app = Flask(__name__, static_url_path='', 
            static_folder='gui/static',
            template_folder='gui/templates')


config_path = 'ustawienia.ini'

config = ConfigParser()
config.read(config_path)

module = {}
errors = {}
		
for k, v in config.items("modules"):
    try:
        module[k] =  importlib.import_module("modules."+k+"."+v)
    except:
        print("error: module "+v+" for "+k+" not found")
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

@app.route('/save-modules', methods=['POST']) 
def UISettingsSaveModules():
    modules = request.get_json(force=True)
    print(modules)
    return "xd"

@app.route('/index')
@app.route('/')
def index():
    return render_template('main.html', errorList = errors)
	
@app.route('/sensors')
def sensors():
    return render_template('sensors.html')

@app.route('/shutdown')
def shutdown():
    os.system("shutdown now -h") 
    return render_template('main.html')
	
@app.route('/close')
def close():
    #os.system("pkill chromium") 
    return ""

@app.route('/settings')
def settings():
    modulesList = {}
    for k, v in config.items("modules"):
        modulesList[k] =  getModules(k)
    return render_template('settings.html', moduleList = modulesList, settings = config )


def startChromium():
    os.system('chromium-browser  --kiosk --no-sandbox --test-type http://localhost/# –overscroll-history-navigation=0')
    return

def saveConfig():
    with open(config_path, 'w') as configfile:
        config.write(configfile)
    return


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    if os.name != 'nt':
        thread = threading.Thread(target = startChromium, args=[])
        thread.start()
    app.run(host= '0.0.0.0', port=int("80"))