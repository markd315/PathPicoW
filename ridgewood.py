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

def bike_result():
    #req
    location = "40.701111,-73.906958"
    decoded = 'https://citymapper.com/api/3/nearby?brand_ids=CitiBike&location=' + location
    decoded += '&region_id=us-nyc&mode_id=us-nyc-citibike&limit=50&extended=1'
    r_t = urequests.get(decoded)
    for s in r_t.json()['elements']:
        if (s['id'] == 'correct'): # todo
            print(s)
            return s['cycles_manual_available'] > 0
            # also has _electric_available and cycles_available
    return False

def bikes_logic():
    pin=19
    base_trip = 4
    pwm_sel = PWM(Pin(pin, Pin.OUT))
    if(bike_result()):
        pwm_sel.freq(80000)
        pwm_sel.duty_u16(64768) # on
        return True
    else:
        pwm_sel.freq(80000)
        pwm_sel.duty_u16(0) # off
        return False

def led_flash_logic(train, minutes):
    if(train == "L"):
        pin=3
        base_trip = 3
    elif(train == "M"):
        pin=12
        base_trip = 1.5
    else: # nothing else implemented
        return
    pwm_sel = PWM(Pin(pin, Pin.OUT))
    if(minutes > base_trip+4 or minutes < base_trip):
        pwm_sel.freq(80000)
        pwm_sel.duty_u16(0) # off
        return False
    elif(minutes < base_trip+4 and minutes > base_trip+2):
        pwm_sel.freq(80000)
        pwm_sel.duty_u16(64768) # on
    elif(minutes > base_trip+1): # slow blink
        pwm_sel.freq(8)
        pwm_sel.duty_u16(52768)
    else: #(minutes > base_trip) # faint blink
        pwm_sel.freq(8)
        pwm_sel.duty_u16(2768)
    return True

def strobe_light(pwm_sel, freq):
    pwm_sel.freq(freq)
    pwm_sel.duty_u16(32768)
    

def http(station_id):
    #apiUrlEncoded = "https%3A%2F%2Fcitymapper.com%2Fapi%2F2%2Fmetrodepartures%3Fheadways%3D1%26ids%3DSubwayKosciuskoSt%26region_id%3Dus-nyc"
    #url = 'https://corsproxy.io/?' + apiUrlEncoded;
    decoded = 'https://citymapper.com/api/2/metrodepartures?headways=1&ids='
    decoded += station_id
    decoded += '&region_id=us-nyc'
    r_t = urequests.get(decoded)
    #print(r_t.status_code)
    #print(r_t.text)
    return r_t.json()

def is_to_manhattan(data, bullet):
    if 'time_seconds' not in data:
        return False
    did = data['direction_id']
    if bullet == 'M':
        return did == '1'
    else: # bullet == 'L':
        return did == '0'


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    connected = False
    while(not connected):
        try:
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            wlan.connect(secrets.new_ssid, secrets.new_passw)
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
        except Exception as e:
            print(e)
            print("Failed to set the time")
            time.sleep(20)
            pass
    print(time.localtime())
    trains = {
        "L": "SubwayMyrtleWyckoffAvs",
        "M": "SubwaySenecaAv"
    }
    while True:
        for bullet, station in trains.items():
            try:
                #print("Querying Subway API: " + bullet + " " + station)
                r = http(station)
                led.value(0)
                set_light = ""
                for s in r['stations'][0]['sections']:
                    for grp in s['departure_groupings']:
                        for data in grp['departures']:
                            #print(data)
                            if set_light == bullet:
                                continue
                            if not is_to_manhattan(data, bullet):
                                continue
                            diff_min = float(data['time_seconds']) / 60.0
                            print(str(diff_min) + " mins " + bullet + " train")
                            set_light_bool = led_flash_logic(bullet, diff_min)
                            if set_light_bool:
                                set_light = bullet
                # bikes trigger
                bikes_logic()
            except Exception as e:
                    print(e)
                    continue
                    pass
        time.sleep(10)
