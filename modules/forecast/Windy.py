from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time 
import os
from pprint import pprint
import re
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")

if os.name != 'nt':
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--no-proxy-server')
    driver = webdriver.Chrome('/usr/bin/chromedriver',options=chrome_options) 
else:
    driver = webdriver.Chrome("chromedriver.exe", options=chrome_options)

working = False

def getForecast(lat, long):
    global driver, working

    if working == True:
        return False
    working = True
    url = "https://www.windy.com/"+lat+"/"+long+"?"+lat+","+long+",9"
    driver.get(url)
    
    driver.implicitly_wait(10)
    time.sleep(1)

    forecast = []

    hour_table = driver.find_element_by_xpath('//*[starts-with(@class,"td-hour")]')
    temp_table = driver.find_element_by_xpath('//*[starts-with(@class,"td-temp")]')
    rain_table = driver.find_element_by_xpath('//*[starts-with(@class,"td-rain")]')
    wind_table = driver.find_element_by_xpath('//*[starts-with(@class,"td-wind")]')
    windDir_table = driver.find_element_by_xpath('//*[starts-with(@class,"td-windDir")]')

    now = driver.find_element_by_xpath("//div[@class='timecode main-timecode noselect desktop-timecode']/div")
    try:
        now = int(now.text.replace(':00', ''))
    except:
        now = int(time.strftime("%H"))

    hours = hour_table.find_elements_by_tag_name("td")
    temperatures = temp_table.find_elements_by_tag_name("td")
    rain = rain_table.find_elements_by_tag_name("td")
    wind = wind_table.find_elements_by_tag_name("td")
    windDir = windDir_table.find_elements_by_tag_name("td")

    x = 0
    day = 0
    while True:
        forecast_item = {}

        try:
            forecast_time = int(hours[x].text)
        except:
            break

        if x > 0 and int(hours[x].text) - int(hours[x-1].text) < 0:
            day = day + 1

        relative_time = day*24 + int(forecast_time) - now

        if relative_time <= -3:
            x=x+1
            continue
        if relative_time > 12:
            break

        forecast_item["delta_time"] = relative_time
        forecast_item["temperature"] = temperatures[x].text
        forecast_item["rain"] = rain[x].text
        forecast_item["wind"] = wind[x].text

        # określenie kierunku wiatru
        div = windDir[x].find_element_by_tag_name("div")
        rotate = div.get_attribute("style")
        deg = int(re.findall("rotate\((.*?)deg", rotate)[0])

        if int(windDir[x].text) == 4:
            deg += 180
        
        if deg >= 360:
            deg -= 360

        forecast_item["windDir"] = deg

        forecast.append(forecast_item)
        x = x + 1
    working = False
    return(forecast)
