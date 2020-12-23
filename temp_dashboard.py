#!/usr/bin/python3
import requests
import json
from time import sleep
from Adafruit_IO import Client, Feed
import sqlite3
from datetime import datetime
import glob
import time

status = 1

# 1 wire tutorial ----
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '10*')[0] # replace string with '28*' if using DS18B20
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c #, temp_f

### Load API file
api = {}
with open('/home/pi/python/temperature_dashboard/api.txt', 'r') as file:
    for line in file:
        (key, value) = line.split()
        api[key] = value
file.close()

# Darksky weather API ----
ds_key = api['DS_KEY'] 
ds_url = api['DS_URL'] 
loc = '53.3721, -1.5489'
units = '?units=si'

ds_call =  "/".join([ds_url, ds_key, loc]) + units

def ds_get(url):
    global status, weather
    try:
        response = requests.get(url)
        print("Querying: " + ds_call)
        weather = response.json()['currently']
        aio.send(status_feed.key, status)
        status = 1
        return weather
    except:
        print("Connection error with " + ds_call)
        status = 0
        return

# Adafruit IO ----
io_key = api['IO_KEY'] 
io_username = api['IO_USER']
aio = Client(io_username, io_key)

reg_temp_feed = aio.feeds('temperature-time-series')
current_temp_feed = aio.feeds('current-temperature')
current_weather_feed = aio.feeds('current-weather')
max_temp_feed = aio.feeds('high-temp')
min_temp_feed = aio.feeds('low-temp')
status_feed = aio.feeds('status')

# Make sending IO feeds into a function with error handling
def send_all():
    global status
    try:
        aio.send(reg_temp_feed.key, read_temp())
        aio.send(current_temp_feed.key, read_temp())
        aio.send(current_weather_feed.key, weather['temperature'])
        aio.send(max_temp_feed.key, max_temp)
        aio.send(min_temp_feed.key, min_temp)
        aio.send(status_feed.key, status)
        status = 1
        print("Adafruit connection OK")
    except:
        print("Adafruit connection down")
        sleep(10)
        status = 0
        return

# Writing loop
while True:
    # sqlite
    ds_get(ds_call)
    db = sqlite3.connect('/home/pi/python/temperature_dashboard/temperature.db')
    cursor = db.cursor()
    # For database
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    cursor.execute("insert into conservatory values(?, ?, ?, ?)", (date, time, read_temp(), weather['temperature']))
    db.commit()
    # Read database values and send to Adafruit IO
    cursor.execute("select max(conservatory_temp) from conservatory where date like date('now')")
    max_temp = cursor.fetchall()[0][0]
    cursor.execute("select min(conservatory_temp) from conservatory where date like date('now')")    
    min_temp = cursor.fetchall()[0][0]
    send_all()
    db.close()
    sleep(120)
