# PicoW trains alert

Made for Raspberry Pi Pico W

The idea is to monitor for and identify IDEAL times to leave your apartment to catch the train, in my case the PATH from Hoboken to New York City.

Another example configuration is shown for 3 separate trains in Bushwick, Brooklyn using another API with multiple LED's.

INSTRUCTIONS:

Create a `secrets.py` file with your network SSID and password instantiated as string variables. The script will use this.

You must save the mta/path code to your device as `main.py` for it to run on startup.

```
ssid = "MyAltice sfdwfdsd" # 
passw = '3431-hudfuhsha-212' #
```

Install the necessary libraries using the shell
```
import mip
mip.install('urequests')
mip.install('utime')
```


Tweak the timings present in the `if elif else` logic.

Run the code (I used the Thonny IDE to load it to my PICO W)

Find a way to externally supply the voltage pins on your board so that it can stay connected to your wifi and keep polling.

I am soldering it with a ~2.5V 2xAA battery array of rechargable amazonbasics batteries and setting it above my door frame.


LIGHT READING GUIDE: