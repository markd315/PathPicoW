import time
import ntptime
from machine import Pin, I2C, PWM
import network  # handles connecting to WiFi
import urequests  # handles making and servicing network requests
import uasyncio
import os
import secrets
time.sleep(4)
i2c = I2C(0)

logfile = open('log.txt', 'a')
# duplicate stdout and stderr to the log file
os.dupterm(logfile)

led = Pin("LED", Pin.OUT)

next_train_time = -99 # TODO use this as a global somehow?

led.value(1)
#These lines just clear the MTA mode settings
led_sel = Pin(12, Pin.OUT)
led_sel.value(0)
led_sel = Pin(19, Pin.OUT)
led_sel.value(0)
pin=3
base_trip=7.5
pwm_sel = PWM(Pin(pin, Pin.OUT))


def led_flash_logic(train, minutes):
    if(minutes > base_trip+4 or minutes < base_trip):
        pwm_sel.freq(80000)
        pwm_sel.duty_u16(0) # off
        return False
    elif(minutes < base_trip+4 and minutes > base_trip+2):
        pwm_sel.freq(80000)
        pwm_sel.duty_u16(64768) # on
    elif(minutes > base_trip+1):
        pwm_sel.freq(8)
        pwm_sel.duty_u16(52768)
    else: #(minutes > base_trip)
        pwm_sel.freq(8)
        pwm_sel.duty_u16(2768)
    return True


def parse_train_arrival(ts):
    yr = int(ts[0:4])
    mo = int(ts[5:7])
    da = int(ts[8:10])
    hr = int(ts[11:13])
    mi = int(ts[14:16])
    se = int(ts[17:19])
    return time.mktime((yr, mo, da, hr, mi, se, 0, 0))

def http():
    return urequests.get("https://path.api.razza.dev/v1/stations/hoboken/realtime").json()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    connected = False
    while(not connected):
        try:
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            wlan.connect(secrets.ssid, secrets.passw)
            connected = True
        except:
            pass
    print("time (init then set)")
    print(time.localtime())
    time.sleep(1)
    failed = True
    while(failed):
        try:
            ntptime.settime()
            failed = False
        except:
            pass
    print(time.localtime())
    #r_s = urequests.get(url)
    #print(r_s.status_code)
    #print(r_s.json())
    #print("Querying PATH API:")
    
    
    while True:
        try:
            r = http()
            led.value(0)
            #print(r)
            for train in r['upcomingTrains']:
                if '33rd Street' in train['lineName']:
                    arr = parse_train_arrival(train['projectedArrival'])
                    now = time.time()
                    diff_min = float(arr - now) / 60.0
                    #diff_min += 2 # TODO REMOVE TESTING
                    next_train_time = diff_min # set global
                    print(str(diff_min) + " mins til a train")
                    if led_flash_logic('path', next_train_time):
                        break
            # Only check times every 10 seconds
            time.sleep(10)
        except:
            continue
            pass