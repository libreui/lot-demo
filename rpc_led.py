import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import json

Pin = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(Pin, GPIO.OUT)
GPIO.output(Pin, GPIO.LOW)

topic = "v1/devices/me/telemetry"
status = False


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # 发送遥测状态
    getValue()

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("v1/devices/me/rpc/request/+")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    id = msg.topic.split('/')[-1]
    print(str(msg.payload))
    # message = str(msg.payload)
    commend = json.loads(msg.payload)
    method = commend['method']
    params = commend['params']
    # 发送遥测数据

    if method == 'getValue':
        getValue()
    if method == 'setValue':
        setValue(params)

    # 回复RPC
    client.publish("v1/devices/me/rpc/response/%s" % id)


def getValue():
    if status:
        GPIO.output(Pin, GPIO.HIGH)
    else:
        GPIO.output(Pin, GPIO.LOW)
    data = json.dumps({"status": status})
    client.publish(topic=topic, payload=data, qos=0)


def setValue(params):
    global status
    status = params
    getValue()


client = mqtt.Client()
client.username_pw_set('A3_TEST_TOKEN')
client.on_connect = on_connect
client.on_message = on_message

# client.connect("mqtt.eclipseprojects.io", 1883, 60)
client.connect("192.168.1.119", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
