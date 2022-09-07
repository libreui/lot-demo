# !/usr/bin/env python3
#  -*- coding: utf-8 -*-
# 温度湿度传感器上报数据MQTT
# 版本：V1.0
# 作者：Libre
# #######################
import os
import requests
import paho.mqtt.client as mqtt
import time
import sys
import random
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
time.sleep(2)
Pin = 12

# 存放温度湿度
temperature = 0.0   # 获取温度值
humidity = 0.0    # 获取湿度值

# client = mqtt.Client(protocol=3)
# client.username_pw_set('Gjt98a89eAOAm53Snnd0', '')
# client.connect(host='192.168.1.119', port=1883, keepalive=60)


def DHT11_rst():
    """重置DHT11,发送主机信号"""
    # 将GPIO设置为输出模式
    GPIO.setup(Pin, GPIO.OUT)
    # 发送前先保证电平拉高
    GPIO.output(Pin, 1)
    # 向DHT11发送低电平(开始信号)
    time.sleep(0.002)
    GPIO.output(Pin, 0)
    # 拉低电平，持续时间保证大于18ms且小于30ms
    time.sleep(0.025)
    # 向DHT11发送高电平（确保重新发送时开始为高电平）
    GPIO.output(Pin, 1)
    GPIO.setup(Pin, GPIO.IN)


def DHT11_Check():
    """检验DHT11响应信号"""
    while GPIO.input(Pin) == 0:   # 轮询检测低电平信号
        continue
    while GPIO.input(Pin) == 1:   # 轮询检测高电平信号
        continue
    return 0


def DHT11_Read_Bit():
    """读取位数据"""
    k = 0
    # 轮询检测50us位起始低电平
    while GPIO.input(Pin) == 0:
        continue

    # 计算高电平持续时间
    while GPIO.input(Pin) == 1:
        k += 1
        continue

    # 这里循环检测20的时间差不多处于28us和70us间，
    # 从而可以判断具体数据，可自行根据实际情况测试判断，稍加增减
    if k > 20:
        return 1    # 大于20次，判断为1
    else:
        return 0    # 小于20次，判断为0


def DHT11_Read_Data():
    """读取数据"""
    humi1 = 0
    humi2 = 0
    temp1 = 0
    temp2 = 0
    check = 0
    data = []

    # 主机发送信号
    DHT11_rst()

    # 如果成功接收响应信号则开始读取位数据
    if DHT11_Check() == 0:
        for i in range(40):
            data.append(DHT11_Read_Bit())

        hum1 = data[0:8]
        hum2 = data[8:16]
        tem1 = data[16:24]
        tem2 = data[24:32]
        checkbit = data[32:40]

        for i in range(8):  # 循环8次，将二进制数转换为十进制数
            humi1 += hum1[i]*(2**(7-i))
            humi2 += hum2[i]*(2**(7-1))
            temp1 += tem1[i]*(2**(7-i))
            temp2 += tem2[i]*(2**(7-i))
            check += checkbit[i]*(2**(7-i))

        temperature = temp1 + temp2 * 0.1   # 获取温度值
        humidity = humi1 + humi2 * 0.1    # 获取湿度值
        checknum = temp1 + humi1 + temp2 + humi2    # 计算前32位数的值

        # 检查前32位的值是否与校验位相等
        if checknum == check:
            # 个人测试偶尔会有湿度大于100但校验成功的个例，故这里排除
            if humidity > 100:
                # 返回0，表示读取错误
                return 0

            # 相等输出温度和湿度
            print("temp:%s,hum:%s" % (temperature, humidity))
            return 1                     # 返回1表示读取成功
        else:
            return 0                     # 返回0，表示读取错误


# 运行
def DHT11_Working():
    retry = 0
    # 如果返回0表示读取错误，retry+1，重新读取
    while DHT11_Read_Data() == 0:
        retry += 1
        print("Data error!Retrying!Times:%d" % retry)
        # 设置重新读取次数不大于10次
        if retry > 10:
            print("Fail to read data! Please retry!")
            break
        # 保证采样间隔2s
        time.sleep(2)
        continue


# 运行程序，读取数值
try:
    while True:
        # DHT11_Working()
        if DHT11_Read_Data() == 1:
            data = '{"temp":"%d"}' % temperature
            print(1)
        else:
            data = '{"temp":"0"}'
            print(2)
        time.sleep(2)

except KeyboardInterrupt:
    pass

# 运行完毕
print("Finished!")
GPIO.cleanup()
