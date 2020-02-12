from flask import Flask, render_template, request, jsonify
from collections import defaultdict 
import importlib
import threading
import os, subprocess, sys
import json
import traceback

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  
	
# ----------------------------------------------------------- #

default_lang = 'polski'
config_path = 'settings.ini'
start_screen = 'sensors'
debug_mode = False

# ----------------------------------------------------------- #

app = Flask(__name__, static_url_path='',   
            static_folder='gui/static',
            template_folder='gui/templates')

config = ConfigParser(allow_no_value=True)
config.read(config_path, encoding='utf-8')
lang = ConfigParser(allow_no_value=True)

try:
    lang_name = config.get('general', 'language')
except:
    lang_name = default_lang

module = {}
errors = {}
for k, v in config.items("modules"):
    try:
        module[k] =  importlib.import_module("modules."+k+"."+v)
    except:
        print("error: loading module "+v+" for "+k+" failed")
        print(sys.exc_info())
        errors[k] = v


@app.route("/get-forecast/")
@app.route("/get-forecast/<lat>/<long>")
def UIGetForecast(lat = "", long = ""):
    if lat == "" and long == "":
        gps = getGPSData()
        lat = str(gps['latitude'])
        long = str(gps['longitude'])
        print(gps)
    try:
        forecast = module['forecast'].getForecast(lat, long)
        var = json.dumps(forecast)
    except:
        print(traceback.format_exc())
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

@app.route("/get-gps")
def UIGetGPSData():
    return getGPSData()

def getGPSData():
    try:
        gps = module['gps'].getGPSData()
    except:
        gps = "error"
    return  json.dumps(gps)

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

@app.route("/set-temperature-unit/<unit>")
def UISettingsSetTemperatureUnit(unit):    
    if unit == "F" or unit == "C":
        try:
            config.set("general", "temperatureUnit", unit)
            saveConfig()
        except:
            pass
    return unit

@app.route("/set-language/<lang>")
def UISettingsSetLanguage(lang):    
    global lang_name, start_screen
    if os.path.isfile('lang/'+lang+'.ini'):
        try:
            config.set("general", "language", lang)
            saveConfig()

            lang_name = lang
            loadLanguage()
            start_screen = 'settings'

            return "success"
        except:
            pass
    return "error"

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

@app.route('/gps')
def gps():
    return render_template('gps.html')

@app.route('/forecast')
def forecast():
    return render_template('forecast.html')

@app.route('/settings')
def settings():
    modulesList = {}
    for k, v in config.items("modules"):
        modulesList[k] =  getModules(k)
    return render_template('settings.html', moduleList = modulesList, ssid = getWifiName())

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


def getWifiName():
    try:
        output = str(subprocess.check_output(['iwgetid']))
        ssid = output.split('"')[1]
    except:
        ssid = False
    return ssid

def startChromium():
    os.system('chromium-browser  --kiosk --no-sandbox --test-type http://localhost/# –overscroll-history-navigation=0')
    return

def saveConfig():
    with open(config_path, 'w') as configfile:
        config.write(configfile)
    return

def getConfigOption(section, option):
        try:
            value = config.get(section, option)
        except:
            value = ""
        return value

def getLanguagesList():
        langs = []
        for file in os.listdir('lang'):
            if file.endswith(".ini"):
                langs.append(file.replace(".ini", ""))
        return langs

def getModules(name):
    modules = []
    for module in os.listdir('modules/'+name):
        if module.endswith(".py"):
            modules.append(module.replace(".py", ""))
    return modules

def loadLanguage():
    try:
        lang.read('lang/'+lang_name+'.ini', encoding='utf-8')
    except:
        pass


@app.context_processor
def utility_processor():
    def __lang(section, option):
        try:
            value = lang.get(section, option)
        except:
            value = section+"."+option
            print(value + " missing in lang "+lang_name)
        return value
    return dict(get_config=getConfigOption, get_languages = getLanguagesList,  __lang=__lang, start = start_screen)

@app.errorhandler(Exception)
def exception_handler(error):
    print(error)
    return render_template('error.html', error=error), 500


if __name__ == "__main__":
    loadLanguage()

    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    if os.name != 'nt':
        thread = threading.Thread(target = startChromium, args=[])
        thread.start()
        debug_mode = False
    app.run(host= '0.0.0.0', port=int("80"), debug=debug_mode)