import google.generativeai as genai
import os
import time


class AIAssistant:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.configure_api()
        self.model = self.create_model()
        self.chat_session = self.start_chat()


    def configure_api(self):
        genai.configure(api_key=self.api_key)

    def create_model(self):
        generation_config = {
        "temperature": 0.8,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
        }
        safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        ]

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            safety_settings=safety_settings,
            generation_config=generation_config,
            system_instruction=(
                "You are an helpful AI assistant for a smart home. You can control the light (there's only 1 light for now), the fan and the door. "
                "You can also give the sensor data (temperature, humidity and light). "
                "You can converse like a normal assistant but if a command is given, only check if it belongs "
                "to the above tasks. When being asked to turn on the fan (in normal working mode), please ask for the fan speed first, "
                "after that, the user will response with a percentage value. Then set the fan to this value. When being asked for "
                "update on the status of the house, ALWAYS response in the format of: STATUS: ..."
                "The system will enter a special mode when the gesture control system is on, the user can ask you to this mode on or off. "
                "Remember that if the gesture control system is on, the system will now works like a state machine, if the light is "
                "currently on and the command related to the light is given, the light will be turn off and vice versa BY YOU without the need " 
                "for the user to confirm whether to turn it on or off, you need to announce this out loud for the user, this is unrelated "
                "to the act of updating the status of the house. The same applies to the door, HOWEVER, the FAN don't need to be alternate "
                "between on and off as there are 5 gesture related to 5 level of speed for the fan so you just need to set the fan to that level."
            ),
        )
        return model

    def start_chat(self):
        return self.model.start_chat(history=[])

    def get_response(self, prompt):
        response = self.chat_session.send_message(prompt)
        return response.text

if __name__ == "__main__":
    assistant = AIAssistant()
    while True:
        time.sleep(1)