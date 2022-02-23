from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import Image, ImageFont, ImageDraw, ImageOps
import time
import datetime
import subprocess
import json
import os
import sys
import requests


delay = 8
refresh_interval = 600 # 600 seconds- 10 minuites
ttf = 'Eight-Bit Madness.ttf'

url = "https://covid-193.p.rapidapi.com/history"

headers = {
    'x-rapidapi-key': "61c3d88f67msh4880132ba89df3fp19b8d1jsn97f2017f5fc8",
    'x-rapidapi-host': "covid-193.p.rapidapi.com"
    }

serial = i2c(port=1, address=0x3c)
device = ssd1306(serial)
font32 = ImageFont.truetype(ttf, 32)
font19 = ImageFont.truetype(ttf, 19)
font15 = ImageFont.truetype(ttf, 15)
font25 = ImageFont.truetype(ttf, 25)
font30 = ImageFont.truetype(ttf, 30)
font22 = ImageFont.truetype(ttf, 22)

def main():
    print("App started")
    started_time = time.time() - refresh_interval
    while True:
        basedir = os.path.dirname(os.path.realpath(__file__))
        icondir = os.path.join(basedir, 'icons')
        elapsed_time = time.time() - started_time
        
        try:
            if(elapsed_time >= refresh_interval):
                started_time = time.time()
                with canvas(device) as drawUpdate:
                    dlIcon = Image.open(os.path.join(icondir,  "updating.bmp"))
                    drawUpdate.bitmap((32,-6), dlIcon, fill=1)
                    drawUpdate.text((32,52), "Updating", font=font19, fill=255)
                    
                    querystring = {"country":"poland","day":datetime.datetime.now().strftime('%Y-%m-%d')}
                    response = requests.request("GET", url, headers=headers, params=querystring)
                    dane = json.loads(response.text)
                    try:
                        hour= datetime.datetime.now().hour
                        print(dane["response"][0]["cases"]["new"])
                        print(dane["response"][0]["deaths"]["new"])
                    except:
                        print("error")
                    if(hour>22):
                        device.contrast(1)
                    else:
                        if(hour>0 and hour<7):
                            device.contrast(0)
                        else:
                            device.contrast(255)
                        
                    print(hour)

                subprocess.check_output(os.path.join(basedir, 'download.sh'), shell=True)
                
                time.sleep(1) 
            
            with open(os.path.join(basedir, 'current-data.json')) as conditions_data_file:
                conditions_data = json.load(conditions_data_file)
            
            with open(os.path.join(basedir, 'forecast-data.json')) as forecast_data_file:
                forecast_data = json.load(forecast_data_file)

            city_name = conditions_data[u'name']
            temp_cur = conditions_data[u'main'][u'temp']
            icon = str(conditions_data[u'weather'][0][u'icon'])
            icon = icon[0:2]   
            humidity = conditions_data[u'main'][u'humidity']
            wind = str(conditions_data[u'wind'][u'speed'])
            wind_dir = str(conditions_data[u'wind'][u'deg'])
            epoch = int(conditions_data[u'dt'])
            utime = time.strftime('%H:%M', time.localtime(epoch))

            logo = Image.open(os.path.join(icondir,  icon + ".bmp"))
            
            
            with canvas(device) as currentWeather:
                currentWeather.bitmap((48,-6), logo, fill=1)
                currentWeather.text((0,0), city_name, font=font19, fill=255)
                currentWeather.text((0,22),  "%2.0f" % temp_cur +"°", font=font32, fill=255)
                now = datetime.datetime.now()
                currentWeather.text((0,52), now.strftime('%h') + " " + "%2d" % now.day, font=font19, fill=255)
                currentWeather.text((80,52), "%02d" % now.hour + ":" + "%02d" % now.minute, font=font19, fill=255)
                currentWeather.text((100,0),  "%2.0f" % humidity + "%", font=font15, fill=255)
            time.sleep(delay)

            for fi in range(3):
                if fi<2:
                    forecast_time_dt  = forecast_data[u'list'][fi][u'dt']
                    forecast_time     = time.strftime('%-I%p', time.localtime(forecast_time_dt))
                    forecast_temp     = forecast_data[u'list'][fi][u'main'][u'temp']
                    forecast_humidity = forecast_data[u'list'][fi][u'main'][u'humidity']
                    forecast_icon     = forecast_data[u'list'][fi][u'weather'][0][u'icon'] 
                    forecast_bmp      = Image.open(os.path.join(icondir,  forecast_icon[0:2] + ".bmp"))
                    with canvas(device) as forecastWeather:
                        forecastWeather.bitmap((48,-6), forecast_bmp, fill=1)
                        forecastWeather.text((0,0), forecast_time, font=font25, fill=255)
                        forecastWeather.text((0,22),  "%2.0f" % forecast_temp+"°", font=font32, fill=255)
                        now = datetime.datetime.now()
                        forecastWeather.text((0,52), now.strftime('%h') + " " + "%2d" % now.day, font=font19, fill=255)
                        forecastWeather.text((80,52), "%02d" % now.hour + ":" + "%02d" % now.minute, font=font19, fill=255)
                    time.sleep(delay)
                else:
                    with canvas(device) as currentWeather:
                        currentWeather.text((5,0), "CORONA", font=font25, fill=255)
                        currentWeather.text((15,15), "Infected: ", font=font19, fill=255)
                        try:
                            currentWeather.text((0,25), dane["response"][0]["cases"]["new"], font=font30, fill=255)
                        except:
                            currentWeather.text((0,25), "no data", font=font22, fill=255)
                        currentWeather.text((15,40), "Deaths: ", font=font19, fill=255)
                        
                        try:
                            currentWeather.text((0,50), dane["response"][0]["deaths"]["new"], font=font30, fill=255)
                        except:
                            currentWeather.text((0,50), "no data", font=font22, fill=255)
                        
                    time.sleep(delay)
                        
        except:
            
            for i in range(30):
                with canvas(device) as drawError:
                    dlIcon = Image.open(os.path.join(icondir,  "unknown.bmp"))
                    drawError.bitmap((32,-12), dlIcon, fill=1)
                    print("error")
                    if i % 2 == 0:
                        drawError.text((18,42), "Error occured.", font=font19, fill=255)
                    else:
                       drawError.text((28,42), "Retry in " + str(30 - i), font=font19, fill=255)
                    now = datetime.datetime.now()
                    drawError.text((0,55), now.strftime('%h') + " " + "%2d" % now.day, font=font19, fill=255)
                    drawError.text((94,55), "%02d" % now.hour + ":" + "%02d" % now.minute, font=font19, fill=255)
                    time.sleep(1)
            started_time = time.time() - refresh_interval


if __name__ == "__main__":
    main()




