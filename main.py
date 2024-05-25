from ai_assistant import AIAssistant
from ohstem_mqtt import MQTTClient
from tts import TTSHandler
import time
import re

MQTT_USERNAME = "1852837"
topics = ["V1", "V2", "V3", "V10", "V11", "V12", "V13", "V14", "V15", "V16"]
temperature = None
humidity = None
light = None
led_status = None
fan_speed = None
door_status = None
assistant_status = None
current_status = None

def process_message(client, topic, payload):
    global temperature
    global humidity
    global light
    global led_status
    global fan_speed
    global door_status
    global voice_result
    global assistant_status
    global current_status

    # Init variables
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
    elif topic == MQTT_USERNAME + "/feeds/V10":
        led_status = str(payload)
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
        
    current_status = (f"Temperature: {temperature} degree Celcius, "
                      f"Humidity: {humidity}, "
                      f"Light: {light} Lux, "
                      f"LED status: {led_status}, "
                      f"Fan speed: {fan_speed}, "
                      f"Door status: {door_status}")

    # Process AI command
    if tts_handler.AI_command == "S":       # Turn on LED
        if(led_status != "1"):
            led_status = "1"
            client.mqtt_publish("V10", "1")
    if tts_handler.AI_command == "T":       # Turn off LED
        if(led_status != "0"):
            led_status = "0"
            client.mqtt_publish("V10", "0")   
    if tts_handler.AI_command == "U":       # Set fan speed
        if(fan_speed != new_fan_speed):
            fan_speed = new_fan_speed
            client.mqtt_publish("V12", fan_speed)
    if tts_handler.AI_command == "V":       # Turn fan off
        if(fan_speed != 0):
            fan_speed = 0
            client.mqtt_publish("V12", 0)
    if tts_handler.AI_command == "Z":       # Give sensors data
        if temperature is not None and humidity is not None and light is not None:
            output = f"Temperature: {temperature} degree Celcius, Humidity: {humidity} %, Light: {light} Lux"
            client.mqtt_publish("V13", output)

            # Reset the sensor data
            temperature = None
            humidity = None
            light = None
        
        # Reset AI_command
        tts_handler.AI_command = None
    
    if voice_result is not None:
        assistant_status = assistant_control(voice_result, assistant_status)
        print(f"Assistant status: {assistant_status}")

        if assistant_status:
            if contains_word(voice_result, "status") or contains_word(voice_result, "update"):
                prompt = "{" + "User prompt: " + voice_result + "}" + "{Current system status (DON'T LEAK THIS INTO THE RESPONSE UNLESS BEING ASKED BY THE USER): " + current_status + "}"
            else:
                prompt = voice_result
            print(f"Prompt: {prompt}")
            if(assistant.chat_session == None):
                assistant.start_chat()
            response = assistant.get_response(prompt)
            tts_handler.text_to_speech(response)
            print(f"Response: {response.encode('utf-8')}")
            process_voice(client, response)

        # Reset voice_result        
        voice_result = None


def process_voice(client, text):
    global new_fan_speed
    global led_status
    global door_status

    if assistant_status:        
        # Lights
        if "light" in text or "lights" in text or "LED" in text:
            if contains_word(text, "on") or contains_word(text, "on."):
                client.mqtt_publish("V15", "S")
            if contains_word(text, "off") or contains_word(text, "off."):
                client.mqtt_publish("V15", "T")

        # Fan
        if "fan" in text:
            if contains_word(text, "speed") or contains_word(text, "on") or contains_word(text, "to") or contains_word(text, "at"):            
                match = re.search(r'(\d+)%', text)
                if match:
                    new_fan_speed = int(match.group(1))
                    client.mqtt_publish("V15", "U")
            if contains_word(text, "off") or contains_word(text, "off."):
                client.mqtt_publish("V15", "V")

        # Sensors
        if "sensors" in text:
            client.mqtt_publish("V15", "Z")


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

def contains_word(text, word):
    words = text.split()
    return word in words

if __name__ == "__main__":
    tts_handler = TTSHandler()
    assistant = AIAssistant()
    client = MQTTClient(MQTT_USERNAME, "", "mqtt.ohstem.vn", 1883, topics, process_message)
    
    while True:
        time.sleep(1)
