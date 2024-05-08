#pip install paho-mqtt==1.6.1
import paho.mqtt.client as mqtt
import time
from datetime import datetime
import os
import re
from gtts import gTTS
import pyaudio
import wave

# global variables
AI_command = None
AI_message1 = None
AI_message2 = None


# MQTT broker details
MQTT_SERVER = "mqtt.ohstem.vn"
MQTT_PORT = 1883
MQTT_USERNAME = "1852837"
MQTT_PASSWORD = ""
MQTT_TOPIC_PUB12 = MQTT_USERNAME + "/feeds/V12"
MQTT_TOPIC_SUB12 = MQTT_USERNAME + "/feeds/V12"
MQTT_TOPIC_PUB13 = MQTT_USERNAME + "/feeds/V13"
MQTT_TOPIC_SUB13 = MQTT_USERNAME + "/feeds/V13"
MQTT_TOPIC_PUB14 = MQTT_USERNAME + "/feeds/V14"
MQTT_TOPIC_SUB14 = MQTT_USERNAME + "/feeds/V14"
MQTT_TOPIC_PUB15 = MQTT_USERNAME + "/feeds/V15"
MQTT_TOPIC_SUB15 = MQTT_USERNAME + "/feeds/V15"


def mqtt_connected(client, userdata, flags, rc):
    print("Connected succesfully!!")
    client.subscribe(MQTT_TOPIC_SUB13) # Assistance Message in general
    client.subscribe(MQTT_TOPIC_SUB15) # Assistance Message response to command
    client.subscribe(MQTT_TOPIC_SUB14) # Assistance Command

def mqtt_subscribed(client, userdata, mid, granted_qos):
    print("Subscribed to Topic!!!")

def mqtt_recv_message(client, userdata, message):
    global AI_command, AI_message1, AI_message2 

    print(" Received message " + message.payload.decode("utf-8")
          + " on topic '" + message.topic
          + "' with QoS " + str(message.qos))

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {'Time': timestamp}

    payload = message.payload.decode("utf-8")

    if message.topic == MQTT_TOPIC_SUB13:
        AI_message1 = payload
    elif message.topic == MQTT_TOPIC_SUB15:
        AI_message2 = payload
    elif message.topic == MQTT_TOPIC_SUB14:
        AI_command = payload

    # If message has been received, create the output string for tts
    if AI_message1 != None:
        output = AI_message1
        text_to_speech(output)    

        # Reset data
        AI_message1 = None

    if AI_command == "Z" and AI_message2 != None: # Give sensor data
        output = AI_message2
        text_to_speech(output)

        # Reset the data
        AI_command = None
        AI_message2 = None

    if AI_command == "Y" and AI_message2 != None: # Turn on the fan
        output = AI_message2
        text_to_speech(output)

        # Reset the data
        AI_command = None
        AI_message2 = None


    if AI_command == "X" and AI_message2 != None: # Adjust fan speed
        speed_value = re.findall(r'(\d+)', AI_message2)
        if speed_value:
            output = "Fan speed set to " + speed_value[0] + " %"
            text_to_speech(output)
            mqttClient.publish(MQTT_TOPIC_PUB12, speed_value[0])
        else:
            output = "Invalid command"
            text_to_speech(output)
            
        # Reset the data
        AI_command = None
        AI_message2 = None
        

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

    #Register mqtt events
    mqttClient.on_connect = mqtt_connected
    mqttClient.on_subscribe = mqtt_subscribed
    mqttClient.on_message = mqtt_recv_message

    mqttClient.loop_start()

    while True:
        time.sleep(1)
    