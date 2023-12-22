# PICO_W_MQTT_pub_sub
 subscription loop SLOW

on a **PICO W with CP829**

a minimal MQTT 
* publish every minute
* subscribe ( and loop ) to remote commands to drive the board LED : **MQTT BLINKY**

PROBLEM: the 'mqtt_client.loop()' waits over 1 second and blocks the MAIN timer loop
______________
**test results:** how many seconds need a counter to 1.000.000
```
# JOB1M : 14.8 sec
# JOB1M + JOB1min : 26.5 sec
# JOB1M + JOB1min + JOB1sec : 38.1 sec
# JOB1M + JOB1min + JOB1sec + JOBt : 56.2 sec
# and enable in JOB1sec mqtt_client.loop(timeout=0.01) : 1524.1 sec
```
but **remote operation ( of board LED ) works**

[open ISSUE](https://github.com/adafruit/Adafruit_CircuitPython_MiniMQTT/issues/195)

______________
# on RPI4 is a 'mosquitto broker' running

use some alias to show the feed from the PICO_W and to drive commands ( pub to topic/set )
![Screenshot RPI4 ](/img/RPI4_MQTT.png)

# PICO_W MU Editor REPL
topic/set commands come through if there is a 'mqtt_client.loop()'
![Screenshot PICO_W IDE ](/img/PICOW_mqtt_test_pub_sub.png)
here show the problematic timing
![Screenshot PICO_W_IDE show time ](/img/PICOW_mqtt_test_pub_sub_loopdt.png)

______________
try on TLS again, not work CP829, 

not work **CP810** but copy in adafruit_minimqtt from  21.12.2022 OK

![Screenshot REMOTE broker TLS ](/img/PICOW_mqtt_test_pub_sub_REMOTE_TLS.png)

make set of new alias mqttxubR
______________

