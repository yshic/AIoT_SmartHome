from ohstem_mqtt import MQTTClient
from tts import TTSHandler
from ai_assistant import AIAssistant
import time

MQTT_USERNAME = "1852837"
topics = ["V1", "V2", "V3", "V10", "V11", "V12", "V13", "V14", "V15", "V16"]
assistant_status = None

def process_message(client, topic, payload):
    global temperature
    global humidity
    global light
    global voice_result
    global assistant_status

    # Init variables
    temperature = None
    humidity = None
    light = None
    voice_result = None
    prompt = None
    response = None

    # Process the received message
    if topic == MQTT_USERNAME + "/feeds/V1":
        temperature = float(payload)
        print(f"Received temperature: {temperature}")
    elif topic == MQTT_USERNAME + "/feeds/V2":
        humidity = float(payload)
        print(f"Received humidity: {humidity}")
    elif topic == MQTT_USERNAME + "/feeds/V3":
        light = float(payload)
        print(f"Received light: {light}")
    elif topic == MQTT_USERNAME + "/feeds/V13":
        tts_handler.AI_message1 = payload
    elif topic == MQTT_USERNAME + "/feeds/V14":
        tts_handler.AI_message2 = payload
    elif topic == MQTT_USERNAME + "/feeds/V15":
        tts_handler.AI_command = payload
        print(f"Received AI command: {tts_handler.AI_command}")
    elif topic == MQTT_USERNAME + "/feeds/V16":
        voice_result = payload      
        print(f"Received Voice: {voice_result}")

    # If all sensor data has been received, create the output string
    if tts_handler.AI_command == "Z":
        if temperature is not None and humidity is not None and light is not None:
            output = f"Temperature: {temperature} degree Celcius, Humidity: {humidity} %, Light: {light} Lux"
            client.mqtt_publish("V13", output)

            # Reset the sensor data
            temperature = None
            humidity = None
            light = None
        
        # Reset AI_command
        tts_handler.AI_command = None

    if tts_handler.AI_message1 is not None:
        output = tts_handler.AI_message1
        tts_handler.text_to_speech(output)
        tts_handler.AI_message1 = None
    
    if voice_result is not None:
        assistant_status = assistant_control(voice_result, assistant_status)
        print(f"Assistant status: {assistant_status}")

        if assistant_status:
            prompt = voice_result
            if(assistant.chat_session == None):
                assistant.start_chat()
            response = assistant.get_response(prompt)
            tts_handler.text_to_speech(response)
            process_voice(client, response)

def process_voice(client, text):
    if assistant_status:        
        if "on" in text and "light" in text:
            print("Here")
            client.mqtt_publish("V10", "1")
        elif "off" in text and "light" in text:
            client.mqtt_publish("V10", "0")

def assistant_control(text, assistant_status):
    if "hi assistant" in text:
        return True
    elif "hi" in text:
        return True        
    elif "hello assistant" in text:
        return True
    elif "hello" in text:
        return True
    if assistant_status:
        if "bye assistant" in text:
            return False
        elif "bye" in text:
            return False
        elif "goodbye assistant" in text:
            return False
        elif "goodbye" in text:
            return False
        else:
            return True
    else:
        return False


tts_handler = TTSHandler()
assistant = AIAssistant()
client = MQTTClient(MQTT_USERNAME, "", "mqtt.ohstem.vn", 1883, topics, process_message)

while True:
    time.sleep(1)
