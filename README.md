# Python temperature dashboard
DS18B10 temperature sensing on a Raspberry Pi, and Darksky weather posting to an Adafruit IO dashboard

## Prerequisites
* Raspberry Pi
* Python 3.x
  + Adafruit_IO python module
  + sqlite3 python module
* DS18B10 thermoprobe and 4.7K Ohm current limiting resistor (or DS18B20 with a code tweak)
* Adafruit IO account (io.adafruit.com) with the following feeds created (or rename and tweak the code)
  + 'temperature-time-series'
  + 'current-temperature'
  + 'current-weather'
  + 'high-temp'
  + 'low-temp'
  + 'status'
* Optional Dark Sky weather account (https://darksky.net/dev)

Note, Dark Sky are no longer accepting new accounts but it is easy to replace with another weather API or remove altogether.

## Preparation
Wire up the DS18B 1-wire device according to [these instructions](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing).

From the Raspberry Pi terminal run:
```
apt install sqlite3 nohup
pip install adafruit-io
pip install sqlite3
raspi-config
# Enable 1-wire devices using the advanced menu option
```
### API keys
Create a file called `api.txt` in the git folder with a key, value pair per line separated by a space. It should have the following keys in any order (fill in missing values denoted by \*):
```
DS_URL https://api.darksky.net/forecast
DS_KEY *
IO_USER *
IO_KEY *
```
This keeps API secrets separate from code. Consider changing permissions on this file for further security.

### Database
Once sqlite3 is installed a database must be created and a table created within it with the following structure. Run the following from the terminal.
```
sqlite3 temperature.db
#>> from within sqlite...
create table conservatory(
  date char(50),
  time char(50),
  conservatory_temp real,
  darksky_current_temp real)
);
.quit # Quits sqlite3
```

## Running
From the terminal in the git folder run `chmod +x temp_dashboard.py` to allow the python file to execute. Then run `nohup temp_dashboard.py &` to run the script detached from the terminal. The terminal can be closed without interrupting the script.

## Autorun from boot
Alternatively add the following line to crontab in order to run at startup:
```
crontab -e
#> Within cron...
@reboot sleep 30 && /usr/bin/python3 /home/pi/python/temperature_dashboard/temp_dashboard.py &
```

Replace the path to folder with your own. `@reboot` triggers the command to run at boot; `sleep 30` ensures that the required system daemons and services are up before the script requires them.

An alternative method is to use `systemd`. This [link](https://www.algorist.co.uk/post/resilient-systemd/) explains how to easily set it up. 

## Acknowledgements
For Adafruit IO connections
https://github.com/adafruit/Adafruit_IO_Python

For DS18B code
https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing
