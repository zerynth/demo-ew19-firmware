import mcu
import streams
import threading
import struct

from wireless import wifi
from murata.lbee5kl1dx import lbee5kl1dx as wifi_driver
from aws.iot import iot, default_credentials

from blockchain.ethereum import ethereum

from bosch.bme280 import bme280
from cypress.capsense import capsense

import eth
import config


def send_eth_transaction(temp, hum):
    print("> Preparing Ethereum Transaction")
    # Get our current balance
    balance = eth.rpc.getBalance(eth.ADDRESS)
    nt = eth.rpc.getTransactionCount(eth.ADDRESS)

    # Prepare a transaction object
    tx = ethereum.Transaction()
    tx.set_gas_price("0x430e23411")
    tx.set_gas_limit("0x33450")
    tx.set_nonce(nt)
    tx.set_receiver(eth.RECEIVER_ADDRESS)
    tx.set_chain(ethereum.ROPSTEN)

    btemp = struct.pack("<i", int(temp*100))
    bhum  = struct.pack("<I", int(hum*100))
    tx.set_data(btemp + bhum + bytes([config.config['STANDID']]))

    # Sign the transaction with the private key and send it
    tx.sign(eth.PRIVATE_KEY)
    print(tx)
    tx_hash = eth.rpc.sendTransaction(tx.to_rlp(True))
    print("> Monitor transaction at:\nhttps://ropsten.etherscan.io/tx/%s" % tx_hash)


def ethereum_store():
    tx_mutex.acquire()
    config.led_start_transaction()
    temp, hum = sensor.get_temp(), sensor.get_hum()
    thing.mqtt.publish(config.config['TOPIC'], {'touch': True})
    send_eth_transaction(temp, hum)
    config.led_end_transaction()
    tx_mutex.release()


ser_ch = streams.serial()
config.led_init()

wifi_driver.init()
for _ in range(3):
    try:
        print("> Establishing Link...")
        wifi.link(config.config['SSID'],wifi.WIFI_WPA2,config.config['PSW'])
        break
    except Exception as e:
        print("> ooops, something wrong while linking :(")
else:
    mcu.reset()
print("> linked!")

tx_mutex = threading.Lock()
endpoint, thingname, clicert, pkey = default_credentials.load()
mqtt_id = ''.join(['%02x' % byte for byte in mcu.uid()]) # derive unique id from mcu uid
thing = iot.Thing(endpoint, mqtt_id, clicert, pkey, thingname=thingname)

print("> connecting to mqtt broker...")
thing.mqtt.connect()
print("> connected")
thing.mqtt.loop()

sensor = bme280.BME280(I2C2)
capsense.init()
capsense.on_btn(ethereum_store)
capsense.on_btn(ethereum_store, event=capsense.BTN1_RISE)

config.led_start_publish()
while True:
    tx_mutex.acquire()
    print("> publish temperature and humidity")
    thing.mqtt.publish(config.config['TOPIC'], {
        'temp': sensor.get_temp(),
        'hum': sensor.get_hum()
    })
    tx_mutex.release()
    sleep(3000)

