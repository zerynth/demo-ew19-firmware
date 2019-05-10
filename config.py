# -*- coding: utf-8 -*-
# @Author: Zerynth Team

import flash

CYPRESS_STANDID = 0
RS_STANDID      = 1

# !!! Change the configuration below
config = {
    'SSID': 'YOUR SSID!',
    'PSW': 'YOUR PASSWORD!',
    'STANDID': CYPRESS_STANDID  # or RS_STANDID
}

def led_init():
    for led in (LED0, LED1, LED2):
        pinMode(led, OUTPUT)
        digitalWrite(led, HIGH) # both LEDs off
    digitalWrite(LED2, LOW) # turn LED1 on

def led_start_publish():
    digitalWrite(LED2, HIGH) # turn LED1 off
    digitalWrite(LED0, LOW) # turn LED0 on

def led_start_transaction():
    for _ in range(10):
        pinToggle(LED0)
        sleep(40)
    digitalWrite(LED0, HIGH)
    digitalWrite(LED1, LOW)

def led_end_transaction():
    digitalWrite(LED1, HIGH)
    digitalWrite(LED0, LOW)
