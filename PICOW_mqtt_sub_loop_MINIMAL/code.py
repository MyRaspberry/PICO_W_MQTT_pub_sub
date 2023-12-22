#SH_T# code.py
print("minimal mqtt publish and subscribe loop ( remote operation )")

import gc
print(f"+ import gc {gc.mem_free()}")
import os
WIFI_SSID = os.getenv('WIFI_SSID')
WIFI_PASSWORD = os.getenv('WIFI_PASSWORD')

TZ_OFFSET = os.getenv('TZ_OFFSET')
useNTP = bool(os.getenv('useNTP'))

MQTT_broker = os.getenv('MQTT_broker') # ___ RPI IP
MQTT_port = os.getenv('MQTT_port') # __ 1883
MQTT_user = os.getenv('MQTT_user') # _______ u213
MQTT_pass = os.getenv('MQTT_pass') # _______ p213

MQTT_mtopic = os.getenv('MQTT_mtopic')
mqtt_topic = MQTT_mtopic
mqtt_hello= f" {os.uname().machine} with CP{os.uname().version} "

import board
import digitalio
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = True  # ________________ after boot LED ON helps to see its working.. can be operated remotely by MQTT
print("___+++ board LED ON")

import time
import socketpool
import wifi
import rtc
import adafruit_ntp
import adafruit_minimqtt.adafruit_minimqtt as MQTT
print(f"+ import ... minimqtt {gc.mem_free()}")

# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connect(mqtt_client, userdata, flags, rc):
    # This function will be called when the mqtt_client is connected
    # successfully to the broker.
    print("\nmqtt Connected to MQTT Broker!")
    print("Flags: {0} RC: {1}".format(flags, rc))


def disconnect(mqtt_client, userdata, rc):
    # This method is called when the mqtt_client disconnects
    # from the broker.
    print("\nmqtt Disconnected from MQTT Broker!")


def subscribe(mqtt_client, userdata, topic, granted_qos):
    # This method is called when the mqtt_client subscribes to a new feed.
    print("\nmqtt Subscribed to {0} with QOS level {1}".format(topic, granted_qos))


def unsubscribe(mqtt_client, userdata, topic, pid):
    # This method is called when the mqtt_client unsubscribes from a feed.
    print("\nmqtt Unsubscribed from {0} with PID {1}".format(topic, pid))


def publish(mqtt_client, userdata, topic, pid):
    # This method is called when the mqtt_client publishes data to a feed.
    print("\nmqtt Published to {0} with PID {1}".format(topic, pid))


def message(client, topic, message):
    print("\nmqtt New message on topic {0}: {1}".format(topic, message))
    if topic =="PICOW/set": # _____________________________________ MQTT REMOTE BLINKY
        if message == "1" :
            LEDsp = True
        if message == "0" :
            LEDsp = False
        led.value = LEDsp
        print(f"___+++ board LED {LEDsp}")

# _______________________________________________ router login
wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
print("___ Connected to {:s}".format( WIFI_SSID) )
pool = socketpool.SocketPool(wifi.radio)

if ( useNTP ) :
    try:
        print("___ get NTP to RTC")
        ntp = adafruit_ntp.NTP(pool, tz_offset=TZ_OFFSET)
        rtc.RTC().datetime = ntp.datetime # NOTE: This changes the boards system time
    except:
        print("failed")

print("___ MQTT broker: "+MQTT_broker)
print("___ mqtt_topic: "+mqtt_topic)
print("___ mqtt NO TLS")
mqtt_client = MQTT.MQTT(
    broker=MQTT_broker,
    port=MQTT_port,
    username=MQTT_user,
    password=MQTT_pass,
    socket_pool=pool,
    ssl_context=False, #ssl_context=ssl.create_default_context(),
    )
# Connect callback handlers to mqtt_client
mqtt_client.on_connect = connect
mqtt_client.on_disconnect = disconnect
mqtt_client.on_subscribe = subscribe
mqtt_client.on_unsubscribe = unsubscribe
mqtt_client.on_publish = publish
mqtt_client.on_message = message

MQTTok = False

try:
    mqtt_client.connect()
    MQTTok = True # _______________________________ used later for publish
except Exception as e:
    print("Error: MQTT connect\n", str(e))
    MQTTok = False

try:
    print("___ Publishing to %s" % MQTT_mtopic)
    mqtt_client.publish(MQTT_mtopic,mqtt_hello )
    MQTTok = True # _______________________________ used later for publish
except Exception as e:
    print("Error: MQTT publish hello\n", str(e))
    #MQTTok = False

try:  # setup subscribe
    mqtt_topic_tune = mqtt_topic + "/set"
    print("___ Subscribing to %s tuning" % mqtt_topic_tune)
    mqtt_client.subscribe(mqtt_topic_tune)
except Exception as e:
    print("Error: MQTT subscribe tuning\n", str(e))
    #MQTTok = False


# _______________________________________________ setup MAIN SEQUENCE
def time_now(): # ______________________________________ use time and NOT datetime
    global nowsec, nowmin
    now = time.localtime()
    nows = f"{now.tm_year}-{now.tm_mon:02}-{now.tm_mday:02} {now.tm_hour:02}:{now.tm_min:02}:{now.tm_sec:02}"
    nowsec = now.tm_sec # ______________________________ look for change and have a 1 sec tick
    nowmin = now.tm_min # ______________________________ look for change and have a 1 min tick
    return nows

nowsec=0
nowseclast=0

loopc = 0
loopdc = 500 # let pass loopdc loops and only then check for time.localtime()

def JOBt() :
    global nows, loopc
    loopc += 1
    if ( loopc > loopdc ) :
        loopc = 0
        nows = time_now() # not check time every loop because 1Mloop will be 20min

def JOB1sec() :
    global nowseclast
    if nowsec != nowseclast :
        nowseclast = nowsec
        print(".",end="")
        #ts=time.monotonic()
        #mqtt_client.loop() # every second check if remote command comes in
        mqtt_client.loop(timeout=0.01)
        #print(f"___ mqtt_client loop {(time.monotonic()-ts)} sec")

nowmin=0
nowminlast=0

def JOB1min() :
    global nowminlast
    if nowmin != nowminlast :
        nowminlast = nowmin
        print(f"\n1min:{nows}")
        mqtts = f"{nows}"
        mqtt_client.publish(MQTT_mtopic,mqtts )

loop1M=0
loop1Msec=time.monotonic()

def JOB1M() :
    global loop1M,loop1Msec
    loop1M += 1
    if loop1M >= 1000000 :
        loop1M = 0
        loop1Msecnow = time.monotonic()
        dt = loop1Msecnow-loop1Msec
        loop1Msec = loop1Msecnow # remember
        print(f"\n1Mloop needed {dt:,.1f} sec")
        #mqtts = f"{nows} 1Mloop {dt:,.1f} sec"
        #mqtt_client.publish(MQTT_mtopic,mqtts ) # diagnostic only


# _________________________________________________________ MAIN
while True:
    JOBt() # ______________________________________________ nows = time_now() and set sec and min ticks
    JOB1sec() # ___________________________________________ mqtt_client.loop()
    JOB1min() # ___________________________________________ mqtt publish
    JOB1M() # _____________________________________________ job loop performance

# JOB1M : 14.8 sec
# JOB1M + JOB1min : 26.5 sec
# JOB1M + JOB1min + JOB1sec : 38.1 sec
# JOB1M + JOB1min + JOB1sec + JOBt : 56.2 sec
# and enable in JOB1sec mqtt_client.loop(timeout=0.01) : 1524.1 sec
