import speech_recognition as sr
import keyboard as kb
import google.generativeai as genai
import time

# Configure Gemini
# [REDACTED]
generation_config = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 5000,
}
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
    safety_settings=[]
)

# Speech-to-text function
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("🎤 Listening... (say something)")
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("⏱️ Listening timed out. Restarting...")
            return None
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        print("❌ Could not understand speech.")
    except sr.RequestError as e:
        print(f"🌐 Network error: {e}")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    return None

if_paused = False

# Main loop for continuous listening
while True:
    # Check for pause/resume commands first
    spoken_text = speech_to_text()
    if not spoken_text:
        continue

    # Handle pause/resume
    if spoken_text.lower() == "pause":
        print("⏸️ Pausing...")
        if_paused = True
        continue
    elif spoken_text.lower() == "resume":
        print("▶️ Resuming...")
        if_paused = False
        continue

    # If the system is paused, skip processing until resumed.
    if if_paused:
        continue

    print("🗣️ You said:", spoken_text)

    # If the speech starts with "analyse", handle via the LLM.
    if spoken_text.lower().startswith("reframe"):
        query = spoken_text[len("reframe"):].strip()
        prompt = (
            "You are an AI assistant that reframes the text I give you. "
            "If the user has been asked to press the Enter key, then at the end of your rephrased text, " 
            "Please remove that phrase and at the end of the rephrased sentence add the special token [ENTER] (Case Sensitive) " 
            "Don't add emojis until asked to do so." 
            "Otherwise, just provide the rephrased text.\n"
            f"Reframe this:\n\"{query}\""
        )
        try:
            response = model.generate_content([prompt])
            bot_response = response.text.strip()
            print("🤖 Gemini:", bot_response)
            # If the response ends with [ENTER], remove the token and simulate pressing Enter.
            if bot_response.endswith("[ENTER]"):
                bot_response = bot_response[:-len("[ENTER]")].rstrip()
                kb.write(bot_response)
                time.sleep(1)
                kb.press_and_release("enter")
            else:
                kb.write(bot_response)
        except Exception as e:
            print(f"❗ Gemini API error: {e}")
    else:
        print("⌨️ Typing raw input...")
        kb.write(spoken_text.strip())
