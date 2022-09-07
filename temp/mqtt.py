import RPi.GPIO as GPIO
import dht11
import paho.mqtt.client as mqtt
import random
import time

# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

# read data using pin 14
instance = dht11.DHT11(pin=18)

# initialize MQTT
broker = '192.168.1.119'  # mqtt代理服务器地址
port = 1883
keepalive = 60     # 与代理通信之间允许的最长时间段
topic = "v1/devices/me/telemetry"  # 消息主题
client_id = f'python-mqtt-pub-{random.randint(0, 1000)}'  # 客户端id不能重复
client_token = 'Gjt98a89eAOAm53Snnd0'


def on_connect(client, userdata, flags, rc):
    """连接回调"""
    if rc == 0:
        print('Connected to MQTT OK!')
    else:
        print('Failed to connect, return code %d\n', rc)


def connect_mqtt():
    """连接mqtt服务器"""
    client = mqtt.Client(client_id)
    client.username_pw_set(client_token)
    client.on_connect = on_connect
    try:
        client.connect(broker, port, keepalive)
        client.loop_start()
        client.subscribe(topic, 0)
    except Exception as e:
        print('MQTT error', e)

    return client


def run():
    """运行"""
    client = connect_mqtt()
    try:
        while True:
            result = instance.read()
            if result.is_valid():
                data = '{"temp":"%-3.1f"}' % result.temperature
                client.publish(topic=topic, payload=data, qos=0)
                print(data)
            time.sleep(6)

    except KeyboardInterrupt:
        GPIO.cleanup()
        client.loop_stop()


if __name__ == '__main__':
    run()
