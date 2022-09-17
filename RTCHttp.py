# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries


import time
import adafruit_requests as requests
import adafruit_espatcontrol_socket as socket
import adafruit_espatcontrol
import adafruit_espatcontrol_wifimanager
from machine import UART, Pin, PWM, RTC


# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
# Debug Level
# Change the Debug Flag if you have issues with AT commands
debugflag = False


uart = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))

print("ESP AT commands")
# For Boards that do not have an rtspin like challenger_rp2040_wifi set rtspin to False.
esp = adafruit_espatcontrol.ESP_ATcontrol(
    uart, 115200,  debug=debugflag
)

# How Long to sleep between polling
sleep_duration = 5
status_light = None
wifi = adafruit_espatcontrol_wifimanager.ESPAT_WiFiManager(esp, secrets, status_light)




print("ESP32 local time")

TIME_API = "http://worldtimeapi.org/api/ip"


the_rtc = RTC()

response = None
while True:
    try:
        print("Fetching json from", TIME_API)
        response = wifi.get(TIME_API)
        break
    except (ValueError, RuntimeError, adafruit_espatcontrol.OKError) as e:
        print("Failed to get data, retrying\n", e)
        continue

json = response.json()
current_time = json["datetime"]
the_date, the_time = current_time.split("T")
year, month, mday = [int(x) for x in the_date.split("-")]
the_time = the_time.split(".")[0]
hours, minutes, seconds = [int(x) for x in the_time.split(":")]
unixtime = json["unixtime"]


# We can also fill in these extra nice things
year_day = json["day_of_year"]
week_day = json["day_of_week"]
is_dst = json["dst"]

# now = time.time(
#     (year, month, mday, hours, minutes, seconds, week_day, year_day, is_dst)
# )

now = time.gmtime(unixtime)
print(now)
the_rtc = RTC()
the_rtc.datetime((year, month, mday, week_day,hours, minutes, seconds,  year_day))

while True:
    print(time.localtime())
    print("Sleeping for: {0} Seconds".format(sleep_duration))
    time.sleep(sleep_duration)