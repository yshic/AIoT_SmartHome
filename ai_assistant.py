import google.generativeai as genai
import os


class AIAssistant:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self._configure_api()
        self.model = self._create_model()
        self.chat_session = self._start_chat()


    def _configure_api(self):
        genai.configure(api_key=self.api_key)

    def _create_model(self):
        generation_config = {
        "temperature": 0.5,
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
                "You are an AI assistant for a smart home. You can control the light (there's only 1 light for now), "
                "the fan (please ask for fan speed), the door. You can also give the sensor (temperature, humidity and light) data. "
                "You can converse like a normal assistant but if a command is given, only check if it belongs to the above tasks."
            ),
        )
        return model

    def _start_chat(self):
        return self.model.start_chat(history=[])

    def get_response(self, prompt):
        response = self.chat_session.send_message(prompt)
        return response.text, self.chat_session.history

    def end_chat(self):
        self.chat_session.end_chat()