#pip install paho-mqtt==1.6.1
import paho.mqtt.client as mqtt
import time
import csv
from datetime import datetime
import pandas as pd
import numpy as np
from gtts import gTTS
import os
import pyaudio
import wave

# global variables
temperature = None
humidity = None
light = None

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

def mqtt_connected(client, userdata, flags, rc):
    print("Connected succesfully!!")
    client.subscribe(MQTT_TOPIC_SUB1) # Temperature
    client.subscribe(MQTT_TOPIC_SUB2) # Humidity
    client.subscribe(MQTT_TOPIC_SUB3) # Light

def mqtt_subscribed(client, userdata, mid, granted_qos):
    print("Subscribed to Topic!!!")

def mqtt_recv_message(client, userdata, message):
    global temperature, humidity, light

    print(" Received message " + message.payload.decode("utf-8")
          + " on topic '" + message.topic
          + "' with QoS " + str(message.qos))

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {'Time': timestamp}

    payload = float(message.payload.decode("utf-8"))  # Convert payload to float

    if message.topic == MQTT_TOPIC_SUB1:
        temperature = payload
    elif message.topic == MQTT_TOPIC_SUB2:
        humidity = payload
    elif message.topic == MQTT_TOPIC_SUB3:
        light = payload

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

    # If all sensor data has been received, create the output string for tts
    if temperature is not None and humidity is not None and light is not None:
        output = f"Temperature: {temperature} degree Celcius, Humidity: {humidity} %, Light: {light} %"
        text_to_speech(output)

        # Reset the sensor data
        temperature = None
        humidity = None
        light = None

def text_to_speech(text):
    # Convert text to speech
    tts = gTTS(text=text, lang='en')
    tts.save("temp.mp3")

    # Convert mp3 file to wav because PyAudio works with wav files
    os.system('ffmpeg -y -i temp.mp3 temp.wav > NUL 2>&1')

    # Play the wav file
    chunk = 1024  
    f = wave.open("temp.wav","rb")  
    p = pyaudio.PyAudio()  
    stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
                    channels = f.getnchannels(),  
                    rate = f.getframerate(),  
                    output = True)  
    data = f.readframes(chunk)  

    while data:  
        stream.write(data)  
        data = f.readframes(chunk)  

    stream.stop_stream()  
    stream.close()  
    p.terminate()
    f.close()

    # Remove the temporary files
    os.remove("temp.mp3")
    os.remove("temp.wav")


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
    