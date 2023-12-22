# PICO_W_MQTT_pub_sub
 subscription loop SLOW

on a PICO W with CP829

a minimal MQTT 
* publish every minute
* subscribe ( and loop ) to remote commands

PROBLEM: the 'mqtt_client.loop()' waits over 1 second and blocks the MAIN timer loop

# on RPI4 is a mosquiito broker running

use some alias to show the feed from the PICO_W and to drive commands ( pub to topic/set )

![Screenshot RPI4 ](/img/RPI4_MQTT.png)

![Screenshot PICO_W IDE ](/img/PICOW_mqtt_test_pub_sub.png)

![Screenshot PICO_W_IDE show time ](/img/PICOW_mqtt_test_pub_sub.png)
