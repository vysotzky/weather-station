from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time 
from pprint import pprint
from collections import defaultdict 
import re
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome("C:\inzynierka\python\chromedriver.exe", options=chrome_options)

working = False

def multi_dict(K, type): 
    if K == 1: 
        return defaultdict(type) 
    else: 
        return defaultdict(lambda: multi_dict(K-1, type)) 

def getForecast(lat, long):
    global driver, working
    if working == True:
        return False
    working = True
    url = "https://www.windy.com/"+lat+"/"+long+"?"+lat+","+long+",9"
    driver.get(url)
    driver.implicitly_wait(10)

    forecast = multi_dict(2, str)

    temp_table = driver.find_element_by_xpath('//*[starts-with(@class,"td-temp")]')
    rain_table = driver.find_element_by_xpath('//*[starts-with(@class,"td-rain")]')
    wind_table = driver.find_element_by_xpath('//*[starts-with(@class,"td-wind")]')
    windDir_table = driver.find_element_by_xpath('//*[starts-with(@class,"td-windDir")]')

    temperatures = temp_table.find_elements_by_tag_name("td")
    rain = rain_table.find_elements_by_tag_name("td")
    wind = wind_table.find_elements_by_tag_name("td")
    windDir = windDir_table.find_elements_by_tag_name("td")


    for x in range(12):
        forecast[x]["temperature"] = temperatures[x].text
        forecast[x]["rain"] = rain[x].text
        forecast[x]["wind"] = wind[x].text

        # określenie kierunku wiatru
        div = windDir[x].find_element_by_tag_name("div")
        rotate = div.get_attribute("style")
        deg = int(re.findall("rotate\((.*?)deg", rotate)[0])

        if int(windDir[x].text) == 4:
            deg += 180
        
        if deg >= 360:
            deg -= 360

        forecast[x]["windDir"] = deg
    #driver.quit()
    working = False
    return(forecast)


# elem = driver.find_element_by_name("q")
# elem.clear()
# elem.send_keys("pycon")
# elem.send_keys(Keys.RETURN)