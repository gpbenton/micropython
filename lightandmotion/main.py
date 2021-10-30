# light and motion detector
import machine
from machine import Pin
from secrets import broker
import ubinascii
import umqtt.simple
import time
import network

from led import led

def connect(client_id, broker):
  client = umqtt.simple.MQTTClient(client_id, broker, keepalive=60)
  print ("Connecting to " + broker)
  client.connect()
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

# ---  Start here ---

led.on()
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
delay = 0
print ("Waiting for wifi")
while delay < 30 and not wlan.isconnected():
    delay = delay + 1
    time.sleep(1)

client_id = ubinascii.hexlify(machine.unique_id())

try:
  client = connect(client_id, broker)
except OSError as e:
  restart_and_reconnect()

led.off()

motionTopic = b'sensor/'+client_id+b'/motion'
motionSensor = Pin(16, Pin.IN)
motionValue = motionSensor.value()
client.publish(motionTopic, str(motionValue))

lightTopic = b'sensor/'+client_id+b'/light'
lightSensor = Pin(0, Pin.IN)
lightValue = lightSensor.value()
client.publish(lightTopic, str(lightValue))
prevLightPublish = time.time()

while True:
  try:
    newMotionValue = motionSensor.value()
    if newMotionValue != motionValue:
        motionValue = newMotionValue
        client.publish(motionTopic, str(motionValue))

    # Don't change light reading more than once a minute
    now = time.time()
    if (now - prevLightPublish) > 60:
        newLightValue = lightSensor.value()
        if newLightValue != lightValue:
            lightValue = newLightValue
            client.publish(lightTopic, str(lightValue))
            prevLightPublish = now
  except OSError as e:
    restart_and_reconnect()
