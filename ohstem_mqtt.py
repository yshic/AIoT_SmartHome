import paho.mqtt.client as mqtt
import time
import csv
from datetime import datetime
import pandas as pd

# global variables
temperature = None
humidity = None
light = None
AI_command = None

# MQTT broker details
MQTT_SERVER = "mqtt.ohstem.vn"
MQTT_PORT = 1883
MQTT_USERNAME = "1852837"
MQTT_PASSWORD = ""
MQTT_TOPIC_PUB1 = MQTT_USERNAME + "/feeds/V1"
MQTT_TOPIC_SUB1 = MQTT_USERNAME + "/feeds/V1"
MQTT_TOPIC_PUB2 = MQTT_USERNAME + "/feeds/V2"
MQTT_TOPIC_SUB2 = MQTT_USERNAME + "/feeds/V2"
MQTT_TOPIC_PUB3 = MQTT_USERNAME + "/feeds/V3"
MQTT_TOPIC_SUB3 = MQTT_USERNAME + "/feeds/V3"
MQTT_TOPIC_SUB14 = MQTT_USERNAME + "/feeds/V14"
MQTT_TOPIC_PUB14 = MQTT_USERNAME + "/feeds/V14"
MQTT_TOPIC_PUB15 = MQTT_USERNAME + "/feeds/V15"
MQTT_TOPIC_SUB15 = MQTT_USERNAME + "/feeds/V15"

def mqtt_connected(client, userdata, flags, rc):
    print("Connected succesfully!!")
    client.subscribe(MQTT_TOPIC_SUB1) # Temperature
    client.subscribe(MQTT_TOPIC_SUB2) # Humidity
    client.subscribe(MQTT_TOPIC_SUB3) # Light
    client.subscribe(MQTT_TOPIC_SUB14) # Assistance Command

def mqtt_subscribed(client, userdata, mid, granted_qos):
    print("Subscribed to Topic!!!")

def mqtt_recv_message(client, userdata, message):
    global temperature, humidity, light, AI_command

    print(" Received message " + message.payload.decode("utf-8")
          + " on topic '" + message.topic
          + "' with QoS " + str(message.qos))

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {'Time': timestamp}

    payload = message.payload.decode("utf-8")

    if message.topic == MQTT_TOPIC_SUB1:
        temperature = float(payload)
    elif message.topic == MQTT_TOPIC_SUB2:
        humidity = float(payload)
    elif message.topic == MQTT_TOPIC_SUB3:
        light = float(payload)
    elif message.topic == MQTT_TOPIC_SUB14:
        AI_command = payload

    # logging
    df = pd.read_csv('mqtt_messages_log.csv')
    row_index = df.loc[df['Time'] == timestamp].index
    if row_index.empty:
        df = pd.concat([df, pd.DataFrame([data])])
    else:
        for key in data:
            df.loc[row_index, key] = data[key]

    # Filter out rows with all-NA values
    df = df.dropna(how='all')

    df.to_csv('mqtt_messages_log.csv', index=False)

    # If all sensor data has been received, create the output string
    if AI_command == "Z":
        if temperature is not None and humidity is not None and light is not None:
            output = f"Temperature: {temperature} degree Celcius, Humidity: {humidity} %, Light: {light} Lux"
            mqttClient.publish(MQTT_TOPIC_PUB15, output)

            # Reset the sensor data
            temperature = None
            humidity = None
            light = None
        
        # Reset AI_command
        AI_command = None


if __name__ == "__main__":
    mqttClient = mqtt.Client()
    mqttClient.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqttClient.connect(MQTT_SERVER, int(MQTT_PORT), 60)

    # Create a new CSV file with headers
    with open('mqtt_messages_log.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Time', 'V1', 'V2', 'V3'])

    #Register mqtt events
    mqttClient.on_connect = mqtt_connected
    mqttClient.on_subscribe = mqtt_subscribed
    mqttClient.on_message = mqtt_recv_message

    mqttClient.loop_start()

    while True:
        time.sleep(1)
    