from machine import Pin
import network  # handles connecting to WiFi
import urequests  # handles making and servicing network requests
import utime
import uasyncio
import secrets

led = Pin("LED", Pin.OUT)

next_train_time = -99 # TODO use this as a global somehow?

def led_flash_logic(minutes):
    # occasional short blink is a pre-alert, don't leave yet.
    # 10-9 is casual blink
    # 9-830 is picking up
    # 830-8 is fast
    # 8-730 is VERY urgent, jog to make it
    if minutes > 10:
        strobe_light(10, 1490)
    elif minutes > 9:
        strobe_light(1500, 1500)
    elif minutes > 8.5:
        strobe_light(500, 500)
    elif minutes > 8:
        strobe_light(150, 150)
    else:
        strobe_light(40, 40)
        
def parse_train_arrival(ts):
    yr = int(ts[0:4])
    mo = int(ts[5:7])
    da = int(ts[8:10])
    hr = int(ts[11:13])
    mi = int(ts[14:16])
    se = int(ts[17:19])
    return utime.mktime((yr, mo, da, hr, mi, se, 0, 0))

def strobe_light(ms_interval, off_interval):
    led.value(0)
    range = int(8000/  ((ms_interval+off_interval)/2)  )
    if range % 2 == 0:
        range += 1
    for i in range(0,range):
        if i % 2 == 0:
            led.value(0)
            utime.sleep_ms(off_interval)
        else:
            led.value(1)
            utime.sleep_ms(ms_interval)
    led.value(1)

async def async_http():
    return urequests.get("https://path.api.razza.dev/v1/stations/hoboken/realtime")

async def await_http(task):
    print("awaiting previously made request")
    complete = await task
    while True: # loop in case response processing incomplete
        try:
            return complete.json()
        except:
            pass

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    led.value(0)    # Connect to network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    wlan.connect(secrets.ssid, secrets.passw)

    task = None
    print("Querying PATH API:")
    r = urequests.get("https://path.api.razza.dev/v1/stations/hoboken/realtime").json()    
    while True:
        if task is not None:
            r = uasyncio.run(await_http(task))
        print("Querying PATH API:")
        task = uasyncio.create_task(async_http())
        waited = False
        print(r)
        for train in r['upcomingTrains']:
            if '33rd Street' in train['lineName']:
                arr = parse_train_arrival(train['projectedArrival'])
                now = utime.time()
                diff_min = float(arr - now) / 60.0 - 300 #tz and secs to mins
                #diff_min -=8 # TODO REMOVE TESTING
                diff_min -= 0.1 # to account for the blink cycle duration
                next_train_time = diff_min # set global
                print(str(diff_min) + " mins til a train")
                if next_train_time > 15.5 or next_train_time < 7.5:
                    led.value(0)
                    continue # Not a relevant train arrival yet/anymore
                if next_train_time > 12.5:
                    # slow blink, short duty cycle
                    waited = True
                    led_flash_logic(next_train_time)
                    break
                elif next_train_time > 10: # 10-12 mins is no urgency
                    led.value(1)
                    break
                else: # we have some urgency, time to flash the light
                    waited = True
                    led_flash_logic(next_train_time)
                    break
        if not waited:
            utime.sleep(8)