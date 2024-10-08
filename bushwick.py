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

#led_r.value(1)
#led_y.value(1)

next_train_time = -99 # TODO use this as a global somehow?

led.value(1)

def l_train_bike_result():
    #req
    #https://citymapper.com/api/3/nearby?brand_ids=CitiBike&location=40.695473,-73.926774&region_id=us-nyc&mode_id=us-nyc-citibike&limit=50&extended=1
    # TODO check the bushwick/dekalb for >2 bikes
    #CitiBike_a3d72b5b-9587-4f33-9722-c01e20a9b358
    # TODO check the stanhope/wykoff for >3 docks
    #CitiBike_f6cf3ecc-b3ad-4291-8c24-277f28f64ba1
    return True

def led_flash_logic(train, minutes):
    if(train == "L" and l_train_bike_result()):
        pin=19
        base_trip = 8
    elif(train == "M"):
        pin=12
        base_trip = 5
    else: # J/Z
        pin=3
        base_trip = 3
    pwm_sel = PWM(Pin(pin, Pin.OUT))
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
    elif bullet == 'L':
        return did == '0'
    else:
        JZdests = [
        'Broad St','Canal St',
        'Delancey St-Essex St''Marcy Av',
        'Bowery','Chambers St','Fulton St'
        ]
        return data['destination_name'] in JZdests

def J_within_M_window(bullet, diff_min, j_list):
    if bullet == 'J':
        j_list.append(diff_min)
    if bullet == 'M':
        hour = time.gmtime()[3]
        print("hour " + str(hour))
        j_preference_mins = 4.5 if hour > 7 and hour < 13 else 2.5
        for j in j_list:
            if diff_min + j_preference_mins > j:
                print("Ignoring an M train because there is an J just behind it")
                return True
    return False

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
        "L": "SubwayDeKalbAvL",
        "J": "SubwayKosciuskoSt",
        "M": "SubwayCentralAv"
    }
    while True:
        j_list = []
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
                            if J_within_M_window(bullet, diff_min, j_list):
                                continue
                            #print(str(diff_min) + " mins " + bullet + " train")
                            set_light_bool = led_flash_logic(bullet, diff_min)
                            if set_light_bool:
                                set_light = bullet
            except Exception as e:
                    print(e)
                    continue
                    pass
        time.sleep(10)
