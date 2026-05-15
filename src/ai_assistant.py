import os
import time
from google import genai
from google.genai import types


class AIAssistant:
    def __init__(self, api_key=None):
        # Initialize the new Client
        self.client = genai.Client(api_key=api_key or os.environ.get("GEMINI_API_KEY"))
        self.model_id = "gemini-2.5-flash-lite"

        self.sys_instr = (
            "Role: Smart Home AI Assistant. Control: 1 light, 1 fan, 1 door. Sensors: temp, humidity, light.\n"
            "--- OPERATING MODES ---\n"
            "1. NORMAL MODE (Default):\n"
            "   - Converse naturally.\n"
            "   - IF user asks to turn on the fan: ALWAYS ask for speed percentage (0-100%) first. Wait for response.\n"
            "   - Format updates as 'STATUS: [Description]'.\n\n"
            "2. GESTURE MODE (State Machine):\n"
            "   - Enter/Exit only when user explicitly asks for 'Gesture Control'.\n"
            "   - LIGHT/DOOR: Act as a toggle. If command received, flip current state (ON->OFF / OFF->ON) "
            "     and announce the action immediately. No confirmation needed.\n"
            "   - FAN: Do NOT toggle. Set speed directly based on the gesture level (1-5) provided.\n"
            "   - Announce all actions out loud for the user."
        )

        # Configuration including Safety and Instructions
        self.config = types.GenerateContentConfig(
            system_instruction=self.sys_instr,
            temperature=0.7,
            top_p=0.95,
            max_output_tokens=2048,
            response_mime_type="text/plain",
            safety_settings=[
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_MEDIUM_AND_ABOVE"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_MEDIUM_AND_ABOVE"),
            ]
        )

        # Initialize Chat Session
        self.chat_session = self.client.chats.create(model=self.model_id, config=self.config)

    def get_response(self, prompt):
        try:
            response = self.chat_session.send_message(prompt)
            return response.text
        except Exception as e:
            return f"Error connecting to Gemini: {str(e)}"

if __name__ == "__main__":
    assistant = AIAssistant()
    while True:
        time.sleep(1)