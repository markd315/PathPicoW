# PathPicoW

Made for Raspberry Pi Pico W

The idea is to monitor for and identify IDEAL times to leave your apartment to catch the train, in my case the PATH from Hoboken to New York City.


INSTRUCTIONS:

Create a `secrets.py` file with your network SSID and password instantiated as string variables. The script will use this.

Tweak the timings present in the `if elif else` logic.

Run the code (I used the Thonny IDE to load it to my PICO W)

Find a way to externally supply the voltage pins on your board so that it can stay connected to your wifi and keep polling.

I am soldering it with a 3V 2xAA battery array of rechargable amazonbasics batteries and setting it above my door frame.


LIGHT READING GUIDE:
15-12 minutes: short bursts of light followed by long darkness (early warning)
12-10 minutes: constant light. You will be unrushed if you leave now.
10-9 minutes: Long 1.5 second even on/off cycle. Leave soon or now.
9-8.5 minutes: .5 second on/off cycle. Leave urgently.
8.5-8 minutes: Even faster .15 second on off cycle. Ideal time to walk out the door.
8-7.5 minutes: strobing .05 second on off cycle. Last chance to leave, rushing is necessary.
15+ or 7.5- minutes: Light off, no departure window imminent.

